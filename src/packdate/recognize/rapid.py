"""RapidOCR backend (ONNX Runtime) with a Cyrillic recognition model.

PP-OCRv6 has no Cyrillic model, so recognition uses PP-OCRv5 mobile
(`cyrillic` or `eslav`); see docs/research/11-models-refresh.md. RapidOCR
downloads the models on first use.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from packdate.recognize import TextLine

if TYPE_CHECKING:
    from PIL.Image import Image

LANGS = ("cyrillic", "eslav")


class RapidOcrBackend:
    def __init__(self, lang: str = "cyrillic") -> None:
        if lang not in LANGS:
            raise ValueError(f"lang must be one of {LANGS}, got {lang!r}")
        try:
            from rapidocr import LangRec, ModelType, OCRVersion, RapidOCR
        except ImportError as e:
            raise ImportError("OCR needs the extra: pip install 'packdate[ocr]'") from e

        self.name = f"rapidocr/{lang}_PP-OCRv5_mobile"
        self._engine = RapidOCR(
            params={
                "Rec.lang_type": LangRec(lang),
                "Rec.model_type": ModelType.MOBILE,
                "Rec.ocr_version": OCRVersion.PPOCRV5,
                "Global.log_level": "warning",
            }
        )

    def __call__(self, image: Image) -> list[TextLine]:
        out = self._engine(image)
        if out.boxes is None or out.txts is None:
            return []
        lines = []
        for points, text, score in zip(out.boxes, out.txts, out.scores):
            xs = [float(p[0]) for p in points]
            ys = [float(p[1]) for p in points]
            lines.append(TextLine(text, float(score), (min(xs), min(ys), max(xs), max(ys))))
        return lines
