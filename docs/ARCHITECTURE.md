# Architecture

## Goals

1. Permissive OSS (Apache-2.0) compatible with PaddleOCR and optional Open Food Facts usage.
2. Clear module boundaries: **detect → recognize → parse**; barcode separate.
3. Fail-safe: prefer abstain + confirm over a wrong ISO date.
4. Honest evaluation: stratified phone photos (inkjet, thermal, embossed, curved, multi-date, negatives).

## Packages (target layout)

| Path | Role |
|------|------|
| `src/packdate/detect/` | Date ROI (e.g. RF-DETR / ONNX). Optional in v0. |
| `src/packdate/recognize/` | OCR backends (PP-OCR first; EasyOCR/TrOCR optional). |
| `src/packdate/parse/` | Formats, RU/EN cue lexicon, MFG vs EXP policy, calendar validation. |
| `src/packdate/pipeline.py` | `extract(image) → Result` |
| `apps/demo/` | Thin CLI / Streamlit — not the library core |
| `datasets/` | Scripts + license notes; sample fixtures under `tests/fixtures/` |

## Dependency policy

**Prefer:** Apache-2.0 / MIT / BSD runtime deps.

**Avoid as hard dependencies:** Ultralytics YOLO (AGPL-3.0), OpenRAIL-restricted OCR weights (e.g. some Surya builds), NC licenses (Nougat), mixing proprietary barcode API dumps into a public OFF-derived DB.

**Open Food Facts:** ODbL share-alike on *database* derivatives; user inventory / per-pack expiry stays in *your* tables, not in OFF. Document attribution in NOTICE/README when OFF is wired in.

## Benchmark gate (hypothesis “model X already solves it”)

On ~40–60 own photos, stratified:

- Exact ISO ≥ 90% on non-null
- False ISO ≤ 5%
- Embossed Exact ≥ 70%

Otherwise the gap remains — and parse/dataset/HITL stay the product.

## v0 → v1

1. **v0.1** — full-frame PP-OCR + RU/EN parse + abstain + CLI + ~30 golden fixtures  
2. **v0.2** — ROI detector + better CIJ preprocess  
3. **v0.3** — optional mobile thin client; barcode+OFF as sibling module  

App “pantry tracker” can live under `apps/` later; it must not block the library API.

## Research archive

See [research/README.md](research/README.md).
