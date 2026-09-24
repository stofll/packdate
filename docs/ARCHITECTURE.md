# Architecture

## Goals

1. Permissive OSS (Apache-2.0) compatible with PaddleOCR and optional Open Food Facts usage.
2. Clear module boundaries: **detect → recognize → parse**; barcode separate.
3. Fail-safe: prefer abstain + confirm over a wrong ISO date.
4. Honest evaluation: stratified phone photos (inkjet, thermal, embossed, curved, multi-date, negatives).

## Packages (target layout)

| Path | Role |
|------|------|
| `src/packdate/detect/` | Date ROI (e.g. RF-DETR N–L / ONNX). Optional; only if the bench shows OCR is ROI-bound. |
| `src/packdate/recognize/` | OCR backends behind optional extras (PP-OCRv5/v6 first; RapidOCR, EasyOCR, TrOCR optional). |
| `src/packdate/parse/` | Formats, RU/EN cue lexicon, MFG vs EXP policy, calendar validation. Stdlib only. |
| `src/packdate/pipeline.py` | `extract(image) → Result` |
| `apps/demo/` | Thin CLI / Streamlit — not the library core |
| `datasets/` | Scripts + license notes; sample fixtures under `tests/fixtures/` |

## Dependency policy

**Prefer:** Apache-2.0 / MIT / BSD runtime deps. The base install has no runtime dependencies; OCR, detector and barcode backends are optional extras.

**Avoid as hard dependencies:** Ultralytics YOLO (AGPL-3.0), RF-DETR XL/2XL (PML 1.0 — the N/S/M/L sizes are Apache-2.0), OpenRAIL-restricted OCR weights (e.g. some Surya builds), NC licenses (Nougat), mixing proprietary barcode API dumps into a public OFF-derived DB.

**Open Food Facts:** ODbL share-alike on *database* derivatives; user inventory / per-pack expiry stays in *your* tables, not in OFF. Document attribution in NOTICE/README when OFF is wired in.

## Benchmark gate (hypothesis “model X already solves it”)

Run in roadmap milestone 3 on ~40–60 own photos, stratified (inkjet, thermal, embossed, curved, multi-date, negatives):

- Exact ISO ≥ 90% on non-null
- False ISO ≤ 5%
- Embossed Exact ≥ 70%

Otherwise the gap remains — and parse/dataset/HITL stay the product.

## v0 → v1

1. **v0.0.x** — `parse/`: RU/EN cues, format grammar, calendar validation, abstain; string-level tests  
2. **v0.1** — full-frame OCR baseline (optional extra) + `extract()` + CLI + ~30 golden fixtures  
3. **Bench gate** — 40–60 stratified photos decide the next step  
4. **v0.2** — ROI detector + CIJ preprocess, *only if* the bench shows OCR misses are ROI-bound  
5. **Barcode + OFF** — sibling module, identity only  
6. **Later** — mobile / pantry thin client under `apps/`

App “pantry tracker” can live under `apps/` later; it must not block the library API.

## Research archive

See [research/README.md](research/README.md).

## Roadmap

Staged milestones: [ROADMAP.md](../ROADMAP.md).

