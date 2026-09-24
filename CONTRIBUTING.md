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

TBD once `pyproject.toml` and the first `extract()` land.

## License

By contributing, you agree that your contributions are licensed under the Apache License 2.0.
