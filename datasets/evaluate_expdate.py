"""Reproducible, OCR-only diagnostic on Products-Real's evaluation split.

Reads the ZIP in place. Ground-truth crops are an oracle experiment, not a
detector benchmark. Labels come from upstream, not from packdate's parser.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
from datetime import date, datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import unicodedata
import zipfile

from packdate.parse import parse_text
from packdate.pipeline import join_lines, load_image, run
from packdate.recognize.rapid import LANGS, RapidOcrBackend

ANNOTATIONS = "Products-Real/evaluation/annotations.json"
IMAGE_ROOT = "Products-Real/evaluation/images/"
MONTHS = {m: i for i, m in enumerate(
    "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split(), 1
)}


def normalized(text: str) -> str:
    """Ignore case, separators and spaces; never fix OCR letters or digits."""
    return "".join(c for c in unicodedata.normalize("NFKC", text).upper() if c.isalnum())


def transcription_present(expected: str, actual: str) -> bool:
    target = normalized(expected)
    # Do not accept a date embedded in a longer digit sequence.
    return bool(target and re.search(r"(?<!\d)" + re.escape(target) + r"(?!\d)", normalized(actual)))


def expected_date(annotation: dict) -> tuple[str | None, str | None]:
    """Validate DMY labels independently; do not invent missing components.

    Two-digit upstream years explicitly mean 2000..2099 in this diagnostic.
    Month-only labels stay YYYY-MM; no medicine end-of-month rule is applied.
    """
    components = annotation.get("dmy_ann", [])
    fields = {c["cls"]: c["transcription"].strip().upper() for c in components}
    if len(fields) != len(components) or set(fields) - {"day", "month", "year"}:
        return None, "invalid_components"
    ordered = sorted(components, key=lambda c: c["bbox"][0])
    if normalized("".join(c["transcription"] for c in ordered)) != normalized(annotation["transcription"]):
        return None, "component_transcription_disagreement"
    if not {"year", "month"} <= fields.keys():
        return None, "missing_year_or_month"
    try:
        year_text = fields["year"]
        if len(year_text) not in (2, 4) or not year_text.isascii() or not year_text.isdigit():
            return None, "invalid_year"
        year = int(year_text) + (2000 if len(year_text) == 2 else 0)
        month_text = fields["month"]
        month = MONTHS[month_text] if month_text in MONTHS else int(month_text)
        value = date(year, month, int(fields.get("day", "1")))
    except (ValueError, TypeError):
        return None, "invalid_calendar_date"
    return (value.isoformat() if "day" in fields else value.strftime("%Y-%m")), None


def region_text(lines, box: list[int]) -> str:
    """Select OCR lines overlapping at least half of the smaller box area."""
    selected = []
    x1, y1, x2, y2 = box
    for line in lines:
        a, b, c, d = line.box
        intersection = max(0, min(x2, c) - max(x1, a)) * max(0, min(y2, d) - max(y1, b))
        smaller = min((x2-x1)*(y2-y1), (c-a)*(d-b))
        if smaller > 0 and intersection / smaller >= 0.5:
            selected.append(line)
    return join_lines(selected)[0]


def outcome(result: dict, expected: str | None) -> str:
    if expected is None:
        return "unscored_label"
    if result["iso_date"] is None:
        return "abstain"
    return "exact" if result["iso_date"] == expected else "false"


def summarize(rows: list[dict]) -> dict:
    successful = [r for r in rows if "error" not in r]
    scored = [r for r in successful if r["expected_iso"] is not None]
    counts = Counter(r["outcome"] for r in scored)
    committed = counts["exact"] + counts["false"]
    ratio = lambda a, b: round(a / b, 4) if b else None
    paired = [r for r in successful if r["crop_text"] is not None]
    return {
        "images": len(rows), "errors": len(rows) - len(successful),
        "ocr_scored": len(successful), "iso_scored": len(scored),
        "unscored_labels": dict(Counter(r["label_issue"] for r in successful if r["label_issue"])),
        "full_frame_transcription_present": sum(r["full_text_match"] for r in successful),
        "oracle_crop_scored": len(paired),
        "oracle_crop_transcription_present": sum(r["crop_text_match"] for r in paired),
        "crop_recovers_full_miss": sum(r["crop_text_match"] and not r["full_text_match"] for r in paired),
        "crop_loses_full_match": sum(r["full_text_match"] and not r["crop_text_match"] for r in paired),
        "pipeline_outcomes": dict(counts),
        "exact_printed_iso_rate": ratio(counts["exact"], len(scored)),
        "false_on_committed": ratio(counts["false"], committed),
        "abstain_rate": ratio(counts["abstain"], len(scored)),
        "candidate_contains_expected_iso": sum(r["candidate_match"] for r in scored),
        "nonexact_with_readable_transcription": sum(r["outcome"] != "exact" and r["full_text_match"] for r in scored),
        "abstain_reasons": dict(Counter(r["result"]["abstain_reason"] for r in scored if r["outcome"] == "abstain")),
    }


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def reparse_report(original: dict) -> dict:
    """Replay saved full-frame OCR through the current parser; no oracle cues."""
    if not original.get("complete") or original.get("schema_version") != 1:
        raise ValueError("reparse requires a complete schema_version=1 report")
    report = deepcopy(original)
    for row in report["rows"]:
        if "error" in row:
            continue
        result = parse_text(row["ocr_text"]).to_dict()
        row["result"] = result
        row["outcome"] = outcome(result, row["expected_iso"])
        row["candidate_match"] = row["expected_iso"] is not None and any(
            c["iso_date"] == row["expected_iso"] for c in result["candidates"]
        )
        row["parser_on_transcription"] = parse_text(row["annotation"]["transcription"]).to_dict()
    report["summary"] = summarize(report["rows"])
    report["evaluation_mode"] = "parser_replay_of_saved_full_frame_ocr"
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archive", type=Path, help="Products-Real ZIP, or a saved report with --reparse")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--lang", choices=LANGS, default="cyrillic")
    ap.add_argument("--limit", type=int, help="first N names in sorted order (smoke test only)")
    ap.add_argument("--oracle-crops", action="store_true")
    ap.add_argument("--crop-padding", type=int, default=8, help="pixels on each side; default 8")
    ap.add_argument("--reparse", action="store_true", help="score saved OCR with the current parser; no OCR inference")
    args = ap.parse_args(argv)
    if (args.limit is not None and args.limit < 1) or args.crop_padding < 0:
        ap.error("limit must be positive and crop-padding nonnegative")
    if args.archive.resolve() == args.out.resolve():
        ap.error("output must differ from input")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    if args.reparse:
        if args.limit or args.oracle_crops:
            ap.error("--reparse cannot be combined with --limit or --oracle-crops")
        report = reparse_report(json.loads(args.archive.read_text(encoding="utf-8")))
        report["reparse"] = {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "input_report_sha256": sha256(args.archive),
            "source_sha256": {str(p.relative_to(root)).replace("\\", "/"): sha256(p)
                              for p in sorted((root / "src/packdate").rglob("*.py"))},
            "evaluator_sha256": sha256(Path(__file__)),
        }
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report["summary"], indent=2))
        return 1 if report["summary"]["errors"] else 0
    rows = []
    started = time.perf_counter()
    ocr = RapidOcrBackend(args.lang)
    # Capture the resolved model configuration: the recognizer's name alone
    # does not identify RapidOCR's default detector/classifier.
    from omegaconf import OmegaConf
    config = OmegaConf.to_container(ocr._engine.cfg, resolve=True)
    models = {}
    for stage, attr in (("Det", "text_det"), ("Cls", "text_cls"), ("Rec", "text_rec")):
        session = getattr(ocr._engine, attr).session.session
        model = Path(session._model_path)
        models[stage] = {"file": model.name, "sha256": sha256(model), "providers": session.get_providers()}
    tracked = subprocess.check_output(["git", "ls-files", "src", "datasets/evaluate_expdate.py"], cwd=root, text=True).splitlines()
    tracked.append("datasets/evaluate_expdate.py")
    report = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": "https://felizang.github.io/expdate/index_expdate.html",
        "attribution": "ExpDate, Ahmet Cagatay Seker and Sang Chul Ahn, KIST; CC BY 4.0",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "archive_sha256": sha256(args.archive), "split": "evaluation",
        "backend": ocr.name, "models": models, "config": config,
        "versions": {p: version(p) for p in ("rapidocr", "onnxruntime", "pillow", "packdate")},
        "python": sys.version, "platform": platform.platform(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "source_sha256": {p: sha256(root / p) for p in sorted(set(tracked))},
        "options": {"lang": args.lang, "limit": args.limit, "oracle_crops": args.oracle_crops, "crop_padding": args.crop_padding},
        "protocol": {
            "ocr": "NFKC uppercase alphanumeric transcription present in spatially matched OCR lines; digit boundaries; no O/0 correction",
            "spatial_match": "intersection / smaller box area >= 0.5",
            "iso": "printed ISO including precision, from consistent calendar-valid upstream DMY labels; YY means 20YY",
            "scope": "mixed-domain diagnostic; no negatives; no valid_through or medicine benchmark claim; barcode disabled",
            "crop": "ground-truth bbox with padding, same OCR detector+recognizer; no cue injection into pipeline",
        },
        "rows": rows,
    }

    def save(complete: bool) -> None:
        report.update(complete=complete, elapsed_seconds=round(time.perf_counter() - started, 3), summary=summarize(rows))
        temporary = args.out.with_suffix(args.out.suffix + ".tmp")
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
        temporary.replace(args.out)

    with zipfile.ZipFile(args.archive) as archive:
        raw = archive.read(ANNOTATIONS)
        report["annotations_sha256"] = hashlib.sha256(raw).hexdigest()
        annotations = json.loads(raw)
        names = sorted(annotations)
        if args.limit:
            names = names[:args.limit]
        report["selected_files"] = names
        for index, name in enumerate(names, 1):
            try:
                record = annotations[name]
                expiry = [a for a in record["ann"] if a["cls"] == "exp"]
                if len(expiry) != 1:
                    raise ValueError("expected exactly one exp region")
                annotation = expiry[0]
                expected, issue = expected_date(annotation)
                image_bytes = archive.read(IMAGE_ROOT + name)
                img = load_image(image_bytes)
                if img.size != (record["width"], record["height"]):
                    raise ValueError("image dimensions disagree with annotation")
                box = annotation["bbox"]
                x1, y1, x2, y2 = box
                if not (0 <= x1 < x2 <= img.width and 0 <= y1 < y2 <= img.height):
                    raise ValueError("invalid expiry bbox")
                tick = time.perf_counter()
                extraction = run(img, ocr=ocr, read_codes=False)
                full_seconds = time.perf_counter() - tick
                local_text = region_text(extraction.lines, box)
                crop_text = None
                crop_seconds = None
                if args.oracle_crops:
                    pad = args.crop_padding
                    crop = img.crop((max(0, x1-pad), max(0, y1-pad), min(img.width, x2+pad), min(img.height, y2+pad)))
                    tick = time.perf_counter()
                    crop_text = join_lines(ocr(crop))[0]
                    crop_seconds = time.perf_counter() - tick
                result = extraction.result.to_dict()
                rows.append({
                    "file": name, "image_sha256": hashlib.sha256(image_bytes).hexdigest(),
                    "annotation": annotation, "expected_iso": expected, "label_issue": issue,
                    "ocr_text": extraction.text, "ocr_lines": [asdict(line) for line in extraction.lines],
                    "region_text": local_text, "crop_text": crop_text,
                    "full_text_match": transcription_present(annotation["transcription"], local_text),
                    "crop_text_match": transcription_present(annotation["transcription"], crop_text) if crop_text is not None else None,
                    "result": result, "outcome": outcome(result, expected),
                    "candidate_match": expected is not None and any(c["iso_date"] == expected for c in result["candidates"]),
                    "full_seconds": round(full_seconds, 4),
                    "crop_seconds": round(crop_seconds, 4) if crop_seconds is not None else None,
                    "parser_on_transcription": parse_text(annotation["transcription"]).to_dict(),
                })
            except Exception as exc:
                rows.append({"file": name, "error": f"{type(exc).__name__}: {exc}"})
            if index % 25 == 0 or index == len(names):
                save(False)
                print(f"{index}/{len(names)} {json.dumps(report['summary'])}", flush=True)
    save(True)
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
