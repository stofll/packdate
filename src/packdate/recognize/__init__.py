"""Recognize: OCR backends behind optional extras."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from PIL.Image import Image


@dataclass(frozen=True)
class TextLine:
    text: str
    score: float
    box: tuple[float, float, float, float]  # x0, y0, x1, y1 in image pixels


class OcrBackend(Protocol):
    name: str

    def __call__(self, image: Image) -> list[TextLine]: ...


def default_backend() -> OcrBackend:
    from packdate.recognize.rapid import RapidOcrBackend

    return RapidOcrBackend()


__all__ = ["OcrBackend", "TextLine", "default_backend"]
