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

**License of this folder:** same as the repository (Apache-2.0). Linked third-party projects keep their own licenses; datasets may use ODbL/CC — check before redistributing.

## Errata and later checks

The notes above are kept as written. Checked against upstream on 2026-09-25 when revising the roadmap:

- **Qwen2.5-VL license.** `03-ocr-verdict.md` and `08-dependencies-shortlist.md` list Qwen2.5-VL as research/NC, while `05-ocr-sota-notes.md` recommends Qwen2.5-VL-7B. Each size has its own license: the 7B-Instruct model card says Apache-2.0, other sizes use Qwen's own licenses. Check the card for each size.
- **RF-DETR license by size.** Apache-2.0 covers the N/S/M/L sizes only. XL/2XL (`rfdetr_plus`) use PML 1.0. The canonical repo is `github.com/roboflow/rf-detr`; the `rfdetr` URL used in 01/02 redirects there.
- **PP-OCRv6 exists.** It shipped in PaddleOCR v3.7.0 (2026-06-11), and PaddleOCR-VL-1.6 shipped in v3.6.0. Cyrillic coverage in v6 still needs checking. Until then, `cyrillic_PP-OCRv5_mobile_rec` is the known Cyrillic model.
- **OFF rate limits are confirmed.** Product reads: 15 req/min per IP. Search: 10 req/min. A custom User-Agent is required.
- **Roadmap direction.** 02/07 propose an app-first path: barcode plus a manual date, with no OCR. The repo takes the library-first, parse-first path instead. See [`../../ROADMAP.md`](../../ROADMAP.md#decisions-behind-this-plan).
- **Sample sizes differ across notes.** They range from 30 golden images to 40–60 bench photos to 50–100 smoke photos. Normalized in the roadmap: ~30 golden fixtures for v0.1 and 40–60 stratified photos for the bench gate.
- **Repo layout in 02 is Dart/Flutter** (`packages/…`). It was superseded by the Python layout in [`../ARCHITECTURE.md`](../ARCHITECTURE.md).
