# Demo apps

Planned (see [ROADMAP](../../ROADMAP.md) milestones 2–3):

- **CLI** (`cli.py`) — run `extract()` on photos and print one JSON object per photo: `python apps/demo/cli.py photo.jpg [--lang eslav] [--no-codes] [--text]`.
- **Evaluate** (`evaluate.py`) — score a folder of labeled photos (format in [tests/fixtures/README.md](../../tests/fixtures/README.md)): `python apps/demo/evaluate.py photos/ --out report.json`.
- **Local web site** — upload a photo, confirm or correct the date, keep a medicine-cabinet list in SQLite, export corrections as fixtures. Local only; photos never leave the machine.

The demo has its own dependencies and must not bloat the core `packdate` package.
