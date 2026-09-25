# packdate

Experimental open-source pipeline for reading **expiration / best-before dates** from product packaging photos, with an optional barcode → product lookup path.

> **Not a drop-in 99% field OCR.** Assist + human confirm. Lab numbers on public benchmarks do not equal fridge-photo accuracy.

## Status

| Milestone | State |
|-----------|--------|
| Repo scaffold + research archive | **Done** |
| Date parser (`parse/`), medicines first | v0.0.x in progress — [policy](docs/PARSER.md) |
| `extract()` v0.1 (full-frame OCR + DataMatrix + CLI) | Code in progress; waiting for golden photos |
| Local web demo (upload → confirm → list) | Planned |
| Bench gate on stratified photos | Planned |
| ROI detector (if the bench needs it) / food + barcode + OFF | Later |

See the full staged plan in [ROADMAP.md](ROADMAP.md). Architecture decisions live in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Why this exists

General OCR (PaddleOCR, doc VLMs, etc.) is strong in 2025–2026. **Expiry-on-packaging** is still an application layer: find the date ROI, OCR the crop, parse many formats, tell *use-by* from *manufactured*, abstain when unsure.

There is no mature permissive “expiry E2E” library on Hugging Face. This repo aims at that gap: parsers, RU/EN cues, honest benchmarks, and a small packaging dataset — not another thin YOLO wrapper.

## Planned pipeline

```text
image
  → optional DataMatrix decode (GS1 AI 17 expiry on EU/US drug packs; GTIN + serial otherwise)
  → optional date ROI detector
  → OCR (default: PP-OCRv5 + Cyrillic rec model; optional extra)
  → parse + disambiguate (годен до / EXP / MFG / Серия / …) + date rules
  → { iso_date, precision, valid_through, rule_id, kind, confidence, candidates, abstain_reason, bboxes }
  → UI / caller confirms when confidence is low
```

The first target domain is **medicines** (EAEU packs), where the printed date format is regulated; food comes later. See [ROADMAP](ROADMAP.md#decisions-behind-this-plan).

Barcode is a **separate** module. EAN/UPC gives identity via Open Food Facts (or local cache), never the expiry of that physical unit. Russian marking DataMatrix codes carry GTIN + serial but no expiry; EU/US drug DataMatrix codes do carry it (GS1 AI 17).

## Install

Not published to PyPI yet. From a clone:

```bash
pip install -e .                    # parser only, no dependencies
pip install -e ".[ocr,barcode]"     # + RapidOCR (Cyrillic PP-OCRv5) and DataMatrix decoding
```

RapidOCR downloads its ONNX models on first run.

```bash
python apps/demo/cli.py photo.jpg --text
```

```python
from packdate.pipeline import extract
from packdate.parse import parse_text

extract("photo.jpg").to_dict()        # needs the extras
parse_text("Годен до: 06.2027").to_dict()  # stdlib only
```

## License

[Apache License 2.0](LICENSE) — see also [NOTICE](NOTICE).

## Docs

- [Roadmap](ROADMAP.md)
- [AGENTS.md](AGENTS.md) (repo rules + verification policy for contributors and coding agents)
- [Architecture](docs/ARCHITECTURE.md)
- [Contributing](CONTRIBUTING.md)
- [Research archive](docs/research/README.md) (libraries, papers, reference projects, OCR verdict)

## Scope

- **In scope:** packaging date reading, date parsing, optional barcode+OFF identity, inventory-friendly outputs.
- **Out of scope (v0):** claiming industrial line accuracy, replacing Cognex/Keyence, shipping proprietary barcode DB mirrors.
