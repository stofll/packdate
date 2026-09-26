# Datasets

Scripts and license notes. No photos or weights are redistributed from this repo; scripts download them into a folder you choose (keep it outside the repo).

## Open sources (checked 2026-09-25)

| Source | What | License | Size | Expiry labels |
|---|---|---|---|---|
| Wikimedia Commons: `Category:Pharmaceutical drugs of Russia` + `Category:Photographs by Retired electrician/medical` | 177 photos of Russian-market medicine packs | per file: 100 CC0, 68 CC BY-SA 4.0, 5 CC BY, 4 public domain | 64 MB as 1280 px thumbnails | 35 labeled here (`commons_ru_drugs.labels.json`), see below |
| [ExpDate](https://felizang.github.io/expdate/index_expdate.html) `Products-Real` (KIST) | 1,767 food / drink / pharma packs; test split (665) has `exp`-class boxes with transcriptions | CC BY 4.0 (official page; the HF mirror `dimun/ExpirationDate` says `afl-3.0` — attribute the source) | 630 MB | yes, non-RU formats |
| [aihpi/bottle-cap-date-stamps](https://huggingface.co/datasets/aihpi/bottle-cap-date-stamps) | 438 inkjet date stamps on curved aluminium caps | CC BY 4.0 | 828 MB | yes (`metadata.csv`) |

Not usable yet: Roboflow Universe datasets (license pages behind a Cloudflare check, **unverified**); Kaggle `medicine-tablet-pack-image-dataset` (scraped from Google Images, license unclear).

### Local ExpDate download (checked 2026-09-26)

`Products-Real.zip` was inspected locally: SHA-256 `31dff6e0045ab6f4683c9e20b5dd04fedd751c174b681193744a013637e38da6`, 660,701,583 bytes. It contains 1,102 training JPEGs, 665 evaluation JPEGs, and an `annotations.json` file for each split. Every image has an annotation entry; the ZIP CRC check passed. These checks establish the contents of the local archive, but there is no upstream checksum here to prove byte-for-byte identity with the official download.

The [official ExpDate page](https://felizang.github.io/expdate/index_expdate.html) provides the download link and licenses the dataset under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Redistribution requires credit to the creators, a license link, and an indication of changes. The page asks users to cite Seker and Ahn's associated publication and acknowledge the Korea Institute of Science and Technology (KIST). The local archive has no bundled license or provenance file, so use the official page for these terms. We keep the archive and photos outside Git: the ZIP exceeds [GitHub's 100 MiB single-file limit](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) and the full image set would make the source repository much larger. For experiments, download it from the official page to a directory outside this repository.

## Evaluate the downloaded ExpDate archive

`evaluate_expdate.py` reads `Products-Real.zip` directly, without extracting or
redistributing its images. Install the existing `ocr` extra and run from the
repository root:

```bash
python datasets/evaluate_expdate.py /path/to/Products-Real.zip --oracle-crops --out /path/to/results/cyrillic.json
```

For this Windows checkout, the equivalent command using the local environment is:

```powershell
$env:PYTHONPATH = "src"
.venv/Scripts/python.exe datasets/evaluate_expdate.py Products-Real.zip --oracle-crops --out D:/packdate-data/expdate/cyrillic.json
```

Use `--limit 10` for a smoke test only, `--lang eslav` for the alternate
recognizer, and omit `--oracle-crops` for full-frame OCR alone. The optional
crop experiment uses upstream expiry boxes plus eight pixels of padding and
the same OCR detector and recognizer. It measures this crop procedure, not a
trained ROI detector or a recognition-only upper bound.

The report separates:

- **OCR transcription presence:** the annotated date appears in OCR lines
  overlapping its box (intersection / smaller box area >= 0.5). Case, spacing,
  and punctuation are ignored; letters are never changed to digits. This is
  normalized transcription matching, not character error rate or ISO accuracy.
- **Printed ISO agreement:** the pipeline's committed `iso_date`, including
  day/month precision, agrees with the upstream DMY components. Labels with
  missing year/month, inconsistent component text, or invalid calendar dates
  are excluded and counted explicitly. Two-digit label years mean 20YY.
- **Abstention and errors:** abstentions remain in the scored denominator;
  inference/data errors are listed separately and cause a nonzero exit code.
  Missing labels never become negative examples.

The evaluator does not inject EXP cues, use annotations as runtime input to the
full-frame pipeline, or decode barcodes. It does not score `valid_through`:
ExpDate mixes product domains, and medicine end-of-month semantics cannot be
assumed for all its labels. Upstream DMY labels are not independently confirmed
ground truth; short-year order can remain ambiguous even when the component
transcriptions agree. This diagnostic does not replace the medicine/negative
fixtures or the milestone 4 gate.

Reports checkpoint every 25 images and include `complete`, per-image OCR,
pipeline results, model/configuration details, package versions, source hashes,
and archive/annotation/image hashes. Keep full reports outside Git. To isolate
a parser change without running OCR again:

```bash
python datasets/evaluate_expdate.py /path/to/results/cyrillic.json --reparse --out /path/to/results/cyrillic-reparsed.json
```

Replay requires a completed report and preserves original OCR provenance and
timing; its `reparse` section records the new parser hashes. Result bounding
boxes are not rebuilt during text-only replay. Metric tests use synthetic
annotations in `tests/test_evaluate_expdate.py` and require no model downloads.

The [2026-09-26 diagnostic report](../docs/benchmarks/expdate-2026-09-26.md)
records the full evaluation run, parser before/after comparison, and remaining
limitations. Its counts are not a medicine accuracy claim.

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
