"""Write draft labels for a folder of photos by running extract().

For each photo without a label, writes `<name>.draft.json`:

    {"valid_through": "2027-06-30" | null, "stratum": "unknown",
     "notes": "draft by packdate ...", "ocr_text": "...", "candidates": [...]}

A person reviews each draft, fixes `valid_through` / `stratum`, drops the
helper fields and renames it to `<name>.json` (the evaluate.py label format).
Drafts are never labels: scoring a model on its own drafts measures nothing.

    python datasets/prelabel.py D:/packdate-data/commons-ru-drugs/images
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from packdate.pipeline import run
from packdate.recognize.rapid import RapidOcrBackend

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def main(folder: Path) -> int:
    ocr = RapidOcrBackend()
    stats: Counter[str] = Counter()
    for photo in sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES):
        if photo.with_suffix(".json").exists():
            stats["already_labeled"] += 1
            continue
        extraction = run(photo, ocr=ocr)
        result = extraction.result.to_dict()
        draft = {
            "valid_through": result["valid_through"],
            "stratum": "unknown",
            "notes": f"draft by packdate {ocr.name}: {result['confidence']}"
            + (f", abstain {result['abstain_reason']}" if result["abstain_reason"] else ""),
            "ocr_text": extraction.text,
            "candidates": [c["iso_date"] + " " + c["kind"] for c in result["candidates"]],
            "codes": [c.text for c in extraction.codes],
        }
        photo.with_suffix(".draft.json").write_text(
            json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        stats[
            result["confidence"]
            + (f"/{result['abstain_reason']}" if result["abstain_reason"] else "")
        ] += 1
        print(f"{result['confidence']:<6} {result['valid_through'] or '-':<11} {photo.name}")
    print(dict(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
