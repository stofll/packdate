"""Score extract() on a folder of labeled photos.

Each photo `name.jpg` needs a sidecar `name.json`:

    {"valid_through": "2027-06-30", "stratum": "box_print"}

`valid_through` is null for photos with no readable expiry (negatives). Photos
stay outside the repo unless anonymized (AGENTS.md rule 8).

    python apps/demo/evaluate.py path/to/photos [--lang eslav] [--out report.json]

Metrics (ROADMAP milestone 2):
- exact: committed and equal to the label
- false: committed but wrong, or committed on a negative
- abstain: no committed date
Misses on labeled photos are split into "ocr" (no candidate had the right date)
and "parser" (a candidate had it, but it was not committed).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from packdate.pipeline import run
from packdate.recognize.rapid import LANGS, RapidOcrBackend

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}  # HEIC: convert first


def score(result: dict, expected: str | None) -> str:
    got = result["valid_through"]
    if got is None:
        if expected is None:
            return "abstain_ok"
        seen = any(c["valid_through"] == expected for c in result["candidates"])
        return "miss_parser" if seen else "miss_ocr"
    return "exact" if got == expected else "false"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Score extract() on labeled photos")
    ap.add_argument("folder", type=Path)
    ap.add_argument("--lang", choices=LANGS, default="cyrillic")
    ap.add_argument("--out", type=Path, help="write the full report as JSON")
    args = ap.parse_args(argv)

    photos = sorted(p for p in args.folder.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    labeled = [(p, p.with_suffix(".json")) for p in photos if p.with_suffix(".json").exists()]
    if not labeled:
        print(f"no labeled photos in {args.folder}", file=sys.stderr)
        return 1

    ocr = RapidOcrBackend(args.lang)
    rows = []
    for photo, label_path in labeled:
        label = json.loads(label_path.read_text(encoding="utf-8"))
        extraction = run(photo, ocr=ocr)
        result = extraction.result.to_dict()
        rows.append(
            {
                "file": photo.name,
                "stratum": label.get("stratum", "unknown"),
                "expected": label.get("valid_through"),
                "outcome": score(result, label.get("valid_through")),
                "confidence": result["confidence"],
                "result": result,
                "ocr_text": extraction.text,
            }
        )

    summary = _summary(rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.out:
        report = {
            "date": date.today().isoformat(),
            "backend": ocr.name,
            "folder": str(args.folder),
            "summary": summary,
            "rows": rows,
        }
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def _summary(rows: list[dict]) -> dict:
    def block(subset: list[dict]) -> dict:
        n = len(subset)
        with_date = [r for r in subset if r["expected"] is not None]
        committed = [r for r in subset if r["result"]["valid_through"] is not None]
        outcomes = Counter(r["outcome"] for r in subset)
        return {
            "n": n,
            "with_date": len(with_date),
            "exact_on_with_date": _ratio(outcomes["exact"], len(with_date)),
            "false_on_committed": _ratio(outcomes["false"], len(committed)),
            "abstain_rate": _ratio(n - len(committed), n),
            "outcomes": dict(outcomes),
            "by_confidence": dict(Counter((r["confidence"], r["outcome"]) for r in subset)),
        }

    by_stratum = defaultdict(list)
    for r in rows:
        by_stratum[r["stratum"]].append(r)
    total = block(rows)
    total["by_confidence"] = {f"{c}/{o}": k for (c, o), k in total["by_confidence"].items()}
    strata = {}
    for name, subset in sorted(by_stratum.items()):
        b = block(subset)
        b.pop("by_confidence")
        strata[name] = b
    return {"total": total, "by_stratum": strata}


def _ratio(a: int, b: int) -> float | None:
    return round(a / b, 3) if b else None


if __name__ == "__main__":
    sys.exit(main())
