"""Barcode: decode DataMatrix codes (zxing-cpp, optional extra).

Returns decoded text only; what it means is decided in `packdate.parse.gs1`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL.Image import Image


@dataclass(frozen=True)
class DecodedCode:
    text: str  # raw, GS as ASCII 29
    format: str
    gs1: bool  # FNC1 in first position (symbology identifier "]d2")
    box: tuple[float, float, float, float]


def available() -> bool:
    try:
        import zxingcpp  # noqa: F401
    except ImportError:
        return False
    return True


def decode(image: Image) -> list[DecodedCode]:
    try:
        import zxingcpp
    except ImportError as e:
        raise ImportError(
            "Barcode decoding needs the extra: pip install 'packdate[barcode]'"
        ) from e

    codes = []
    for bc in zxingcpp.read_barcodes(
        image, formats=zxingcpp.BarcodeFormat.DataMatrix, text_mode=zxingcpp.TextMode.Plain
    ):
        pos = bc.position
        xs = [p.x for p in (pos.top_left, pos.top_right, pos.bottom_right, pos.bottom_left)]
        ys = [p.y for p in (pos.top_left, pos.top_right, pos.bottom_right, pos.bottom_left)]
        codes.append(
            DecodedCode(
                text=bc.text,
                format=bc.format.name,
                gs1=bc.symbology_identifier == "]d2",
                box=(min(xs), min(ys), max(xs), max(ys)),
            )
        )
    return codes
