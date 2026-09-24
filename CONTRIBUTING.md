# Contributing

Thanks for considering a contribution.

## Good first issues

- New date format regex + unit test fixture
- RU/EN cue words (`годен до`, `употребить до`, `best before`, …)
- Anonymized date crop + `expected.json` under `tests/fixtures/` (no faces / PII)

## Rules

1. Do not submit bulk AI-generated parsers without fixtures.
2. Do not vendor datasets or weights whose license is unclear.
3. Keep barcode and expiry modules separate.
4. Prefer failing closed (abstain) over a guessed date.

## Where we are

See [ROADMAP.md](ROADMAP.md) for the current milestone and good first targets (parser formats and fixtures first).

## Dev setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Tests live under `tests/` and arrive with the parser (roadmap milestone 1). The parser must stay stdlib-only; OCR backends go into optional extras.

## License

By contributing, you agree that your contributions are licensed under the Apache License 2.0.
