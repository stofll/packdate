# Golden photo fixtures

One photo + one label per case:

```text
tests/fixtures/<name>.jpg
tests/fixtures/<name>.json   {"valid_through": "2027-06-30", "stratum": "box_print", "notes": ""}
```

- `valid_through`: last good day as a human reads it from the pack, or `null` for a negative (no readable expiry).
- `stratum`: `box_print`, `embossed_blister`, `tube_seam`, `foil_blister`, `multi_date`, `negative`.
- Label provenance: labeled by a person; if a tool pre-labeled it, say which in `notes` (docs/research/11 §5).

Only commit photos with no faces, names, addresses, prescriptions or pharmacy receipts. Private photo sets stay outside the repo; score them with:

```bash
python apps/demo/evaluate.py path/to/photos --out report.json
```
