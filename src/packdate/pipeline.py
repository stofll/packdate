"""extract(image) → Result: DataMatrix + full-frame OCR + parser.

v0.1 runs OCR on the whole frame as a measured baseline, not the target
design (ROADMAP decisions).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING

from packdate.barcode import DecodedCode
from packdate.parse import expiry_from_gs1, parse_text
from packdate.recognize import OcrBackend, TextLine, default_backend
from packdate.result import AbstainReason, Confidence, Result, Source

if TYPE_CHECKING:
    from PIL.Image import Image

Decoder = Callable[["Image"], list[DecodedCode]]


@dataclass(frozen=True)
class Extraction:
    """Everything the pipeline saw, for storage and debugging."""

    result: Result
    text: str  # OCR lines in reading order, as passed to the parser
    lines: tuple[TextLine, ...] = ()
    codes: tuple[DecodedCode, ...] = ()
    ocr_backend: str | None = None
    image_size: tuple[int, int] = (0, 0)
    code_results: tuple[Result, ...] = ()


_default_ocr: OcrBackend | None = None


def extract(image: str | Path | bytes | Image, **kwargs) -> Result:
    return run(image, **kwargs).result


def run(
    image: str | Path | bytes | Image,
    *,
    ocr: OcrBackend | None = None,
    use_ocr: bool = True,
    decoder: Decoder | None = None,
    read_codes: bool = True,
) -> Extraction:
    """Run the pipeline. `ocr` / `decoder` default to the installed backends."""
    img = load_image(image)

    codes: list[DecodedCode] = []
    if read_codes:
        if decoder is None:
            from packdate import barcode

            decoder = barcode.decode if barcode.available() else None
        if decoder is not None:
            codes = decoder(img)
    code_results = [expiry_from_gs1(c.text) for c in codes if c.gs1]

    lines: list[TextLine] = []
    backend_name = None
    if use_ocr:
        global _default_ocr
        if ocr is None:
            _default_ocr = _default_ocr or default_backend()
            ocr = _default_ocr
        lines = ocr(img)
        backend_name = ocr.name
    text, offsets = join_lines(lines)
    ocr_result = parse_text(text)
    if ocr_result.chosen:
        ocr_result = replace(ocr_result, bboxes=_boxes_for(ocr_result.chosen.span, offsets))

    return Extraction(
        result=merge(ocr_result, code_results),
        text=text,
        lines=tuple(lines),
        codes=tuple(codes),
        ocr_backend=backend_name,
        image_size=img.size,
        code_results=tuple(code_results),
    )


def load_image(image: str | Path | bytes | Image) -> Image:
    from io import BytesIO

    from PIL import Image as PILImage
    from PIL import ImageOps

    if isinstance(image, (str, Path)):
        img = PILImage.open(image)
    elif isinstance(image, bytes):
        img = PILImage.open(BytesIO(image))
    else:
        img = image
    # Phone photos carry their rotation in EXIF.
    return (ImageOps.exif_transpose(img) or img).convert("RGB")


def join_lines(lines: list[TextLine]) -> tuple[str, list[tuple[int, int, TextLine]]]:
    """Reading order: rows top to bottom, left to right inside a row.

    A line joins the current row when its vertical center is within half the
    row's first line height. Rows are joined with newlines, lines in a row
    with spaces, so "MFG EXP" stays on one row for column pairing.
    """
    rows: list[list[TextLine]] = []
    for line in sorted(lines, key=lambda ln: (ln.box[1] + ln.box[3]) / 2):
        center = (line.box[1] + line.box[3]) / 2
        if rows:
            first = rows[-1][0]
            first_center = (first.box[1] + first.box[3]) / 2
            if abs(center - first_center) <= (first.box[3] - first.box[1]) / 2:
                rows[-1].append(line)
                continue
        rows.append([line])

    parts: list[str] = []
    offsets: list[tuple[int, int, TextLine]] = []
    pos = 0
    for r, row in enumerate(rows):
        for i, line in enumerate(sorted(row, key=lambda ln: ln.box[0])):
            if i or r:
                sep = " " if i else "\n"
                parts.append(sep)
                pos += len(sep)
            parts.append(line.text)
            offsets.append((pos, pos + len(line.text), line))
            pos += len(line.text)
    return "".join(parts), offsets


def _boxes_for(span: tuple[int, int], offsets) -> tuple[tuple[float, float, float, float], ...]:
    """Boxes of the OCR lines covering a text span (spans may cross lines)."""
    return tuple(line.box for start, end, line in offsets if start < span[1] and span[0] < end)


def merge(ocr_result: Result, code_results: list[Result]) -> Result:
    """Combine OCR and DataMatrix readings.

    A code with AI (17) wins when OCR agrees or has no date; a disagreement
    is ambiguous. GTIN / serial from any code are kept in `extra`.
    """
    extra = dict(ocr_result.extra)
    for r in code_results:
        extra.update(r.extra)

    dated = [r for r in code_results if r.chosen]
    if not dated:
        return replace(ocr_result, extra=extra)

    code = dated[0]
    candidates = tuple(c for r in dated for c in r.candidates) + ocr_result.candidates
    if len({r.valid_through for r in dated}) > 1:
        return Result.abstain(AbstainReason.AMBIGUOUS, Source.DATAMATRIX, candidates, extra)
    if ocr_result.chosen is None:
        return replace(code, extra=extra, candidates=candidates)
    if ocr_result.valid_through == code.valid_through:
        return replace(
            code,
            confidence=Confidence.HIGH,
            extra=extra,
            candidates=candidates,
            bboxes=ocr_result.bboxes,
        )
    return Result.abstain(AbstainReason.AMBIGUOUS, Source.DATAMATRIX, candidates, extra)
