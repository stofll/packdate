# Architecture

## Goals

1. Permissive OSS (Apache-2.0) compatible with PaddleOCR and optional Open Food Facts usage.
2. Clear module boundaries: **detect → recognize → parse**; barcode separate.
3. Fail-safe: prefer abstain + confirm over a wrong ISO date.
4. Honest evaluation: stratified phone photos (medicines first: box print, embossed blister, tube seam, foil blister, multi-date, negatives).

First domain is **medicines** (EAEU packs); food follows. Rationale in [ROADMAP](../ROADMAP.md#decisions-behind-this-plan) and [research/10](research/10-medicine-vs-food.md).

## Packages (target layout)

| Path | Role |
|------|------|
| `src/packdate/detect/` | Date ROI (e.g. RF-DETR N–L / ONNX). Optional; only if the bench shows OCR is ROI-bound. |
| `src/packdate/recognize/` | OCR backends behind optional extras (RapidOCR / PaddleOCR with the Cyrillic PP-OCRv5 rec model first; EasyOCR, TrOCR optional). |
| `src/packdate/barcode/` | DataMatrix / EAN / UPC decode behind `packdate[barcode]` (zxing-cpp). Returns decoded text only. |
| `src/packdate/parse/` | Formats, RU/EN cue lexicon, MFG vs EXP policy, calendar validation, date rules, GS1 element-string parsing. Stdlib only. |
| `src/packdate/pipeline.py` | `extract(image) → Result`; `run(image) → Extraction` (result + OCR lines, text, codes, backend name) for storage and debugging |
| `apps/demo/` | Thin CLI + local web site (upload → confirm → list). Not the library core; own dependencies. |
| `datasets/` | Scripts + license notes; sample fixtures under `tests/fixtures/` |

### Barcode vs expiry

- **EAN / UPC** → product identity only (Open Food Facts, local cache). Never an expiry.
- **GS1 DataMatrix with AI (17)** (EU FMD, US DSCSA drug packs) → a per-pack expiry source; parsed in `parse/` like any other text, `source=datamatrix`.
- **Russian marking codes** (МДЛП, «Честный ЗНАК») → GTIN + serial only; useful for identity and duplicate detection, no expiry in the code.

## Result contract

`extract()` and the parser return the same shape. One ISO day is not enough: a month-precision date means different last days under different rules (see [research/12](research/12-post-recognition.md#1-date-semantics-edge-cases-for-the-parser)).

| Field | Meaning |
|-------|---------|
| `iso_date` | Date as printed, normalized (`2027-06` for month precision) |
| `precision` | `day` / `month` (later `hour` / `year` for food) |
| `valid_through` | Last good day after applying `rule_id` |
| `rule_id` | Rule used to get `valid_through`, e.g. `eaeu76_end_of_month`, `gs1_ai17` |
| `kind` | `expiry` / `mfg` / `unknown` (EU `use_by` / `best_before` only from EU cues; RU «употребить до» is a synonym of «годен до») |
| `confidence` | `high` / `check` / `none` — categories, not raw scores |
| `candidates` | Other readings, for N-best chips in the UI |
| `abstain_reason` | Why no date was committed (`no_cue`, `cue_without_date`, `ambiguous`, `mfg_only`, …) |
| `source` | `ocr` / `datamatrix` |
| `bboxes` | Where the date and cue were found |

## Demo app storage

The web demo keeps the immutable pipeline output (`extraction`: photo path, raw OCR text, backend + parser versions, result) separate from the human decision (`confirmation`: accept / pick candidate / edit / reject, final value). Corrections can then be exported as fixtures. Photos stay local. Full model: [research/12](research/12-post-recognition.md#proposed-minimal-data-model).

## Dependency policy

**Prefer:** Apache-2.0 / MIT / BSD runtime deps. The base install has no runtime dependencies; OCR, detector and barcode backends are optional extras.

**Avoid as hard dependencies:** Ultralytics YOLO (AGPL-3.0), RF-DETR XL/2XL (PML 1.0 — the N/S/M/L sizes are Apache-2.0), OpenRAIL-restricted OCR weights (e.g. some Surya builds), NC licenses (Nougat), mixing proprietary barcode API dumps into a public OFF-derived DB.

**Open Food Facts:** ODbL share-alike on *database* derivatives; user inventory / per-pack expiry stays in *your* tables, not in OFF. Document attribution in NOTICE/README when OFF is wired in.

## Benchmark gate (hypothesis “model X already solves it”)

Run in roadmap milestone 4 on ~40–60 own photos, stratified (box print, embossed blister, tube seam, foil blister, multi-date, negatives):

- Exact ISO ≥ 90% on non-null
- False ISO ≤ 5%
- Embossed Exact ≥ 70%

Otherwise the gap remains — and parse/dataset/HITL stay the product.

## v0 → v1

1. **v0.0.x** — `parse/`: medicine cues and formats, date rules, GS1 element strings, calendar validation, abstain; string-level tests
2. **v0.1** — full-frame OCR baseline + DataMatrix decode (optional extras) + `extract()` + CLI + ~30 golden fixtures
3. **Web demo** — local upload → confirm → list; exports corrections as fixtures
4. **Bench gate** — 40–60 stratified photos decide the next step
5. **v0.2** — ROI detector + CIJ preprocess, *only if* the bench shows OCR misses are ROI-bound
6. **Food** — ТР ТС 022 grammar + EAN/UPC + OFF identity
7. **Later** — reminders, mobile client, cosmetics

Apps under `apps/` must not block the library API.

## Research archive

See [research/README.md](research/README.md).

## Roadmap

Staged milestones: [ROADMAP.md](../ROADMAP.md).
