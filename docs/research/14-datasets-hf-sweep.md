# Wide dataset sweep (HF-first) for packdate — research notes

**Access date:** 2026-09-26 (Europe/Moscow). Complements [13-datasets-audit.md](13-datasets-audit.md). Criteria: cast a **broad net**; do **not** early-filter empty cards, detection-only, non-RU, or NC — put them in the table with notes. No invented sizes; multi-GB dumps not downloaded; Cloudflare/401/429 → **UNVERIFIED** (not “does not exist”).

**packdate context (unchanged):** Apache-2.0; medicines-first expiry OCR; RU/CIS Cyrillic important; ~30 golden + 40–60 stratified bench; ExpDate ROI seed only if needed; OFF identity only.

---

## 1. Search log (queries + APIs)

### 1.1 Hugging Face Datasets API (`https://huggingface.co/api/datasets?search=…&limit=…`)

| Query / filter | Hits noted (this pass) | Notable IDs |
|---|---|---|
| `expiry` | 4 | `anuragzepto/expiry-ocr` (empty), `HitmanReborn/expiry_piper_*` (**audio**), `gemmozero/ai-domain-expiry-2026` (text) |
| `expiration` / `expiration_date` | 2 | `dimun/ExpirationDate` (known mirror), **`jojogo9/expiration_date`** (NEW, empty card + zips) |
| `expdate` / `expiry date OCR` / `expiration date detection` / `inkjet` / `packaging OCR` / `pharma packaging` / `medicine packaging` / `drug package` / `lot number expiry` / `срок годности` / `годен` | 0–few | — |
| `date stamp` | 1 | `aihpi/bottle-cap-date-stamps` (known) |
| `blister` | 1 | **`ABINSHA/blister_data`** (NEW) |
| `pharmaceutical` | 50 (mostly text/Vidore PDFs) | `vidore/vidore_v3_pharmaceuticals` (document pages, not packs); `twinkle-ai/tw-drug-labels-vision` (known leaflets) |
| `medicine pack` | 2 | robotics AgiBot video — wrong task |
| `drug label` | 5 | leaflets / openFDA text; `twinkle-ai/tw-drug-labels-vision` |
| `medicine ocr` | 2 | **`mjhbest/aihub-medicine-OCR`**, **`mahesh006/medicine-ocr-clean`** |
| `drug image` | 2+ | `gopeshgopi/Drug-Image-DataSet` (stub), `WJ1240424/Drug-image2name` (GPL, tiny) |
| `medicine` + `modality:image` | many | **`mennox/Italian-OTC-medicines`**, **`gokuljegadeesan/Medicine_boxes_annotated`**, Indian URL tables, electricsheep synth CSVs |
| `expired` | 1+ | **`VietMedTeam/Expired-Food-Items`** → **HTTP 401** (gated/private) — UNVERIFIED contents |
| Broader keyword union (`ocr`, `packaging`, `pharma`, `tablet`, `pill`, …) | ~180 unique IDs scanned | Most irrelevant (text QA, robotics, patents) |

Also fetched per-ID cards via `GET /api/datasets/{id}` and raw README where present.

### 1.2 HF models / Spaces (linked datasets)

| Search | Result |
|---|---|
| models `expiry date` / `expiration date` | `krishuggingface/Expiry_Date_Detection` (OD, 0 dl), `harshauckoo/expiry_date_extraction`, `Nicias/ocr_carte_date_expiration` — **no clear public pack dataset linked** |
| spaces `expiry ocr` | `LYZZMM/expiry-keeper-ocr` — app Space, not a dataset release |

### 1.3 Roboflow Universe

- Search HTML for `expiry date`, `expiration date`, `pharmaceutical packaging`, `medicine packaging`, `lot expiry`, `blister`, … → **~390 path-like hits** (many false positives: parking-lot, date-fruit, packaging defects).
- Verified pages (og:description + license link) when not rate-limited:
  - Known: TCC 668 CC0; `ml-model-tlmqd` 2518 CC BY 4.0; college/nguyen/choi/prtica/expiry-ocr (sizes as in [13] or UNVERIFIED this pass).
  - **NEW verified:** `expiry-date/area-expiry-date` **4,480** images, **CC BY 4.0**; `fyp-hdzz0/medicine-packaging` **865** CC0; `kabul-university-evptq/drug-name-detection` **1,823** CC BY 4.0.
- Many high-interest slugs (`homestorage/date-expiry`, HAW Hamburg, NHS `find-expiration-date`, `thesismodel/medbox-detection-expiry-quantity`, `medicine-ocr-cqbuu/medicine-expiry-detection-uqsvc`, …) returned **HTTP 429** after bulk fetch — catalogued as **UNVERIFIED size**, not absent.
- Roboflow blog (2026-06-11) cites a **“major project”** pharma set with **1,716** images (`name` + `date` classes). Exact Universe slug **not resolved** this pass (`major-project-8anow/…` 404) — **UNVERIFIED URL**.

### 1.4 Mendeley public-api

| ID | Name | License | Size field |
|---|---|---|---|
| `bsmy5jjysy` | Mobile-Captured Drug Packs (known) | CC BY 4.0 | ~2k images (see [13]) |
| **`bjy2svvmn8`** | **Mobile-Captured Pharmaceutical Medication Packages** | **CC BY 4.0** | **3,900** JPG + xlsx; `size` ≈ **6.46 GB** |
| **`3cpx2fmn3r`** | **Food Packaging OCR Dataset** | **CC BY 4.0** | zip **2,561,540,317** B (~2.56 GB); **image count UNVERIFIED** (not unzipped) |

### 1.5 Zenodo API

| Query | Useful hits |
|---|---|
| expiration / expiry / packaging OCR | Mostly papers; **ChronoShelf** = code paper, not a photo dump |
| — | **Bilingual Food Labels** [10.5281/zenodo.14630762](https://doi.org/10.5281/zenodo.14630762) **CC BY 4.0**, **350** images (counted from `all_images.zip` listing) |
| — | **HalalBench** [10.5281/zenodo.18674795](https://doi.org/10.5281/zenodo.18674795) dataset **CC BY-SA 4.0** (card); **1,043** images claimed (50 real / 993 synth); Zenodo file list this pass showed **PDF only** — full image dump via GitHub `data/` instructions (**download path partially UNVERIFIED**) |

### 1.6 Figshare API

`search_for=expiration date packaging OCR` / `pharmaceutical packaging images` → no relevant packaging-expiry dumps (birth records / unrelated).

### 1.7 Papers with Code

HTML search returned empty/redirect this path; no dedicated “expiration date detection” dataset page surfaced beyond ExpDate literature already in [13].

### 1.8 GitHub / web

| Lead | Status |
|---|---|
| ExpDate official + HF mirror | Known ([13]) |
| `ameera3/OCR_Expiration_Date`, `510-Date`, `HieuNTg/Date-Recognition` | Known avoid / no LICENSE |
| MedNet-MoBiL / Saqib `InputImages.zip` (~3k packs cited in paper) | Repo lookup **rate-limited / UNVERIFIED** this pass |
| Algerian drug-label OCR papers | **No public dump found** |
| SA NFP packaging OCR (arXiv 2510.03570): 1,628 images / 113 GT | **Not public** (paper dataset description only) |
| Roboflow blog medical lot/expiry pipeline | Points at Universe “major project” (slug UNVERIFIED) |

### 1.9 Wikimedia Commons API `categoryinfo`

| Category | Files (2026-09-26) | Note |
|---|---|---|
| Pharmaceutical drugs of Russia | 122 | Known |
| Photographs by Retired electrician/medical | (known branch union) | Known |
| **Pharmaceutical product packaging** | **952** | Global expand target (already flagged in [13]) |
| **Blister packs** | **56** | **NEW category tally** (not RU-specific) |
| Drug packaging | 3 | Tiny |
| Expiry dates | 2 | Tiny |
| Medicine packages / Medication packaging / Best before dates | missing or empty | — |

### 1.10 Kaggle

Web search HTML this path returned no dataset links (likely JS/bot wall). Known scraped medicine-tablet set remains **UNVERIFIED** ([13]).

### 1.11 OFF / Beauty Facts

Identity-only reaffirmation; no new expiry GT. (See [13] / [06].)

---

## 2. Already known (brief re-list — full detail in [13])

| Source | Role reminder |
|---|---|
| Commons RU pharma (+ branch labels) | Golden / OCR bench seed (Cyrillic) |
| ExpDate Products-Real (official CC BY 4.0; not HF `afl-3.0` mirror) | ROI seed; non-RU OCR bench |
| `aihpi/bottle-cap-date-stamps` | Inkjet OCR hardness |
| Mobile-Captured Drug Packs (`bsmy5jjysy`) | Medicine photos, **no expiry GT** |
| Roboflow TCC products-expiration-dates CC0 (668) | ROI seed |
| Other Roboflow expiry sets in [13] | Conditional ROI |
| OFF / Beauty / Pet Facts | **Identity only** |
| TextOCR | Weak pretrain |
| Avoid: PharmaPack academic, Mobiusi NC, scraped Kaggle, no-LICENSE GitHub, DailyMed JPEGs as fixtures, empty `anuragzepto/expiry-ocr` |

---

## 3. Full candidate table (ALL hits this sweep)

Columns: **Labels** = boxes / transcription / date kind; **Role** = golden \| OCR bench \| ROI seed \| identity \| pretrain \| avoid; **Redistrib** = yes \| conditional \| no.

### 3.A New or newly catalogued (vs [13])

| id / URL | Size (upstream) | Labels | License + link | RU/Cyrillic | Role | Redistrib | Notes |
|---|---|---|---|---|---|---|---|
| **Food Packaging OCR** — [Mendeley 3cpx2fmn3r.2](https://data.mendeley.com/datasets/3cpx2fmn3r/2) | Zip **2.56 GB** (`size` API); **#images UNVERIFIED** | Det + rec annotations; fields include product name, brand, ingredients, nutrition, **validity period** | **CC BY 4.0** (Mendeley `data_licence`) | Low (Malaysia MMU; EN/MS likely) | OCR bench / pretrain (food; validity text) | Yes (attrib.; 3P content caveat) | Strongest **new** open packaging-OCR dump this pass; not medicine-first; do not vendor zip into git |
| **Mobile-Captured Pharmaceutical Medication Packages** — [doi:10.17632/bjy2svvmn8.1](https://doi.org/10.17632/bjy2svvmn8.1) | **3,900** images / **150** packs; ~**6.46 GB** | **No** expiry transcription | **CC BY 4.0** | Low / UNVERIFIED (Egypt authors; EN/AR likely) | Identity / hardness | Yes (attrib.) | **Distinct** from `bsmy5jjysy` (2k/166); larger unlabeled medicine-photo pool |
| **Roboflow `expiry-date/area-expiry-date`** — [Universe](https://universe.roboflow.com/expiry-date/area-expiry-date) | **4,480** (og:description) | Detection (area expiry) | **CC BY 4.0** (Universe UI) | UNVERIFIED | ROI seed (largest Universe expiry set found) | Conditional (provenance opaque) | Bigger than TCC; still uploader-declared |
| **`mennox/Italian-OTC-medicines`** — [HF](https://huggingface.co/datasets/mennox/Italian-OTC-medicines) | **719** JPG under `out/` (+ `medicines.json` **725** rows) | Product metadata (EAN/SKU, SmPC-style text incl. *Scadenza e conservazione* storage wording) — **not** inkjet pack-date GT | **Apache-2.0** (card) | None (Italian) | Identity / OCR hardness | Yes | Mentions accessibility “expiry” use-case; labels are leaflet/storage text, not printed EXP crops |
| **`ABINSHA/blister_data`** — [HF](https://huggingface.co/datasets/ABINSHA/blister_data) | **1,366** PNG = **683** `pair_*_batch` + **683** `pair_*_med` (sibling count) | Pair naming suggests batch strip vs med blister — **no card, no LICENSE, no transcription schema** | **None** on card | UNVERIFIED | Avoid until license; optional hardness if clarified | **No** | Empty card; visually relevant filenames |
| **`jojogo9/expiration_date`** — [HF](https://huggingface.co/datasets/jojogo9/expiration_date) | `train_data.zip` **361,112,313** B; `test_data 2.zip` **300,526,739** B (~662 MB) | Unknown (no README) | **None** | UNVERIFIED | Avoid until license + schema | **No** | Empty card; do not invent contents |
| **`VietMedTeam/Expired-Food-Items`** — [HF](https://huggingface.co/datasets/VietMedTeam/Expired-Food-Items) | UNVERIFIED | Search snippets show manufacturing/expiration **text captions** | UNVERIFIED | None (VI/EN food) | UNVERIFIED → treat as gated | No until open | **HTTP 401** API + page — exists but inaccessible without auth |
| **`gokuljegadeesan/Medicine_boxes_annotated`** — [HF](https://huggingface.co/datasets/gokuljegadeesan/Medicine_boxes_annotated) | **~515** JPG counted in tree (train/valid/test); YOLO `Med-Box` | Detection boxes only (whole box) | **None** | UNVERIFIED (likely IN packs) | Identity / pack detection seed | **No** until license | Wrong granularity for expiry ROI |
| **`mahesh006/medicine-ocr-clean`** — [HF](https://huggingface.co/datasets/mahesh006/medicine-ocr-clean) | **6,424** rows (card); ~68 MB | `image` + `text` = **drug name** strings (viewer samples) | **None** | None | Identity / name OCR; **not** expiry | **No** until license | Empty prose README |
| **`mjhbest/aihub-medicine-OCR`** — [HF](https://huggingface.co/datasets/mjhbest/aihub-medicine-OCR) | WebDataset shards (`medicine-TL*`, `VL*`, …); size_categories `n<1K` tag **suspicious** vs shard count | Korean AI Hub–style medicine OCR (likely leaflets/scripts) | **None** on HF | None (KO) | Pretrain? / avoid until AI Hub terms checked | **No** pending terms | No README; upstream AI Hub licenses often research-only |
| **Roboflow `fyp-hdzz0/medicine-packaging`** | **865** | Class names = drug brands (Anarex, Atenelol, …) | **CC0** | None | Identity (classification) | Yes (CC0) | Not expiry-labeled |
| **Roboflow `kabul-university-evptq/drug-name-detection`** | **1,823** | `drug-name` boxes | **CC BY 4.0** | UNVERIFIED | Identity | Conditional | Also mirrored on Kaggle (provenance still uploader-declared) |
| **HalalBench** — [GitHub](https://github.com/halallens-no/halalbench) / [Zenodo 18674795](https://doi.org/10.5281/zenodo.18674795) | **1,043** (50 real / 993 synth) claimed | COCO OCR annotations; **ingredients**, 14 langs — **not** expiry-specific | Dataset **CC BY-SA 4.0** (README badge); code MIT | No RU | Pretrain / packaging OCR bench | Conditional (SA share-alike) | Zenodo file list this pass = PDF; image host via repo `data/` — confirm before planning download |
| **Bilingual Food Labels** — [Zenodo 14630762](https://doi.org/10.5281/zenodo.14630762) | **350** images (`all_images.zip` listing); GT CSVs | Ingredient / bilingual label GT (CSV) | **CC BY 4.0** | No | Pretrain / food packaging OCR | Yes | Not expiry GT; Amazon-style filenames |
| **Commons `Category:Blister packs`** | **56** files | None | Per-file | Mixed | ROI hardness seed (foil/blister) | Conditional | Filter for visible dates; not RU |
| **Commons `Category:Pharmaceutical product packaging`** | **952** files | None | Per-file | Mixed global | Expand Commons pipeline | Conditional | Already named in [13] acquisition; tallied again |
| **`zavzyatiy/medicines_from_zakupki_gov_ru`** — [HF](https://huggingface.co/datasets/zavzyatiy/medicines_from_zakupki_gov_ru) | Tabular **1M–10M** size tag; procurement CSV/XLSX | Text fields can include «Годен до» in lot descriptions — **no photos** | **Apache-2.0** | **Yes (RU text)** | Parser string mining only | Yes | **Not** a vision set |
| **`MiXaiLL76/7SEG_OCR`** | **3,333** synth 7-segment | Digits transcription | **MIT** | N/A | Weak pretrain (device digits ≠ CIJ) | Yes | Not packaging |
| **`UniqueData/ocr-barcodes-detection`** | Grocery + barcode OCR | Barcode polygons + text | **CC BY-NC-ND 4.0** | No | Avoid (NC-ND) | **No** | Barcode, not expiry |
| **Roboflow blog “major project” pharma 1,716** | Blog claims **1,716**; classes `name` + `date` | Detection ROI for lot/expiry strip | UNVERIFIED (Universe slug unresolved) | UNVERIFIED | ROI seed **if** found | UNVERIFIED | Track down slug later; do not invent URL |
| **Roboflow long-tail expiry / medicine slugs** (HAW, NHS, `thesismodel/medbox-…`, `homestorage/date-expiry` ~200 from search title, `medicine-ocr-cqbuu/…`, `kangminho/expiration-date`, `dateprinted/date-m4dhd`, Lipton expiry, packaging-date-code QC, blister-packaged-medicine thesis, …) | Mostly **UNVERIFIED** (429) | Typically detection | UI often CC BY 4.0 when page loads | UNVERIFIED | Catalog only | Conditional | Re-fetch individually when rate limit clears |
| **SA NFP food packaging** (arXiv:2510.03570) | Paper: **1,628** / GT **113** | Ingredients + NFP transcription | **Not public** | No | Avoid (unavailable) | No | Documented for completeness |
| **HitmanReborn/expiry_piper_*** | Audio TTS of “expiry” phrases | Audio | None | — | Avoid (wrong modality) | No | — |
| **Vidore v3 pharmaceuticals** | 10k–100k docs | Doc VQA | CC BY 4.0 | No | Avoid for packdate vision | Yes but wrong task | PDF slides, not packs |
| **electricsheepafrica/* medicine*** synth tabular | CSV + token “image” tags | Synthetic stats | CC BY 4.0 | No | Avoid | — | Not photos |
| **`gopeshgopi/Drug-Image-DataSet`**, **`area416/Pharma_Marketing_Content`**, Indian medicines URL tables | Tiny / URL-only / marketing | — | None / unknown | — | Avoid / identity thin | No | Low value |

### 3.B Already in [13] (reconfirmed this pass where checked)

| Source | Reconfirm |
|---|---|
| ExpDate / `dimun/ExpirationDate` | Official CC BY 4.0; mirror still `afl-3.0` |
| bottle-cap-date-stamps | CC BY 4.0; 438 images |
| Mobile-Captured Drug Packs `bsmy5jjysy` | CC BY 4.0 |
| Roboflow TCC / ml-model / college / nguyen / choi / prtica / expiry-ocr | Licenses as [13]; some sizes re-seen via og tags |
| OFF / TextOCR / tw-drug-labels / Mobiusi / PharmaPack / DailyMed / no-LICENSE GitHub | Unchanged advice |
| Commons RU categories | 122(+medical photographer cat); draft labels on branch |

---

## 4. NEW vs already in 13 — summary count

| Bucket | Approx. count this pass |
|---|---|
| **Materially new vision/OCR candidates** (with enough metadata to discuss) | **~18–22** (Food Packaging OCR; bjy2 3900 packs; area-expiry 4480; Italian OTC; blister_data; jojogo9; medicine-ocr-clean; Medicine_boxes; aihub medicine OCR; RF medicine-packaging CC0; RF drug-name; HalalBench; Bilingual Food Labels; Commons blister; plus gated VietMedTeam; unresolved RF major-project; RU zakupki text) |
| Roboflow long-tail paths discovered but size **UNVERIFIED** | **dozens** (do not treat search HTML as a verified dataset list) |
| HF noise (text QA, robotics, audio “expiry”) filed as avoid | many |
| Confirmed **still missing**: large labeled **RU medicine expiry** photo set | yes |

---

## 5. Shortlist upgrades (relative to [13] executive table)

Keep [13] priorities 1–8. **Add / raise** only where license-safe and task-adjacent:

| Priority delta | Source | Why upgrade |
|---|---|---|
| **+A** | **Food Packaging OCR (Mendeley CC BY 4.0)** | Real packaging det+rec **including validity-period** text — best new OCR bench/pretrain outside ExpDate; food not medicine |
| **+B** | **Roboflow `area-expiry-date` (4,480, CC BY 4.0)** | Largest verified open expiry-**detection** set; provenance still Conditional — use after spot-check; prefer behind TCC CC0 if rights anxiety |
| **+C** | **bjy2 Mobile-Captured Pharmaceutical Packages (3,900, CC BY 4.0)** | Larger unlabeled medicine-photo pool than `bsmy5jjysy`; still **no** expiry GT |
| **+D** | **Italian OTC (Apache-2.0, 719)** | Clean pack photos + EAN for identity experiments; storage text ≠ inkjet EXP |
| **+E** | **HalalBench / Bilingual Food Labels** | Packaging OCR difficulty / multilingual pretrain; SA on HalalBench; not expiry GT |
| **Optional** | RF `medicine-packaging` CC0 (865), drug-name 1823 | Identity only |
| **Do not upgrade** | `jojogo9`, `ABINSHA/blister_data`, `medicine-ocr-clean`, AI Hub mirror, VietMedTeam 401, NC UniqueData | License or schema gaps |

**Still primary for RU medicines:** own photos + Commons expand + human-confirmed labels ([13] acquisition plan).

---

## 6. Still missing for RU medicines

| Need | Status after this sweep |
|---|---|
| Large **labeled** RU/CIS medicine packs with visible expiry + lot | **Still missing.** HF Cyrillic queries (`срок годности`, `годен`) → **0** datasets. Closest RU artifact = **tabular** zakupki text, not photos |
| Hard strata: embossed blister, tube seam, foil, CIJ «Годен до», rotated panel, MFG+EXP, negatives | Commons draft + blister category thin; no scale |
| EAEU date formats on photos | Parser fixtures ≠ photo coverage |
| RU DataMatrix in-frame with OCR date | Not found as open labeled set |
| Public Честный ЗНАК photos with clear license | Not found |
| Cyrillic CIJ on curved/blister | Bottle-cap remains Latin digits |

**Conclusion:** Broadening the net found **useful non-RU packaging OCR / expiry-detection / medicine-photo** resources, especially Food Packaging OCR (Mendeley), Roboflow area-expiry (4.5k), and the larger Mendeley pharma photo set — but **did not** uncover a public labeled RU medicines expiry corpus. packdate’s path remains own capture + Commons + honest bench.

---

## 7. Top surprises on Hugging Face

1. **Almost no public HF datasets** match `expiry` / `expiration` / `срок годности` with pack photos + date GT. The namespace is dominated by empty stubs, audio TTS, domain-name “expiry”, or mistagged ExpDate mirrors.
2. **`VietMedTeam/Expired-Food-Items`** appears in search/snippets with expiry captions but is **401 gated** — easy to miss or mis-report as missing.
3. **Medicine-adjacent HF hits are mostly wrong task:** Italian OTC (identity), medicine-ocr-clean (**names**), Medicine_boxes (whole-box OD), tw-drug leaflets, Vidore PDFs, AI Hub shards without SPDX.
4. **`ABINSHA/blister_data`** and **`jojogo9/expiration_date`** look on-topic by name/files but ship **without licenses** — classic “HF graveyard” risk.
5. Real progress this pass was **off-HF**: Mendeley Food Packaging OCR + second Mobile-Captured pharma dump; Roboflow **area-expiry-date 4480**; Zenodo HalalBench / Bilingual Food Labels.

---

## 8. Hard gaps (actionable)

1. **RU labeled expiry photos** — still the #1 gap.
2. **Expiry transcription** (not just detection boxes) on open medicine packs — ExpDate remains the main public transcription set; Food Packaging OCR may help on “validity period” but is food and image count unverified without unzip.
3. **License vacuum** on the few HF names that look relevant (`jojogo9`, blister_data, medicine-ocr-clean, Medicine_boxes, aihub mirror).
4. **Roboflow rate limits / provenance** — dozens of expiry-named projects exist; sizes/licenses need one-by-one verification; image origin still uploader-declared.
5. **Gated / non-public academic sets** (VietMedTeam, SA NFP 1628, Algerian drug OCR, PharmaPack) — document existence; do not plan Apache redistrib.

---

## 9. Sources fetched (2026-09-26)

- HF Datasets API multi-query + per-id cards; datasets-server info for VietMedTeam (401)
- HF model/space search for expiry
- Roboflow Universe search HTML + selected project pages (og:description / creativecommons links); blog.roboflow.com lot/expiry article
- Mendeley `public-api/datasets/{id}` for `3cpx2fmn3r`, `bjy2svvmn8`, `bsmy5jjysy`
- Zenodo API records `14630762`, `18674795`; counted 350 files in Bilingual `all_images.zip`
- Wikimedia Commons `categoryinfo` for RU + packaging + blister categories
- Figshare API search (no relevant hits)
- arXiv HTML 2510.03570 (SA NFP; not public)
- WebSearch cross-checks: ExpDate, MedNet-MoBiL, ChronoShelf, HalalBench, Algerian OCR
- Baseline: [13](13-datasets-audit.md), `datasets/README.md`

---

## 10. UNVERIFIED (open)

1. Exact image/annotation counts inside Food Packaging OCR zip (2.56 GB not extracted).
2. Contents/schema/license of `jojogo9/expiration_date` and `ABINSHA/blister_data`.
3. `VietMedTeam/Expired-Food-Items` (401).
4. Roboflow “major project” 1,716 exact Universe URL; many RF expiry slug sizes (429).
5. HalalBench full image host beyond Zenodo PDF.
6. AI Hub terms for `mjhbest/aihub-medicine-OCR`.
7. Kaggle medicine-tablet-pack license (bot wall).
8. Whether ExpDate / Food Packaging OCR / area-expiry contain any Cyrillic cues (not sampled).
