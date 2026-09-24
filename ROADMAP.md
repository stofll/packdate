# Roadmap

Near-term plan for **packdate**. Dates are rough; order matters more than calendar.

## Done

- [x] Public Apache-2.0 repo skeleton (`stofll/packdate`)
- [x] Research archive under `docs/research/` (OCR verdict, barcode/OFF, deps shortlist)
- [x] Module layout: `detect` / `recognize` / `parse` (stubs)
- [x] Architecture + licensing notes

## Next

### 0 — Repo hygiene *(this milestone)*

- [x] `ROADMAP.md` + clearer README status
- [ ] GitHub description, topics, homepage pointer *(Contents-only PAT cannot PATCH; set in GitHub UI or widen token)*

### 1 — Date parser (library core)

- [ ] RU/EN cue lexicon (EXP / BB / MFG / «годен до» / …)
- [ ] Format normalization + calendar validation
- [ ] Result types: `iso_date`, `kind`, `confidence`, `candidates`
- [ ] Abstain policy (prefer no ISO over a wrong one)
- [ ] Unit tests on strings + format table (no photos required)

**Done when:** OCR text (or fixture strings) → stable ISO or honest abstain; MFG ≠ EXP on golden cases.

### 2 — `extract()` v0.1 (full-frame OCR)

- [ ] Default backend: PP-OCR + Cyrillic (optional heavy extra)
- [ ] `pipeline.extract(...) → Result`
- [ ] Thin CLI under `apps/demo/`
- [ ] ~25–40 golden photo fixtures + expected JSON
- [ ] Fixture metrics: Exact ISO, false ISO, abstain rate

**Done when:** install → run CLI on a few photos → readable JSON + clear “confirm me” cases.

### 3 — Honest bench gate

- [ ] Stratified set: inkjet / thermal / embossed / curved / multi-date / negative
- [ ] Report against architecture thresholds (hypothesis, not marketing)
- [ ] Document remaining gaps in README if gates miss

### 4 — ROI detector v0.2 *(only if v0.1 is ROI-bound)*

- [ ] `detect/` with permissive ONNX path (no Ultralytics as hard dep)
- [ ] CIJ-friendly preprocess
- [ ] Keep `extract()` API stable

### 5 — Barcode sibling module

- [ ] EAN/UPC decode (e.g. zxing-cpp)
- [ ] Open Food Facts / local cache for **identity only**
- [ ] Document: barcode ≠ per-pack expiry; ODbL attribution in NOTICE

### Later (does not block the library)

- Thin mobile / pantry UI under `apps/`
- HITL confirm UX patterns
- Optional small VLM as a **bench comparison**, not the default runtime

## Out of scope for early versions

- Claiming industrial / Cognex-class field accuracy
- Shipping proprietary barcode DB dumps into a public OFF-derived database
- AGPL hard dependencies (e.g. Ultralytics YOLO as required runtime)
