# Roadmap

Near-term plan for **packdate**. Dates are rough; order matters more than calendar.

## Decisions behind this plan

- **Library first, app later.** The research archive (`02-full-report.md`, `07-reference-projects.md`) sketches an app-first path (barcode + manual date, OCR later). This repo deliberately starts with the library core instead; a pantry app is a consumer of the library, not a prerequisite.
- **Parse first.** The parser is the part no upstream project provides and it can be tested on plain strings, so it lands before any OCR.
- **Medicines first, food later** *(decided 2026-09-25)*. Printed expiry on EAEU medicine packs follows a narrow, regulated grammar (month + year, last day of the month implied — EAEU Council Decision №76, п.6 and п.30), and the date must appear on both box and blister. Food dates under ТР ТС 022/2011 range from hour precision to "годен N суток" relative to manufacture and "see the lid" references. Russian DataMatrix codes (МДЛП and the marked food groups) do **not** carry the expiry date, so OCR is still required for RU packs; EU (FMD) and US (DSCSA) drug codes do carry it. Sources: [research/10](docs/research/10-medicine-vs-food.md).
- **Full-frame OCR in v0.1 is a measured baseline, not the target design.** The research lists "full-image OCR without ROI" as an anti-pattern; v0.1 uses it only to get numbers. The bench in milestone 4 decides whether the ROI detector is needed.
- **Demo is a simple local web site** *(decided 2026-09-25)*: upload a photo, see the result, confirm or correct it, keep a list. It doubles as the labeling tool for fixtures. No mobile app and no Streamlit for now.
- **Light core.** `packdate` installs with no runtime dependencies; OCR, detector and barcode backends come as optional extras. Web demo dependencies stay under `apps/demo/`.

## Done

- [x] Public Apache-2.0 repo skeleton (`stofll/packdate`)
- [x] Research archive under `docs/research/` (OCR verdict, barcode/OFF, deps shortlist, domain choice, post-recognition design)
- [x] Module layout: `detect` / `recognize` / `parse` (stubs)
- [x] Architecture + licensing notes

## Next

### 0 — Repo hygiene *(this milestone)*

- [x] `ROADMAP.md` + clearer README status
- [x] SPDX license metadata in `pyproject.toml` (setuptools ≥ 77), pytest config
- [x] GitHub description, topics, homepage (set in the GitHub UI)
- [x] `AGENTS.md` — repo working rules + mandatory verification of claims
- [x] CI: GitHub Actions running `pytest` on Python 3.11–3.13 (together with the first tests in milestone 1)

### 1 — Date parser, medicines (library core)

- [x] Result types (see [ARCHITECTURE](docs/ARCHITECTURE.md#result-contract)): `iso_date`, `precision` (`day` / `month`), `valid_through` (last good day), `rule_id`, `kind` (`expiry` / `mfg` / `unknown`), `confidence` (`high` / `check` / `none`), `candidates`, `abstain_reason`, `source`
- [x] Medicine cue lexicon: «Годен до» / «годен» / «до», «Серия» / «Лот», «Дата изготовления» / «Изготовлено»; EN: EXP, LOT, MFG
- [x] EAEU №76 п.6 formats: `ММ ГГГГ`, `ММ.ГГГГ`, `ММ/ГГГГ`, `ММ_ГГГГ` and two-digit-year variants; full `ДД.ММ.ГГГГ` when the day is printed (shelf life < 12 months, п.30)
- [x] Rule `eaeu76_end_of_month`: month precision → `valid_through` = last day of that month
- [x] GS1 element-string parser (stdlib, input is already-decoded text): AI (01) GTIN, (17) expiry, (10) batch, (21) serial; FNC1 / GS separators; explicit policy for day `00`
- [x] OCR-noise normalization (`O→0`, `l/I→1`, spaces around separators) and calendar validation (reject `13.2027`)
- [ ] Spaces inside digit groups (`20 27`) and no-separator dates (`062027`) — see [PARSER known gaps](docs/PARSER.md#known-gaps)
- [x] Disambiguation policy documented in [docs/PARSER.md](docs/PARSER.md): cue beats position; MFG never becomes expiry; the expiry line vs the «Серия» line on the same pack
- [x] Abstain policy with reasons (`no_cue`, `cue_without_date`, `ambiguous`, `mfg_only`) — prefer no ISO over a wrong one
- [x] Unit tests on strings + format table under `tests/` (no photos required); stdlib only

**Done when:** OCR text (or fixture strings) from medicine packs → stable `valid_through` or honest abstain; MFG ≠ EXP on golden cases.

Food and cosmetics grammars (ТР ТС 022, ТР ТС 009) are deferred to milestone 6; their edge cases are listed in [research/12](docs/research/12-post-recognition.md#1-date-semantics-edge-cases-for-the-parser).

### 2 — `extract()` v0.1 (full-frame OCR + DataMatrix)

- [ ] OCR backend behind `packdate[ocr]`: RapidOCR with `cyrillic_PP-OCRv5_mobile_rec` as the first candidate, compared against PaddleOCR on the fixtures. PP-OCRv6 has no Cyrillic model yet ([research/11](docs/research/11-models-refresh.md))
- [ ] DataMatrix decode behind `packdate[barcode]` (zxing-cpp, Apache-2.0): GTIN + serial for identity and duplicate detection; AI (17) → expiry with `source=datamatrix` on EU/US packs. RU codes carry no expiry
- [ ] `pipeline.extract(...) → Result`
- [ ] Thin CLI under `apps/demo/`
- [ ] ~30 golden medicine photo fixtures + expected JSON (label provenance recorded; a cloud VLM may pre-label only with human review — see [research/11 §5](docs/research/11-models-refresh.md#5-cloud-vlm-as-an-offline-labeling-oracle-not-runtime))
- [ ] Fixture metrics: Exact `valid_through`, false ISO, abstain rate

**Done when:** install → run CLI on a few photos → readable JSON + clear "confirm me" cases.

### 3 — Local web demo (`apps/demo/`)

- [ ] Upload a photo → `extract()` → confirmation screen: crop with bbox, recognized date, confidence as a category, candidate chips; nothing preselected at low confidence; never auto-save
- [ ] Storage in SQLite (stdlib `sqlite3`): product / item / expiry / extraction (immutable pipeline output) / confirmation (human decision) — model in [research/12](docs/research/12-post-recognition.md#proposed-minimal-data-model)
- [ ] Medicine-cabinet list sorted by `valid_through`; "expires soon" section (default 5 days)
- [ ] Export confirmed corrections as fixtures (opt-in per item)
- [ ] Local only: photos stay on disk, EXIF / GPS stripped
- [ ] Small Python web framework + server-rendered HTML; open each dependency's license before adding it (AGENTS rule 5); dependencies isolated from the core package

**Done when:** a photo of a medicine box goes from upload to a confirmed entry in the list, and the correction can be exported as a fixture.

### 4 — Honest bench gate

- [ ] 40–60 own medicine photos, stratified: box print (inkjet / laser) / embossed blister / tube seam / foil blister / multi-date (MFG + EXP) / negative
- [ ] Report against the [architecture thresholds](docs/ARCHITECTURE.md#benchmark-gate-hypothesis-model-x-already-solves-it) (hypothesis, not marketing)
- [ ] Split failures into "OCR missed the date" vs "parser got it wrong", so the next step is picked by data: ROI + preprocess (milestone 5) or more parser work
- [ ] One small VLM as a comparison run only: GLM-OCR (MIT, lists `ru`), Qwen3.5-2B, or PaddleOCR-VL-1.6 0.9B (Apache-2.0)
- [ ] Document remaining gaps in README if gates miss

### 5 — ROI detector v0.2 *(only if milestone 4 shows OCR is ROI-bound)*

- [ ] `detect/` with a permissive ONNX path (no Ultralytics as hard dep); RF-DETR N/S/M/L only — XL/2XL are PML 1.0, not Apache
- [ ] Train/eval seeds: ExpDate (CC BY 4.0 per the [official dataset page](https://felizang.github.io/expdate/index_expdate.html); attribute the source, not the HF mirror) + own RU photos
- [ ] CIJ / dot-matrix preprocess (morphology, CLAHE)
- [ ] Keep `extract()` API stable

### 6 — Food: date grammar + barcode identity

- [ ] ТР ТС 022/2011 rules: «годен до конца» + month (end of month), hour precision for ≤ 72 h, «годен N суток» derived from the manufacture date, «срок годности не ограничен», location references ("см. на крышке") → abstain and ask for another photo
- [ ] EAN/UPC decode via `packdate[barcode]`
- [ ] Open Food Facts for **identity only**: API v3 with a custom User-Agent, respecting 15 req/min for product reads and 10 req/min for search; bulk data from official dumps, not scraping
- [ ] Local cache; expect many misses for RU products (~36.5k tagged Russia at research time)
- [ ] Document: EAN/UPC ≠ per-pack expiry; ODbL attribution in NOTICE

### Later (does not block the library)

- Reminders: daily "expires soon" digest rather than one notification per item
- Mobile client: Google ML Kit text recognition has no Cyrillic, so on-device OCR would be RapidOCR / PaddleOCR via ONNX Runtime or MNN
- Cosmetics (ТР ТС 009: «До 06.2027» = expired on 2027-05-31; PAO after opening)
- ЦРПТ True API as an optional online expiry source for RU codes — needs a participant token; terms for consumer apps unverified
- Public RU/CIS expiry dataset (200–500 photos) with clear license

## Out of scope for early versions

- Claiming industrial / Cognex-class field accuracy
- Shipping proprietary barcode DB dumps into a public OFF-derived database
- AGPL hard dependencies (e.g. Ultralytics YOLO as required runtime)
- VLM or cloud API as the default runtime
