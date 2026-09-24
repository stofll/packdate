# packdate

Experimental open-source pipeline for reading **expiration / best-before dates** from product packaging photos, with an optional barcode → product lookup path.

> **Not a drop-in 99% field OCR.** Assist + human confirm. Lab numbers on public benchmarks do not equal fridge-photo accuracy.

## Why this exists

General OCR (PaddleOCR, doc VLMs, etc.) is strong in 2025–2026. **Expiry-on-packaging** is still an application layer: find the date ROI, OCR the crop, parse many formats, tell *use-by* from *manufactured*, abstain when unsure.

There is no mature permissive “expiry E2E” library on Hugging Face. This repo aims at that gap: parsers, RU/EN cues, honest benchmarks, and a small packaging dataset — not another thin YOLO wrapper.

## Planned pipeline

```text
image
  → optional date ROI detector
  → OCR (default: PP-OCR + Cyrillic where needed)
  → parse + disambiguate (EXP / BB / MFG / годен до / …)
  → { iso_date, kind, confidence, candidates, bboxes }
  → UI / caller confirms when confidence is low
```

Barcode (EAN/UPC) is a **separate** module: identity via Open Food Facts (or local cache). A barcode does **not** give the expiry of that physical unit.

## Status

Scaffold / research-backed foundation. Implementation of `extract()` comes next.

## License

[Apache License 2.0](LICENSE) — see also [NOTICE](NOTICE).

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Contributing](CONTRIBUTING.md)
- [Research archive](docs/research/README.md) (libraries, papers, reference projects, OCR verdict)
- Key decisions: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## Name & scope

- **In scope:** packaging date reading, date parsing, optional barcode+OFF identity, inventory-friendly outputs.
- **Out of scope (v0):** claiming industrial line accuracy, replacing Cognex/Keyence, shipping proprietary barcode DB mirrors.
