from datetime import date

import pytest

from packdate.parse import expiry_from_gs1, parse_gs1
from packdate.parse.gs1 import gtin_check_digit_ok
from packdate.result import AbstainReason, Confidence, Precision, Source

GS = "\x1d"
GTIN_RU = "04601234567893"
GTIN_EU = "04150123456782"
CRYPTO_92 = "A" * 44


def test_ru_medicine_code_has_no_expiry():
    # МДЛП: FNC1 01 GTIN 21 serial(13) GS 91 key(4) GS 92 code(44)
    code = f"]d2{GS}01{GTIN_RU}21ABCDE12345678{GS}91EE06{GS}92{CRYPTO_92}"
    assert parse_gs1(code) == {
        "01": GTIN_RU,
        "21": "ABCDE12345678",
        "91": "EE06",
        "92": CRYPTO_92,
    }
    result = expiry_from_gs1(code)
    assert result.abstain_reason is AbstainReason.CODE_WITHOUT_DATE
    assert result.source is Source.DATAMATRIX
    assert result.extra == {"gtin": GTIN_RU, "serial": "ABCDE12345678"}


def test_ru_dairy_code_with_weight():
    code = f"01{GTIN_RU}21ABC123{GS}93dGVz{GS}3103000350"
    assert parse_gs1(code) == {"01": GTIN_RU, "21": "ABC123", "93": "dGVz", "3103": "000350"}


def test_eu_code_with_expiry():
    code = f"01{GTIN_EU}1727063010ABC123{GS}21XYZ987"
    result = expiry_from_gs1(code)
    assert result.valid_through == date(2027, 6, 30)
    assert result.precision is Precision.DAY
    assert result.confidence is Confidence.HIGH
    assert result.rule_id == "gs1_ai17"
    assert result.extra == {"gtin": GTIN_EU, "serial": "XYZ987", "batch": "ABC123"}


def test_zxing_escaped_and_hri_forms():
    escaped = f"01{GTIN_EU}1727063010ABC<GS>21XYZ"
    hri = f"(01){GTIN_EU}(17)270630(10)ABC(21)XYZ"
    expected = {"01": GTIN_EU, "17": "270630", "10": "ABC", "21": "XYZ"}
    assert parse_gs1(escaped) == expected
    assert parse_gs1(hri) == expected


def test_day_00_is_end_of_month_but_needs_check():
    result = expiry_from_gs1(f"01{GTIN_EU}17270200")
    assert result.valid_through == date(2027, 2, 28)
    assert result.precision is Precision.MONTH
    assert result.confidence is Confidence.CHECK


@pytest.mark.parametrize(
    "code",
    [
        "",
        "hello",
        f"01{GTIN_EU[:-1]}",  # truncated fixed-length AI
        f"01{GTIN_EU}17271332",  # month 13
        f"01{GTIN_EU}17270231",  # 31 February
        f"01{GTIN_EU[:-1]}0",  # wrong check digit
        f"01{GTIN_EU}21{GS}",  # empty value
    ],
)
def test_invalid_codes(code):
    assert expiry_from_gs1(code).abstain_reason is AbstainReason.INVALID_CODE


def test_gtin_check_digit():
    assert gtin_check_digit_ok(GTIN_EU)
    assert gtin_check_digit_ok(GTIN_RU)
    assert not gtin_check_digit_ok("04150123456783")
    assert not gtin_check_digit_ok("abc")
