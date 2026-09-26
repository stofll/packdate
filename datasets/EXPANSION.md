# Dataset acquisition shortlist

Checked 2026-09-26 against the primary pages linked below. This updates the
operational shortlist after merging the Commons/ExpDate work with research
notes [13](../docs/research/13-datasets-audit.md) and
[14](../docs/research/14-datasets-hf-sweep.md). The research notes remain dated
snapshots. Proposed priorities below are engineering judgments, not benchmark
results. New image collections have not been downloaded in this pass.

## Start with usable date labels

**First: [Preussenquelle bottle-cap date stamps](https://huggingface.co/datasets/aihpi/bottle-cap-date-stamps).**
The card declares CC BY 4.0. Reading its public `metadata.csv` on 2026-09-26
confirmed 438 rows and 1,082 semicolon-separated date labels; `num_caps` also
sums to 1,082. This adds a different surface/printing condition to ExpDate.
The labels describe printed dates, not medicine semantics. Some photos contain
multiple caps, so the evaluator needs per-image lists of expected dates instead
of the existing single-date sidecar contract. The card says labels were initially
VLM-generated and flagged cases were human-corrected; do not describe every label
as independently human-confirmed. Keep the capture batches separate when
designing train/test splits. The upstream `train` name alone is not a held-out
test guarantee.

Metadata count can be reproduced with the standard library (no image download):

```python
import csv
import io
from urllib.request import urlopen

url = "https://huggingface.co/datasets/aihpi/bottle-cap-date-stamps/resolve/main/metadata.csv"
with urlopen(url, timeout=30) as response:
    rows = list(csv.DictReader(io.StringIO(response.read().decode("utf-8-sig"))))
print(len(rows), sum(int(row["num_caps"]) for row in rows))
print(sum(len(row["label"].split(";")) for row in rows))
```

**Second: [Food Packaging OCR, version 2](https://data.mendeley.com/datasets/3cpx2fmn3r/2).**
The source declares CC BY 4.0 and detection/recognition annotations that include
validity-period text. This is promising for whole-package text and cue/date
association. The exact image count, number of expiry examples, and date-field
schema remain unverified here. The public API request returned HTTP 403 in this
pass, while the dataset page was readable. Do not turn the archive size reported
in research note 14 into an image-count estimate. Inspect the `det` and `rec`
labels and a representative sample before writing an adapter; validity-period
text can describe relative shelf life rather than an explicit printed expiry.

## Expand medicine coverage with labeling

| Source | Source-reported coverage | Required work |
|---|---|---|
| [Mobile-Captured Pharmaceutical Medication Packages v1](https://data.mendeley.com/datasets/bjy2svvmn8/1) | 3,900 photos, 150 packages; 26 photos per package; CC BY 4.0 | Sample for legible expiry, record negatives and manually label dates. Split by package, not by photo. |
| [Mobile-Captured Drug Packs v3](https://data.mendeley.com/datasets/bsmy5jjysy/3) | 2,000 photos, 166 packages; CC BY 4.0 | Inspect content and any supplied annotations. Treat as an unlabeled pool until expiry ground truth is established. |
| [Commons pharmaceutical product packaging](https://commons.wikimedia.org/wiki/Category:Pharmaceutical_product_packaging) and [blister packs](https://commons.wikimedia.org/wiki/Category:Blister_packs) | Expansion leads from research note 14; current usable count not reverified | Reuse the existing downloader's provenance approach, verify each file's license, filter for visible dates/Cyrillic, then review labels. |

The Mendeley counts are from dataset descriptions, not local archive counts.
Neither description establishes a ready-to-score expiry transcription set.
Overlap between these two collections and existing material has not been
checked; their counts must not be added as unique new benchmark examples.
Larger photo pools still need readable-date selection, negative examples and
human confirmation to advance the medicine milestones.

## Detection candidates, after the benchmark justifies ROI work

| Source | Page snapshot | Limitation |
|---|---|---|
| [TCC products-expiration-dates](https://universe.roboflow.com/tcc-xrqer/products-expiration-dates) | 668 images; date/code/prod/due classes; [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) link | The authors describe Brazilian home/supermarket capture and roughly 10% background images. Verify exported annotations and provenance; boxes alone do not supply ISO truth. |
| [area-expiry-date](https://universe.roboflow.com/expiry-date/area-expiry-date) | 4,480 images; CC BY 4.0; 73 listed classes | Classes mix region labels, numbers and cue words; the page has no project description. Audit the schema, duplicates, augmented copies and source rights before treating it as additional independent data. |

The page sizes are reported upstream; no image export was counted here.
The second set's large headline count does not establish 4,480 independent,
fully transcribed expiry photographs. Neither set requires an Ultralytics
runtime dependency merely to inspect its annotations.

## Acquisition order and acceptance checks

1. Build a bottle-cap importer/evaluator with multiple expected dates and label
   provenance; keep OCR reading scores separate from expiry-selection scores.
2. Inspect Food Packaging OCR's actual labels before committing to a full run.
3. Sample the medicine pools and confirm useful cases, prioritizing Cyrillic,
   foil, embossing, MFG+EXP and negatives over near-duplicate views.
4. Consider detection sets only after comparing full-frame and recognition-only
   crop baselines. The [ExpDate experiment](../docs/benchmarks/expdate-2026-09-26.md)
   does not establish the benefit of a learned ROI detector.

For every accepted source, store downloads outside Git and record dataset
revision, source URL, creator, license, original split, package/group identity,
file hashes and annotation provenance. Check exact and near duplicates across
sources before splitting; keep all views/crops of a package together. Report
metrics separately by source, domain and surface. Preserve an untouched test
partition before tuning models or parser rules.

For CC BY 4.0 sources, the [license deed](https://creativecommons.org/licenses/by/4.0/)
requires credit, a license link and an indication of changes when sharing.
Third-party data retains its own terms; it does not become Apache-2.0 because
packdate code is Apache-2.0. Sources with missing licenses, NC restrictions or
unresolved provenance stay out of redistributed fixtures pending clarification.
