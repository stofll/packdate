"""Read expiry dates from photos and print one JSON object per image.

python apps/demo/cli.py photo.jpg [more.jpg ...] [--lang eslav] [--no-codes] [--text]
"""

from __future__ import annotations

import argparse
import json
import sys

from packdate.pipeline import run
from packdate.recognize.rapid import LANGS, RapidOcrBackend


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("images", nargs="+")
    ap.add_argument("--lang", choices=LANGS, default="cyrillic", help="OCR recognition model")
    ap.add_argument("--no-codes", action="store_true", help="skip DataMatrix decoding")
    ap.add_argument("--text", action="store_true", help="include OCR text and codes")
    args = ap.parse_args(argv)

    ocr = RapidOcrBackend(args.lang)
    for path in args.images:
        extraction = run(path, ocr=ocr, read_codes=not args.no_codes)
        out = {"file": path, **extraction.result.to_dict()}
        if args.text:
            out["ocr_text"] = extraction.text
            out["codes"] = [c.text for c in extraction.codes]
        print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
