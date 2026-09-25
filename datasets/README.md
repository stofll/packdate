# Datasets

Scripts and license notes. No photos or weights are redistributed from this repo; scripts download them into a folder you choose (keep it outside the repo).

## Open sources (checked 2026-09-25)

| Source | What | License | Size | Expiry labels |
|---|---|---|---|---|
| Wikimedia Commons: `Category:Pharmaceutical drugs of Russia` + `Category:Photographs by Retired electrician/medical` | 177 photos of Russian-market medicine packs | per file: 100 CC0, 68 CC BY-SA 4.0, 5 CC BY, 4 public domain | 64 MB as 1280 px thumbnails | 35 labeled here (`commons_ru_drugs.labels.json`), see below |
| [ExpDate](https://felizang.github.io/expdate/index_expdate.html) `Products-Real` (KIST) | 1,767 food / drink / pharma packs; test split (665) has `exp`-class boxes with transcriptions | CC BY 4.0 (official page; the HF mirror `dimun/ExpirationDate` says `afl-3.0` — attribute the source) | 630 MB | yes, non-RU formats |
| [aihpi/bottle-cap-date-stamps](https://huggingface.co/datasets/aihpi/bottle-cap-date-stamps) | 438 inkjet date stamps on curved aluminium caps | CC BY 4.0 | 828 MB | yes (`metadata.csv`) |

Not usable yet: Roboflow Universe datasets (license pages behind a Cloudflare check, **unverified**); Kaggle `medicine-tablet-pack-image-dataset` (scraped from Google Images, license unclear).

## Commons medicine photos

```bash
python datasets/commons_ru_drugs.py D:/packdate-data/commons-ru-drugs   # images + manifest.json + label sidecars
python datasets/prelabel.py D:/packdate-data/commons-ru-drugs/images    # draft labels for the rest
python apps/demo/evaluate.py D:/packdate-data/commons-ru-drugs/images   # scores labeled photos only
```

`manifest.json` keeps title, license, author and source URL per photo: keep it for attribution when you share results or images.

`commons_ru_drugs.labels.json` holds 35 labels (12 with an expiry, 23 negatives or multi-item) keyed by Commons file title. They were read from the photos by Claude during a visual review on 2026-09-25 and **have not been confirmed by a person yet**. Photos where the date was not legible at 1280 px were left unlabeled.

### Measured here

Script `apps/demo/evaluate.py`, backend `rapidocr/cyrillic_PP-OCRv5_mobile`, the 35 labeled photos above, 2026-09-25. Too few photos for accuracy claims; use it to find failure types.

| Parser version | Exact on 12 with a date | False on committed | Negatives abstained |
|---|---|---|---|
| before no-separator dates (`parse/medicine-dates`) | 3 | 1 of 4 | 22 of 22 |
| after (`data/open-sources`) | 6 | 1 of 7 | 22 of 22 |

Remaining misses: embossed tube seam (OCR), rotated side-panel cue (OCR), embossed blister date with no cue in frame, sticker `09 28` with no cue, shelf life derived from the manufacture date. The one false date is a photo of two items with different dates.
