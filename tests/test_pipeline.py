from datetime import date

import pytest

from packdate.barcode import DecodedCode
from packdate.parse import expiry_from_gs1, parse_text
from packdate.pipeline import join_lines, merge
from packdate.recognize import TextLine
from packdate.result import AbstainReason, Confidence, Source

GS = "\x1d"
EU_CODE = "0104150123456782" + "17270630"
RU_CODE = f"010460123456789321ABCDE12345678{GS}91EE06{GS}92" + "A" * 44


def line(text, x0, y0, x1, y1):
    return TextLine(text, 0.99, (x0, y0, x1, y1))


def test_reading_order_rows_then_columns():
    lines = [
        line("01.2028", 200, 62, 300, 98),
        line("EXP", 200, 10, 260, 40),
        line("01.2025", 20, 60, 120, 100),
        line("MFG", 20, 12, 80, 42),
    ]
    text, offsets = join_lines(lines)
    assert text == "MFG EXP\n01.2025 01.2028"
    assert [o[2].text for o in offsets] == ["MFG", "EXP", "01.2025", "01.2028"]


def test_join_empty():
    assert join_lines([]) == ("", [])


def test_merge_code_and_ocr_agree():
    ocr = parse_text("Годен до 30.06.2027")
    result = merge(ocr, [expiry_from_gs1(EU_CODE)])
    assert result.source is Source.DATAMATRIX
    assert result.confidence is Confidence.HIGH
    assert result.valid_through == date(2027, 6, 30)
    assert result.extra["gtin"] == "04150123456782"


def test_merge_code_and_ocr_disagree():
    ocr = parse_text("Годен до 07.2027")
    result = merge(ocr, [expiry_from_gs1(EU_CODE)])
    assert result.abstain_reason is AbstainReason.AMBIGUOUS
    assert {c.valid_through for c in result.candidates} == {date(2027, 6, 30), date(2027, 7, 31)}


def test_merge_code_without_date_keeps_ocr_and_identity():
    ocr = parse_text("Годен до 06.2027")
    result = merge(ocr, [expiry_from_gs1(RU_CODE)])
    assert result.source is Source.OCR
    assert result.valid_through == date(2027, 6, 30)
    assert result.extra == {"gtin": "04601234567893", "serial": "ABCDE12345678"}


def test_merge_code_date_when_ocr_abstains():
    result = merge(parse_text(""), [expiry_from_gs1(EU_CODE)])
    assert result.valid_through == date(2027, 6, 30)
    assert result.source is Source.DATAMATRIX


class FakeOcr:
    name = "fake"

    def __init__(self, lines):
        self.lines = lines

    def __call__(self, image):
        return self.lines


def test_run_with_fake_ocr_sets_boxes():
    Image = pytest.importorskip("PIL.Image")
    from packdate.pipeline import run

    lines = [line("Серия 010624", 10, 10, 200, 40), line("Годен до: 06.2027", 10, 60, 260, 90)]
    extraction = run(Image.new("RGB", (300, 120), "white"), ocr=FakeOcr(lines), read_codes=False)
    assert extraction.result.valid_through == date(2027, 6, 30)
    assert extraction.result.bboxes == ((10, 60, 260, 90),)
    assert extraction.text == "Серия 010624\nГоден до: 06.2027"
    assert extraction.ocr_backend == "fake"


def test_run_with_fake_decoder():
    Image = pytest.importorskip("PIL.Image")
    from packdate.pipeline import run

    code = DecodedCode(EU_CODE, "DataMatrix", gs1=True, box=(0, 0, 10, 10))
    extraction = run(
        Image.new("RGB", (50, 50), "white"),
        ocr=FakeOcr([]),
        decoder=lambda img: [code],
    )
    assert extraction.result.valid_through == date(2027, 6, 30)
    assert extraction.result.source is Source.DATAMATRIX


def test_decode_real_gs1_datamatrix():
    zxingcpp = pytest.importorskip("zxingcpp")
    Image = pytest.importorskip("PIL.Image")
    from packdate import barcode

    bc = zxingcpp.create_barcode(
        "(01)04150123456782(17)270630(10)ABC(21)XYZ", zxingcpp.BarcodeFormat.DataMatrix, gs1=True
    )
    raw = memoryview(bc.to_image(scale=6))
    symbol = Image.frombytes("L", (raw.shape[1], raw.shape[0]), raw.tobytes())
    canvas = Image.new("L", (symbol.width + 80, symbol.height + 80), 255)
    canvas.paste(symbol, (40, 40))

    codes = barcode.decode(canvas.convert("RGB"))
    assert len(codes) == 1 and codes[0].gs1
    result = expiry_from_gs1(codes[0].text)
    assert result.valid_through == date(2027, 6, 30)
    assert result.extra == {"gtin": "04150123456782", "serial": "XYZ", "batch": "ABC"}
