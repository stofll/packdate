# Open datasets audit for packdate (research notes, 2026-09-26)

**Access date:** 2026-09-26. Every size and license below was checked against a primary page, API, or LICENSE file on that date, or is marked **UNVERIFIED**. Complements [03](03-ocr-verdict.md) (datasets section), [06](06-barcode-and-open-data.md), [10](10-medicine-vs-food.md), [11](11-models-refresh.md), and the catalog on branch `data/open-sources` (`datasets/README.md`).

**packdate context:** Apache-2.0 library; medicines-first expiry OCR on packaging photos; RU/CIS Cyrillic important; ~30 golden fixtures (milestone 2) and 40–60 stratified bench photos (milestone 4); ExpDate as ROI seed only if milestone 4 shows OCR is ROI-bound (milestone 5); OFF for identity only (milestone 6); public RU dataset is a later goal (ROADMAP “Later”).

---

## Executive shortlist (medicine-first fixtures / bench)

Build **~30 golden + 40–60 stratified bench** mostly from **own photos** and **Commons RU packs**, not by redistributing multi-GB third-party dumps into the repo.

| Priority | Source | Why | License (verified) | Fit |
|---|---|---|---|---|
| 1 | **Own medicine photos** (demo-as-labeler) | Only way to cover EAEU «Годен до» / blister / tube seam / DataMatrix RU with human-confirmed labels | You own the photos; record label provenance | Golden + stratified bench |
| 2 | **Wikimedia Commons** RU pharma categories + packdate labels on `data/open-sources` | Already has Cyrillic packs; 35 draft labels (12 with date); per-file licenses | Per file: CC0 / CC BY / CC BY-SA / PD (see branch README) | Seed fixtures (**Conditional** redistribute: keep `manifest.json` attribution; SA files stay SA) |
| 3 | **ExpDate Products-Real** (official page, not HF mirror) | Best public expiry ROI set; boxes + transcriptions; includes pharma packs | **CC BY 4.0** ([official dataset page](https://felizang.github.io/expdate/index_expdate.html)) | Seed for ROI (milestone 5); OCR bench for non-RU formats |
| 4 | **aihpi/bottle-cap-date-stamps** | Hard inkjet on curved metal — stress-test for CIJ OCR | **CC BY 4.0** (HF card) | OCR bench stratum (bottle caps, not medicine) |
| 5 | **Mobile-Captured Drug Packs** (Mendeley) | 2,000 phone photos of 166 drug packs; angles/lighting | **CC BY 4.0** (Mendeley `data_licence`) | Medicine packaging photos; **no expiry transcription** — use as unlabeled / identity / OCR hardness only |
| 6 | **Roboflow TCC `products-expiration-dates`** | 668 Brazilian packs; ExpDate-style classes; paper ERAMIARS 2025 | **CC0 1.0** (Universe page, 2026-09-26) | Seed for ROI (PT/BR formats); provenance of supermarket photos is uploader-declared |
| 7 | **Open Food Facts** (dumps / AWS images) | Product identity + packaging photos | Data **ODbL** + **DbCL**; images **CC-BY-SA** ([OFF data page](https://world.openfoodfacts.org/data)) | **Identity only** — never as per-pack expiry |
| 8 | **TextOCR** (optional pretrain) | Scene-text boxes + transcriptions | Annotations **CC BY 4.0**; images from OpenImages (separate terms) | Weak transfer to inkjet/embossed expiry — optional seed only |

**Do not** treat Roboflow Universe, Kaggle scraped packs, PharmaPack (academic-only), Mobiusi NC, empty HF cards, or DailyMed carton JPEGs as drop-in golden fixtures without a further rights pass.

---

## Full candidate table

Columns: **Redistrib** = OK to publish fixtures/derivatives under packdate’s Apache docs + NOTICE?  
**Fit** = Seed for ROI | OCR bench | Parser string-only N/A | Identity | Avoid.

| Name + primary URL | Domain | Size (upstream) | Labels | License + citation | Redistrib | Cyrillic / RU | Fit | Caveats |
|---|---|---|---|---|---|---|---|---|
| **Wikimedia Commons** `Category:Pharmaceutical drugs of Russia` + `Category:Photographs by Retired electrician/medical` — [Commons](https://commons.wikimedia.org/); script+labels on `origin/data/open-sources` | Medicine packaging (RU market) | Categories: **122** + **99** files (API 2026-09-26); branch README: **177** unique JPG/PNG after union/filter; **35** draft labels (12 with `valid_through`) | Draft `valid_through` / stratum in `commons_ru_drugs.labels.json` (Claude visual review 2026-09-25; **not human-confirmed**) | **Per file** (branch tally 2026-09-25: 100 CC0, 68 CC BY-SA 4.0, 5 CC BY, 4 PD) | **Conditional** — attribute; SA → share-alike derivatives | **High** | OCR bench / golden seed | Keep `manifest.json`; 1280 px thumbs may miss embossed dates |
| **ExpDate Products-Real** — [official dataset page](https://felizang.github.io/expdate/index_expdate.html); Drive folder linked from page; paper doi [10.1016/j.eswa.2022.117310](https://doi.org/10.1016/j.eswa.2022.117310) | Food / beverage / **pharma** packs | **1,767** real (1,102 train / 665 test); Products-Synth ~12k; Date-Synth 128k; Components-Synth 450k (official page) | Boxes + transcriptions; classes date/due/prod/code; test `exp` | **CC BY 4.0** (official `index_expdate.html` License section, fetched 2026-09-26) | **Yes** (with attribution + cite KIST) | Low (formats are EN/numeric; not EAEU «Годен до») | Seed for ROI; OCR bench (non-RU) | **HF mirror `dimun/ExpirationDate` tags `afl-3.0`** — do not attribute via mirror; homepage footer CC BY-SA is Nerfies site template, not the dataset |
| **aihpi/bottle-cap-date-stamps** — [HF](https://huggingface.co/datasets/aihpi/bottle-cap-date-stamps) | Bottle caps (mineral water) | **438** images; **1,082** date labels (card) | Transcription `DD.MM.YY` in `metadata.csv`; multi-cap `;`-joined | **CC BY 4.0** (HF card + API `license:cc-by-4.0`) | **Yes** (attribution) | Low (Latin digits) | OCR bench (inkjet / reflective) | Not medicine; VLM-assisted labels with human correction |
| **Mobile-Captured Drug Packs** — [Mendeley doi 10.17632/bsmy5jjysy.3](https://doi.org/10.17632/bsmy5jjysy.3) | Medicine packaging (phone photos) | **2,000** images; **166** packages (dataset description) | None for expiry (research = drug label extraction) | **CC BY 4.0** (Mendeley API `data_licence.short_name`, 2026-09-26) | **Yes** (attribution; third-party content caveat in CC BY deed) | Low / UNVERIFIED market (Cairo University authors; Arabic/EN packs likely) | Medicine pack photos / hardness; **not** expiry-labeled | ~5.9 GB total (`size` in API); do not vendor into git |
| **Roboflow TCC Products Expiration Dates** — [Universe](https://universe.roboflow.com/tcc-xrqer/products-expiration-dates); paper [ERAMIARS 2025](https://sol.sbc.org.br/index.php/eramiars/article/view/39448) | General packaging (BR supermarket) | **668** images (paper + og:description) | Detection: date / code / prod / due (ExpDate schema); **no** transcription in paper scope | **CC0 1.0** (Universe “Public Domain” + `creativecommons.org/publicdomain/zero/1.0/`, 2026-09-26) | **Yes** (CC0) | None | Seed for ROI | Uploader-declared; image provenance not independently audited |
| **Roboflow `ml-model-tlmqd/expiry-date-recognition`** — [Universe](https://universe.roboflow.com/ml-model-tlmqd/expiry-date-recognition) | Packaging expiry detection | **2,518** images (og:description) | Detection (Universe) | **CC BY 4.0** (Universe UI, 2026-09-26) | **Conditional** — attribution; **provenance UNVERIFIED** | UNVERIFIED | Seed for ROI (secondary) | Self-declared license; treat as unverified origin |
| **Roboflow `college-37gbk/expiry-date-detection-wowdr`** | Packaging | **100** (og:description) | Detection | **CC BY 4.0** (Universe UI) | Conditional | UNVERIFIED | Minor ROI seed | Small; provenance UNVERIFIED |
| **Roboflow `nguyen-luat-gia-khoi/expired-date-dataset`** | Packaging / text | **211** (og:description) | Detection | **CC BY 4.0** (Universe UI) | Conditional | UNVERIFIED | Minor | Provenance UNVERIFIED |
| **Roboflow `choi-t72ze/expiration-date-w0s6o`** | Packaging | **13** (og:description) | Detection | **CC BY 4.0** (Universe UI) | Conditional | — | Too small | Skip for training |
| **Roboflow `prtica-em-pesquisa/product-expiration`**, **`expiry-ocr/expiry-ocr`** | Packaging | Size **UNVERIFIED** here | Detection (Universe) | **CC BY 4.0** (Universe UI, 2026-09-26) | Conditional | UNVERIFIED | Optional | Same provenance caveat |
| **Open Food Facts** — [data](https://world.openfoodfacts.org/data); images AWS Open Data | Food packaging | Products: Russia tag **36,581** (OFF API v2 search, 2026-09-26); images “over 6.7 million” (OFF blog; not re-counted) | Product fields; OCR text dumps exist — **not** per-pack expiry GT | DB **ODbL** + contents **DbCL**; images **CC-BY-SA** (OFF data page) | **Conditional** — ODbL share-alike for DB derivatives; image SA | Modest RU coverage | **Identity** | Barcode ≠ expiry; rate limits; custom User-Agent |
| **Open Beauty / Pet / Products Facts** | Cosmetics / pet / other | OPF search `medicines` count **112** (API, 2026-09-26) | Identity | Same family as OFF (verify per site) | Conditional | Low | Identity (thin) | Not a medicine expiry set |
| **TextOCR** — [textvqa.org/textocr](https://textvqa.org/textocr/dataset/) | Scene text | Train **21,778** images / 714k words; val 3,124; test 3,232 (site) | Polygons + transcription | Annotations **CC BY 4.0**; images from **OpenImages** (separate terms) | **Conditional** | Low for RU packaging | Weak pretrain seed | Limited transfer to CIJ/embossed expiry |
| **twinkle-ai/tw-drug-labels-vision** — [HF](https://huggingface.co/datasets/twinkle-ai/tw-drug-labels-vision) | Pharma **leaflets / cartons** (TFDA TW) | **44,663** records; ~67,947 rendered pages (card) | Structured leaflet fields; `storage` text — **not** inkjet pack expiry | **CC BY 4.0** (HF card) | Yes (attribution) | Traditional Chinese — **not** RU Cyrillic | Document OCR / carton layout only | Wrong task for packdate expiry inkjet; dpi 90 WebP |
| **510-Date** (ExpRec companion) — [GitHub](https://github.com/AnanasPizzaMigliore/510-Date); cited from [MDPI Algorithms 18(5):286](https://www.mdpi.com/1999-4893/18/5/286) | Date crops (recognition) | Paper: **510** samples | Recognition crops (LMDB `Date/data.mdb` in repo) | Repo **no LICENSE** file (API `license: null`, 2026-09-26); article CC BY ≠ dataset | **No** until clarified | UNVERIFIED | Avoid until license | ExpRec Android demo is **GPL-3.0** (separate) |
| **HieuNTg/Date-Recognition** — [GitHub](https://github.com/HieuNTg/Date-Recognition) | Expiry pipeline demo | Repo large (weights?); dataset terms absent | Pipeline code; no clear licensed dataset | **No LICENSE** (`license: null`) | **No** | UNVERIFIED | Avoid | YOLOv8 + CTC demo |
| **ameera3/OCR_Expiration_Date** — [GitHub](https://github.com/ameera3/OCR_Expiration_Date) | Dot-matrix medicine OCR research | README mentions custom/synthetic + real test sets; exact public size **UNVERIFIED** | Dot-matrix chars / some real medicine photos (README) | **No LICENSE** on repo | **No** | Low | Avoid | Useful ideas; not redistributable as-is |
| **PharmaPack** (Uni Geneva) — [project page](http://sip.unige.ch/projects/snf-200021-165672/pharmapack/) | Pharma packages (mobile) | Page claims enrollment/recognition sets; size not re-fetched (site flaky 2026-09-26) | Recognition features historically | **Academic only**; “not for any commercial usage, distribution or reproduction” (project page text, prior fetch / search) | **No** | — | **Avoid** | Registration wall; incompatible with Apache commercial OSS |
| **Mobiusi/Pharmacy-Drug-Image-Recognition-Dataset** — [HF](https://huggingface.co/datasets/Mobiusi/Pharmacy-Drug-Image-Recognition-Dataset) | Claims drug images + expiry field | Card claims “over 30,000”; viewer shows **4** rows / 2.54 MB | Structured fields including `expiry_date` (often “Unknown”) | **CC BY-NC-SA 4.0** + commercial paywall language on card | **No** (NC) | — | **Avoid** | NC + quality/credibility red flags |
| **anuragzepto/expiry-ocr** — [HF](https://huggingface.co/datasets/anuragzepto/expiry-ocr) | — | Empty (card) | — | None | No | — | Avoid | Empty stub |
| **Kaggle `nitesh31mishra/medicine-tablet-pack-image-dataset`** | Medicine packs | ~437 often cited; **UNVERIFIED** this pass (Kaggle behind bot check) | Unclear | License **UNVERIFIED**; described upstream as scraped Google Images ([11](11-models-refresh.md)) | **No** until license + provenance | UNVERIFIED | **Avoid** | Scraped origin |
| **Gong et al. retail food package dates** — doi [10.1007/s11760-020-01764-7](https://doi.org/10.1007/s11760-020-01764-7) | Food packs | Literature: ~2,424 images — **download/license UNVERIFIED** | ROI points (paper) | **UNVERIFIED** | No | — | Avoid until source found | No clear open dump found 2026-09-26 |
| **Engraved-digit / CNN-ED** MDPI Sustainability 2023 — doi [10.3390/su151712915](https://doi.org/10.3390/su151712915) | Engraved expiry digits | Paper: ~30 originals/class + GAN synth — **no public dump found** | Digit classes | Article CC BY ≠ dataset | No | — | Avoid (no dump) | Tube-seam relevant scientifically only |
| **DailyMed / openFDA / SPL media** | US label / carton panels | Large (SPL ecosystem) | Label XML; package images in submissions | Images typically **manufacturer copyright**; FDA availability ≠ PD ([NLM/FDA practice](https://dailymed.nlm.nih.gov/dailymed/about-dailymed.cfm)) | **No** (redistribute) | Latin | Avoid as fixtures | OK to link/API for identity research with ToS care — not a packdate fixture dump |
| **SynthText** (Oxford) | Synthetic scene text | Large | Syn boxes | Research / non-commercial VGG terms (not Apache) | **No** for commercial OSS redist | — | Avoid | Code Apache ≠ data terms |
| **Честный ЗНАК / МДЛП photos** | RU marked goods | **No public licensed photo dataset found** (2026-09-26) | — | — | — | Would be ideal | Gap | Consumer app / participant API ≠ open photos |

---

## Explicit Avoid list

| Item | Reason |
|---|---|
| PharmaPack (Geneva) | Academic-only; forbids commercial redistribution |
| Mobiusi Pharmacy HF dataset | CC BY-NC-SA + commercial lock; thin/odd sample |
| HF `dimun/ExpirationDate` as license authority | Tags `afl-3.0` vs official CC BY 4.0 — use official page only |
| Kaggle medicine-tablet-pack (scraped) | License + provenance unclear |
| Empty / no-LICENSE GitHub “datasets” (510-Date, HieuNTg, ameera3) | Cannot redistribute |
| DailyMed/openFDA package JPEGs as redistributed fixtures | Third-party copyright |
| SynthText / many ICDAR dumps as Apache-friendly pretrain | Restrictive or unclear commercial terms |
| Proprietary barcode API dumps mixed into OFF | LICENSING / AGENTS rule |
| Training on cloud-VLM labels without human review | Gray zone under provider ToS ([11 §5](11-models-refresh.md#5-cloud-vlm-as-an-offline-labeling-oracle-not-runtime)) |
| Assuming Честный ЗНАК screenshots are open | No clear license; likely ToS-bound |

---

## Gap analysis: what is still missing for RU medicines

| Need | Status |
|---|---|
| Large **labeled** RU/CIS medicine pack set with visible expiry + lot | **Missing.** Commons gives ~10² photos; only **12** draft positives labeled on branch |
| Stratified hard cases: embossed blister, tube seam, foil, inkjet «Годен до», rotated side panel, MFG+EXP, negatives | Partially illustrated in Commons draft labels; **no scale** |
| EAEU formats (`ММ.ГГГГ`, `ММ ГГ`, no-separator `0727`, «годен N лет» derived) | Parser string fixtures cover grammar; **photo** coverage thin |
| RU DataMatrix (01/21/91/92) in-frame with OCR date | Identity from code ≠ expiry; need photos where both appear |
| Public **Честный ЗНАК** photos with clear license | **Not found** |
| Cyrillic CIJ / thermal on curved or blister surfaces | Bottle-cap set is Latin digits only |

**Conclusion (unchanged from 03):** there is still **no large public RU packaging-expiry dataset**. packdate’s contribution path remains: own photos + Commons expand + honest stratified bench.

---

## Recommended acquisition plan (license-safe)

1. **Own photos first (milestones 2–4)**  
   Capture 40–60 medicine packs stratified per ROADMAP. Label in the local demo (confirm UI). Record provenance: photographer, date, human confirmer. Prefer CC0/CC BY if later publishing a packdate fixture set.

2. **Commons expand (scripts on `data/open-sources`)**  
   Run `commons_ru_drugs.py` outside the repo; human-confirm the 35 draft labels; add sibling categories (`Pharmaceutical product packaging` has **952** files globally — filter for Cyrillic/visible dates carefully). Keep per-file `manifest.json`. Do not commit image binaries to git.

3. **ExpDate for ROI only**  
   Download Products-Real from the **official** Drive link; attribute CC BY 4.0 + cite Seker & Ahn 2022 + KIST. Use for detector seed if milestone 4 fails the full-frame gate. Do not cite the HF `afl-3.0` mirror.

4. **Bottle-cap + Mobile-Captured Drug Packs**  
   Optional hardness / medicine-pack diversity. Attribute CC BY 4.0. Do not pretend Mobile-Captured has expiry GT.

5. **Roboflow TCC CC0 (668)**  
   Acceptable ROI seed for BR formats after a spot-check that images look original. Prefer CC0 over other Universe sets whose provenance is opaque even if UI says CC BY 4.0.

6. **OFF for identity (milestone 6)**  
   Official dumps / API with User-Agent; ODbL attribution in NOTICE; never store per-pack expiry in OFF-derived tables.

7. **Later public RU set (200–500)**  
   Publish own+confirmed Commons crops under a clear SPDX (prefer CC BY 4.0 for labels+photos you control; keep SA Commons files separate or link-only).

**Do not:** scrape Google/Yandex Images; mirror Честный ЗНАК; vendor multi-GB zips into the Apache repo; train on unreviewed cloud-VLM labels for weights you ship.

---

## Corrections vs prior research notes

| Claim | Prior | 2026-09-26 check | Action |
|---|---|---|---|
| ExpDate = **CC BY 4.0** | [11](11-models-refresh.md), ROADMAP m5, research README errata | **Confirmed** on `index_expdate.html` License section (research + commercial with attribution) | Keep |
| HF `dimun/ExpirationDate` = `afl-3.0` | 11 | **Confirmed** (HF API `license: afl-3.0`) | Keep — attribute official page only |
| Roboflow Universe licenses all **UNVERIFIED** (Cloudflare) | 11 | **Partially outdated:** several pages opened 2026-09-26; TCC set **CC0**; several others **CC BY 4.0** in UI. Provenance still unverified | Update practice: verify per dataset; still distrust scraped origin |
| Commons RU ~177 photos / 35 labels | `data/open-sources` README | Category API 122 + 99; labels JSON still **35** (12 dated) | Keep; sizes are category counts not guaranteed unique JPG filter |
| OFF Russia ~36.5k | 06 / ROADMAP | API count **36,581** | Keep |
| “No large public RU packaging expiry set” | 03 | **Still true** | Keep |
| Mobile-Captured Drug Packs | Not in prior catalog | **New** CC BY 4.0 medicine-pack photo set (no expiry GT) | Add |
| tw-drug-labels-vision | Not in prior catalog | **New** CC BY 4.0 TW leaflets — wrong task for inkjet expiry | Note only |
| ExpDate “license only citation / UNVERIFIED” | Risk if reading truncated page text | Full HTML **does** state CC BY 4.0 | Do not weaken 11’s claim |

Nothing in 10–12 was **falsified**. The main refresh is: Roboflow is no longer a blanket Cloudflare wall (for this access path), and two medicine-adjacent photo sets (Mendeley Mobile-Captured; TW leaflets) are newly catalogued with clear licenses but limited expiry fit.

---

## Sources fetched (2026-09-26)

| URL | Used for |
|---|---|
| https://felizang.github.io/expdate/index_expdate.html | ExpDate sizes + **CC BY 4.0** |
| https://huggingface.co/datasets/dimun/ExpirationDate (+ API) | Mirror `afl-3.0` |
| https://huggingface.co/datasets/aihpi/bottle-cap-date-stamps (+ API) | CC BY 4.0, 438 images |
| https://data.mendeley.com/datasets/bsmy5jjysy (+ public-api) | Mobile-Captured Drug Packs CC BY 4.0, 2000 images |
| https://universe.roboflow.com/tcc-xrqer/products-expiration-dates | CC0, 668 |
| Other Roboflow Universe URLs listed above | CC BY 4.0 UI labels |
| https://sol.sbc.org.br/index.php/eramiars/article/download/39448/39220/ | Brazilian dataset description |
| https://world.openfoodfacts.org/data | ODbL / CC-BY-SA |
| OFF API v2 search `countries_tags_en=russia` | count 36581 |
| Wikimedia Commons API `categoryinfo` / `categorymembers` | RU / packaging category sizes |
| https://textvqa.org/textocr/dataset/ | TextOCR CC BY 4.0 |
| https://huggingface.co/datasets/twinkle-ai/tw-drug-labels-vision | CC BY 4.0 leaflets |
| GitHub API: AnanasPizzaMigliore/510-Date, HieuNTg/Date-Recognition, ameera3/OCR_Expiration_Date | no SPDX |
| `origin/data/open-sources:datasets/README.md` + `commons_ru_drugs.labels.json` | Prior catalog + 35 labels |

---

## UNVERIFIED (open)

1. Exact unique image count after Commons script JPG filter (today vs 2026-09-25).
2. Image **provenance** behind Roboflow CC BY uploads (other than TCC paper’s stated supermarket capture).
3. Kaggle medicine-tablet-pack license field (page blocked).
4. PharmaPack current download terms (site timeouts).
5. Whether any ExpDate Products-Real images contain Cyrillic cues (unlikely; not sampled this pass — do not invent).
6. Gong et al. dataset public dump location/license.
7. Engraved-digit dataset public release.
