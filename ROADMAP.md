# Roadmap

Near-term plan for **packdate**. Dates are rough; order matters more than calendar.

## Decisions behind this plan

- **Library first, app later.** The research archive (`02-full-report.md`, `07-reference-projects.md`) sketches an app-first path (barcode + manual date, OCR later). This repo deliberately starts with the library core instead; a pantry app is a consumer of the library, not a prerequisite.
- **Parse first.** The parser is the part no upstream project provides and it can be tested on plain strings, so it lands before any OCR.
- **Full-frame OCR in v0.1 is a measured baseline, not the target design.** The research lists "full-image OCR without ROI" as an anti-pattern; v0.1 uses it only to get numbers. The bench in milestone 3 decides whether the ROI detector is needed.
- **Light core.** `packdate` installs with no runtime dependencies; OCR, detector and barcode backends come as optional extras.

## Done

- [x] Public Apache-2.0 repo skeleton (`stofll/packdate`)
- [x] Research archive under `docs/research/` (OCR verdict, barcode/OFF, deps shortlist)
- [x] Module layout: `detect` / `recognize` / `parse` (stubs)
- [x] Architecture + licensing notes

## Next

### 0 — Repo hygiene *(this milestone)*

- [x] `ROADMAP.md` + clearer README status
- [x] SPDX license metadata in `pyproject.toml` (setuptools ≥ 77), pytest config
- [ ] GitHub description, topics, homepage (set in the GitHub UI)
- [ ] CI: GitHub Actions running `pytest` on Python 3.11–3.13 (together with the first tests in milestone 1)

### 1 — Date parser (library core)

- [ ] RU/EN cue lexicon (EXP / BB / USE BY / MFG / «годен до» / «употребить до» / «изготовлено» / …)
- [ ] Format grammar: `DD.MM.YYYY`, `DD.MM.YY`, `DD/MM/YY`, `YYYY-MM-DD`, no-separator `DDMMYY` / `YYMMDD`, month names (`JUL25`, `12 ИЮЛ 2026`); ExpDate's 13 formats as a checklist
- [ ] OCR-noise normalization (`O→0`, `l/I→1`, stray spaces inside numbers)
- [ ] Calendar validation (reject `32.13.2025`) and locale policy: RU → DMY; ambiguous `MM/DD` vs `DD/MM` with no locale → candidates, not a guess
- [ ] Result types: `iso_date`, `kind` (`use_by` / `best_before` / `mfg` / `unknown`), `confidence`, `candidates`
- [ ] Disambiguation policy documented (cue beats position; "latest date" only under an EXP cue; MFG + shelf-life "годен N суток" → abstain or derive, decide explicitly)
- [ ] Abstain policy (prefer no ISO over a wrong one)
- [ ] Unit tests on strings + format table under `tests/` (no photos required); stdlib only

**Done when:** OCR text (or fixture strings) → stable ISO or honest abstain; MFG ≠ EXP on golden cases.

### 2 — `extract()` v0.1 (full-frame OCR)

- [ ] Default backend behind an optional extra (`packdate[ocr]`): compare PP-OCRv5 + `cyrillic_PP-OCRv5_mobile_rec` against PP-OCRv6 (PaddleOCR 3.7.0, June 2026) on the fixtures; check that v6 covers Cyrillic before switching
- [ ] Consider RapidOCR (ONNX runtime of PP-OCR models) as a lighter install
- [ ] `pipeline.extract(...) → Result`
- [ ] Thin CLI under `apps/demo/`
- [ ] ~30 golden photo fixtures + expected JSON
- [ ] Fixture metrics: Exact ISO, false ISO, abstain rate

**Done when:** install → run CLI on a few photos → readable JSON + clear “confirm me” cases.

### 3 — Honest bench gate

- [ ] 40–60 own photos, stratified: inkjet / thermal / embossed / curved / multi-date / negative
- [ ] Report against the [architecture thresholds](docs/ARCHITECTURE.md#benchmark-gate-hypothesis-model-x-already-solves-it) (hypothesis, not marketing)
- [ ] Split failures into "OCR missed the date" vs "parser got it wrong", so the next step is picked by data: ROI + preprocess (milestone 4) or more parser work
- [ ] One small VLM as a comparison run only (PaddleOCR-VL-1.6 0.9B, Qwen3-VL-2B, or Qwen2.5-VL-7B — all Apache-2.0)
- [ ] Document remaining gaps in README if gates miss

### 4 — ROI detector v0.2 *(only if milestone 3 shows OCR is ROI-bound)*

- [ ] `detect/` with a permissive ONNX path (no Ultralytics as hard dep); RF-DETR N/S/M/L only — XL/2XL are PML 1.0, not Apache
- [ ] Train/eval seeds: ExpDate class schema (`date` / `due` / `prod` / `code`) + own RU photos; confirm ExpDate dataset license before redistributing anything
- [ ] CIJ / dot-matrix preprocess (morphology, CLAHE)
- [ ] Keep `extract()` API stable

### 5 — Barcode sibling module

- [ ] EAN/UPC decode (e.g. zxing-cpp, Apache-2.0) as `packdate[barcode]`
- [ ] Open Food Facts for **identity only**: API v3 with a custom User-Agent, respecting 15 req/min for product reads and 10 req/min for search; bulk data from official dumps, not scraping
- [ ] Local cache; expect many misses for RU products (~36.5k tagged Russia at research time)
- [ ] Document: barcode ≠ per-pack expiry; ODbL attribution in NOTICE

### Later (does not block the library)

- Thin mobile / pantry UI under `apps/`
- HITL confirm UX patterns
- Public RU/CIS expiry dataset (200–500 photos) with clear license

## Out of scope for early versions

- Claiming industrial / Cognex-class field accuracy
- Shipping proprietary barcode DB dumps into a public OFF-derived database
- AGPL hard dependencies (e.g. Ultralytics YOLO as required runtime)
- VLM or cloud API as the default runtime
