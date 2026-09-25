# Research archive

Snapshot of background research that shaped **packdate** (cut date **2026-09-25**).  
These notes are historical context, not runtime docs. Normative decisions live in [`../ARCHITECTURE.md`](../ARCHITECTURE.md).

| Doc | Contents |
|-----|----------|
| [01-ocr-expiry.md](01-ocr-expiry.md) | Deep dive: expiry OCR pipelines, papers, OSS gaps |
| [02-full-report.md](02-full-report.md) | Combined report: OCR + barcodes + MVP for an OSS repo |
| [03-ocr-verdict.md](03-ocr-verdict.md) | Second-pass verdict: HF / SOTA vs “already solved?” |
| [04-ocr-gaps.md](04-ocr-gaps.md) | Why general OCR ≠ expiry tracker |
| [05-ocr-sota-notes.md](05-ocr-sota-notes.md) | Short SOTA notes |
| [06-barcode-and-open-data.md](06-barcode-and-open-data.md) | OFF and barcode stack |
| [07-reference-projects.md](07-reference-projects.md) | Reference repos and roadmap |
| [08-dependencies-shortlist.md](08-dependencies-shortlist.md) | What to depend on / avoid |
| [09-ocr-models-license-audit.md](09-ocr-models-license-audit.md) | Deep OCR/VLM license audit (code vs weights, 2026-09-25) |
| [10-medicine-vs-food.md](10-medicine-vs-food.md) | First domain: RU/EU/US DataMatrix contents, printed date rules for drugs vs food, decoders |
| [11-models-refresh.md](11-models-refresh.md) | Gaps after 09: on-device Cyrillic OCR, ExpDate license, 2026 small VLMs, labeling-oracle terms |
| [12-post-recognition.md](12-post-recognition.md) | After OCR: date-semantics edge cases, pantry app data models, HITL confirm, storage, reminders |
| [13-datasets-audit.md](13-datasets-audit.md) | Open datasets license audit for medicine-first fixtures / ExpDate / Commons / OFF (2026-09-26) |
| [14-datasets-hf-sweep.md](14-datasets-hf-sweep.md) | Wide HF-first dataset sweep: all hits incl. empty/NC/non-RU; Food Packaging OCR; RF area-expiry 4480; Mendeley 3900 packs (2026-09-26) |

**License of this folder:** same as the repository (Apache-2.0). Linked third-party projects keep their own licenses; datasets may use ODbL/CC — check before redistributing.

## Errata and later checks

The notes above are kept as written. Checked against upstream on 2026-09-25 when revising the roadmap:

- **Qwen2.5-VL license.** `03-ocr-verdict.md` and `08-dependencies-shortlist.md` list Qwen2.5-VL as research/NC, while `05-ocr-sota-notes.md` recommends Qwen2.5-VL-7B. Each size has its own license: the 7B-Instruct model card says Apache-2.0, other sizes use Qwen's own licenses. Check the card for each size.
- **RF-DETR license by size.** Apache-2.0 covers the N/S/M/L sizes only. XL/2XL (`rfdetr_plus`) use PML 1.0. The canonical repo is `github.com/roboflow/rf-detr`; the `rfdetr` URL used in 01/02 redirects there.
- **PP-OCRv6 exists.** It shipped in PaddleOCR v3.7.0 (2026-06-11), and PaddleOCR-VL-1.6 shipped in v3.6.0. Official PP-OCRv6 docs: unified model covers CN/EN/JA + Latin — **not Cyrillic**. Keep `cyrillic_PP-OCRv5_mobile_rec` for RU (see [09](09-ocr-models-license-audit.md)).
- **OFF rate limits are confirmed.** Product reads: 15 req/min per IP. Search: 10 req/min. A custom User-Agent is required.
- **Roadmap direction.** 02/07 propose an app-first path: barcode plus a manual date, with no OCR. The repo takes the library-first, parse-first path instead. See [`../../ROADMAP.md`](../../ROADMAP.md#decisions-behind-this-plan).
- **Sample sizes differ across notes.** They range from 30 golden images to 40–60 bench photos to 50–100 smoke photos. Normalized in the roadmap: ~30 golden fixtures for v0.1 and 40–60 stratified photos for the bench gate.
- **Qwen2.5-VL per size (deep audit 2026-09-25).** Confirmed from HF cards/LICENSE files: **3B** = `qwen-research` (non-commercial); **7B** = Apache-2.0; **72B** = Qwen LICENSE AGREEMENT (conditional; >100M MAU needs separate license). Blanket “Qwen2.5-VL is NC” is false. See [09-ocr-models-license-audit.md](09-ocr-models-license-audit.md).
- **PP-OCRv6 language coverage.** Official docs: unified model = Simplified/Traditional Chinese, English, Japanese, + Latin scripts — **not Cyrillic**. Keep `cyrillic_PP-OCRv5_mobile_rec` for RU. Industrial/dot-matrix improvements in v6 are documented.
- **MinerU license moved.** Current master uses Apache-2.0–based MinerU Open Source License with MAU/revenue thresholds (not blanket AGPL). Older releases may still be AGPL.
- **TrOCR weights SPDX.** `microsoft/trocr-base-printed` HF card has no `license:` field; unilm code is MIT. Treat weights as UNVERIFIED until clarified.
- **olmOCR / DeepSeek-OCR.** Apache-2.0 / MIT respectively — license OK; still document-biased for packaging dates (bench-only, not license-avoid).
- **Repo layout in 02 is Dart/Flutter** (`packages/…`). It was superseded by the Python layout in [`../ARCHITECTURE.md`](../ARCHITECTURE.md).

Added with notes 10–12 (2026-09-25):

- **ML Kit OCR has no Cyrillic.** 01/02 suggest ML Kit text recognition for an Android demo; the official v2 languages page lists no Russian. Keep ML Kit for barcodes only. See [11](11-models-refresh.md).
- **ExpDate license is CC BY 4.0** per the official dataset page; the HF mirror `dimun/ExpirationDate` says `afl-3.0`. Attribute via the official page. The roadmap's "confirm ExpDate license" item is resolved. See [11](11-models-refresh.md).
- **Gemma 4 is Apache-2.0** (Gemma 1–3 / 3n use the Gemma license). New permissive VLM candidates: GLM-OCR (MIT), Qwen3.5-0.8B/2B, MiniCPM-V-4.6. Avoid Moondream 3.x and LFM-VL. See [11](11-models-refresh.md).
- **Russian DataMatrix codes carry no expiry.** 06 says a barcode never gives per-pack expiry; that holds for EAN/UPC and RU marking codes, but EU FMD / US DSCSA drug DataMatrix codes do include AI (17) expiry. See [10](10-medicine-vs-food.md).
- **«Употребить до» ≠ EU "use by".** Under ТР ТС 022 it is a synonym of «годен до». The old roadmap's `kind=use_by` for RU cues is dropped. See [12](12-post-recognition.md).

Added with note 13 (2026-09-26):

- **ExpDate CC BY 4.0 re-confirmed** on the official dataset page License section; HF mirror `dimun/ExpirationDate` remains mistagged `afl-3.0`. See [13](13-datasets-audit.md).
- **Roboflow Universe is no longer a blanket Cloudflare wall** (for this access path). TCC `products-expiration-dates` shows **CC0**; several other expiry sets show **CC BY 4.0** in the UI. Image provenance is still uploader-declared — treat as Conditional. See [13](13-datasets-audit.md).
- **New medicine-pack photo set:** Mobile-Captured Drug Packs (Mendeley, CC BY 4.0, 2,000 images) — no expiry transcriptions. See [13](13-datasets-audit.md).
- **Still no large labeled RU packaging-expiry dataset.** Commons + own photos remain the acquisition path for Cyrillic medicines.

Added with note 14 (2026-09-26):

- **Wide sweep beyond [13](13-datasets-audit.md):** Hugging Face has almost no usable pack-expiry datasets (`срок годности` / `годен` → 0). Material new finds are mostly **off-HF**: Mendeley Food Packaging OCR (CC BY 4.0, validity-period annotations, ~2.56 GB zip), second Mobile-Captured pharma set (`bjy2svvmn8`, 3,900 images, CC BY 4.0), Roboflow `area-expiry-date` (**4,480**, CC BY 4.0), Zenodo HalalBench / Bilingual Food Labels. See [14](14-datasets-hf-sweep.md).
- **HF surprises:** gated `VietMedTeam/Expired-Food-Items` (401); empty-card `jojogo9/expiration_date` (~662 MB zips); license-less `ABINSHA/blister_data` (683 batch/med pairs); Italian OTC packs Apache-2.0 (identity, not inkjet EXP).
- **Still no large labeled RU packaging-expiry dataset** after the broader net.

