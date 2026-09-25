# Datasets

Scripts and license notes. **No photos or weights are redistributed from this repo** by default; download into a folder you choose (keep it outside the tree).

Normative audit: [`docs/research/13-datasets-audit.md`](../docs/research/13-datasets-audit.md) (access date **2026-09-26**). Domain notes: [10](../docs/research/10-medicine-vs-food.md), ExpDate license: [11](../docs/research/11-models-refresh.md), OFF: [06](../docs/research/06-barcode-and-open-data.md).

## Branch `data/open-sources`

Download helpers and draft Commons labels live on branch **`data/open-sources`** (not on `main` yet):

| Path on branch | Role |
|---|---|
| `datasets/commons_ru_drugs.py` | Download Commons RU medicine thumbs + `manifest.json` |
| `datasets/commons_ru_drugs.labels.json` | 35 draft labels (12 with date) — **not human-confirmed** |
| `datasets/prelabel.py` | Draft labels for unlabeled photos |
| `datasets/README.md` | Catalog snapshot checked **2026-09-25** |

```bash
git fetch origin data/open-sources
git show origin/data/open-sources:datasets/commons_ru_drugs.py > /tmp/commons_ru_drugs.py
# python /tmp/commons_ru_drugs.py /path/outside/repo/commons-ru-drugs
```

## Open sources (re-verified 2026-09-26)

| Source | What | License | Size (upstream) | Expiry labels | packdate fit |
|---|---|---|---|---|---|
| Wikimedia Commons: `Pharmaceutical drugs of Russia` + `Photographs by Retired electrician/medical` | RU-market medicine pack photos | Per file (CC0 / CC BY / CC BY-SA / PD) | ~177 JPG/PNG (branch 2026-09-25); categories 122 + 99 files (API 2026-09-26) | 35 draft on branch (12 dated) | Golden / OCR bench (Cyrillic) |
| [ExpDate](https://felizang.github.io/expdate/index_expdate.html) Products-Real (KIST) | Food / drink / pharma packs | **CC BY 4.0** (official page) | 1,767 real (1102 / 665) | Boxes + transcriptions; test `exp` | ROI seed; non-RU OCR bench |
| HF mirror [`dimun/ExpirationDate`](https://huggingface.co/datasets/dimun/ExpirationDate) | Same files | Tagged **`afl-3.0`** — **mismatch** | — | — | Attribute **official** page only |
| [`aihpi/bottle-cap-date-stamps`](https://huggingface.co/datasets/aihpi/bottle-cap-date-stamps) | Inkjet dates on aluminium caps | **CC BY 4.0** | 438 images | Yes (`metadata.csv`) | OCR hardness (not medicine) |
| [Mobile-Captured Drug Packs](https://doi.org/10.17632/bsmy5jjysy.3) (Mendeley) | Phone photos of drug packs | **CC BY 4.0** | 2,000 images / 166 packs | **No** expiry GT | Medicine pack diversity |
| [Roboflow TCC products-expiration-dates](https://universe.roboflow.com/tcc-xrqer/products-expiration-dates) | BR supermarket packs | **CC0 1.0** (Universe UI 2026-09-26) | 668 | Detection boxes (date/code/prod/due) | ROI seed; provenance uploader-declared |
| Other Roboflow expiry sets listed in [13](../docs/research/13-datasets-audit.md) | Detection | Mostly **CC BY 4.0** in UI | Varies | Boxes | Conditional — provenance opaque |
| [Open Food Facts](https://world.openfoodfacts.org/data) | Product DB + pack photos | ODbL + DbCL; images CC-BY-SA | Russia products ≈ 36.5k (API) | N/A (not per-pack expiry) | **Identity only** |
| [TextOCR](https://textvqa.org/textocr/dataset/) | Scene text | Annotations CC BY 4.0; OpenImages images separate | ~28k images | Word boxes | Weak pretrain only |

### Avoid / do not vendor

- Kaggle `medicine-tablet-pack-image-dataset` — scraped; license **UNVERIFIED**
- PharmaPack (Uni Geneva) — academic / no commercial redistribution
- Mobiusi Pharmacy HF — NC
- GitHub date demos without LICENSE (`510-Date`, `HieuNTg/Date-Recognition`, …)
- DailyMed / openFDA package JPEGs as redistributed fixtures
- Empty HF stubs (`anuragzepto/expiry-ocr`)

## Attribution checklist

When you share results or publish fixtures derived from third-party images:

1. Keep Commons `manifest.json` (title, license, author, source URL).
2. Cite ExpDate: Seker & Ahn, *Expert Systems with Applications* 2022; acknowledge KIST; link CC BY 4.0.
3. OFF: ODbL attribution string from the [data page](https://world.openfoodfacts.org/data); do not mix proprietary barcode dumps.
4. Record label provenance on packdate fixtures (human vs draft VLM).

## Gap

There is still **no large public labeled RU/CIS medicine expiry photo set**. Plan: own photos + Commons expand + optional ExpDate ROI — see [13 § acquisition](../docs/research/13-datasets-audit.md#recommended-acquisition-plan-license-safe) and ROADMAP milestones 2 / 4 / 5 / Later.
