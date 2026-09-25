"""Real OCR run. Downloads models on first use, so it is opt-in:

PACKDATE_OCR_TESTS=1 pytest tests/test_ocr_rapid.py
"""

import os
from datetime import date

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("PACKDATE_OCR_TESTS") != "1", reason="set PACKDATE_OCR_TESTS=1"
)


def test_rapidocr_reads_a_rendered_expiry_line():
    pytest.importorskip("rapidocr")
    from PIL import Image, ImageDraw, ImageFont

    from packdate.pipeline import run
    from packdate.recognize.rapid import RapidOcrBackend

    img = Image.new("RGB", (700, 160), "white")
    ImageDraw.Draw(img).text((30, 50), "EXP 06/2027", font=ImageFont.load_default(48), fill="black")
    extraction = run(img, ocr=RapidOcrBackend(), read_codes=False)
    assert extraction.result.valid_through == date(2027, 6, 30), extraction.text
