# AGENTS.md

Instructions for coding agents and humans editing **packdate**.
Human contributor summary: [CONTRIBUTING.md](CONTRIBUTING.md). Product plan: [ROADMAP.md](ROADMAP.md).

## Mission (do not redefine)

packdate is an **Apache-2.0** library-shaped pipeline for reading **expiration / best-before dates** from packaging photos, plus an optional **barcode → product identity** path. It is assist + confirm, not a claim of industrial field OCR.

Barcode ≠ per-pack expiry. Keep those modules separate.

Core install stays dependency-light; OCR / detector / barcode are optional extras (see ROADMAP decisions).

## Source of truth

| Topic | Read first |
|-------|------------|
| Milestones | [ROADMAP.md](ROADMAP.md) |
| Pipeline / deps / bench gates | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| License / OFF / patents | [docs/LICENSING.md](docs/LICENSING.md), [NOTICE](NOTICE) |
| Research notes (historical) | [docs/research/](docs/research/) |

If a chat suggestion conflicts with these files, **follow the repo files** unless the maintainer explicitly changes them in the same change set.

## Verification of information (mandatory)

Any claim that enters the repo — in docs, README, research notes, PR descriptions, issue comments you draft, commit messages that state facts, or code comments that cite numbers — must be **checkable**.

1. **No invented facts.** Do not fabricate metrics, dataset sizes, model scores, paper titles, URLs, license texts, API behaviors, or “we measured X%” results. If you do not have the source or a reproducible command/output in this repo, say so and mark the statement as unknown / TODO.
2. **Cite or show how to reproduce.** Prefer a primary link (paper, model card, LICENSE file, commit, CLI output saved under `docs/` or CI) over memory. For numbers from our own runs, point at the script + fixture set + date of the run.
3. **Distinguish tiers of evidence.**
   - *Measured here* — produced by packdate tests/benches in this repository.
   - *Reported upstream* — quoted from another project/paper with link + date accessed.
   - *Hypothesis / target* — roadmap gates (e.g. Exact ISO ≥ 90%); never present as achieved results.
4. **Re-check before merging stale research.** Files under `docs/research/` are an archive. Before promoting a claim into README, ARCHITECTURE, or marketing-facing text, re-verify against current upstream pages or re-run the local bench. If verification fails, update or strike the claim; do not copy forward.
5. **Licenses are facts too.** Before adding a dependency or vendoring weights/data, open its license (and NOTICE obligations). Do not assume “MIT-like” or “Apache because Paddle”. Reject or isolate AGPL / unclear / NC / OpenRAIL-restricted artifacts as hard runtime deps (see ARCHITECTURE).
6. **When unsure, abstain in prose the same way the parser abstains on dates:** write “unverified”, open a TODO, or omit — never a confident wrong number.

Agents: if a user or prior message supplies a statistic, treat it as **untrusted until verified** against a source or a local run. Challenge politely in the PR/commit notes if you cannot verify; do not launder unverified claims into docs.

## Repository working rules

1. **Language of durable docs:** English in README, ROADMAP, AGENTS, ARCHITECTURE, code, and commit subjects. Russian is fine in issues/chat; translate lasting decisions into the docs.
2. **Small, reviewable commits.** One concern per commit. Subject ≈ imperative summary (`parse: add RU cue lexicon`), body only if needed for why/verification.
3. **Tests for behavior.** Parser and format changes need unit fixtures. Photo/OCR claims need golden fixtures under `tests/fixtures/` (no faces / PII) before accuracy language in README.
4. **Fail closed.** Prefer abstain / low confidence over a guessed ISO date — in code and in documentation promises.
5. **Dependency policy.** Prefer Apache-2.0 / MIT / BSD runtime deps. No Ultralytics YOLO (AGPL) as a hard dependency. Document new attributions in `NOTICE` when required.
6. **Do not mix data regimes.** No proprietary barcode API dumps into a redistributed Open Food Facts–derived database. Per-pack expiry stays outside OFF.
7. **Apps vs library.** Product UI under `apps/` must not block or bloat the core `extract()` / parse API.
8. **Secrets.** Never commit tokens, cookies, or private photos. Use env / local untracked paths for credentials.
9. **Public surface.** Assume every push to `main` is public. Do not land half-verified accuracy claims “temporarily”.

## Layout reminders

```text
src/packdate/detect/      # optional date ROI
src/packdate/recognize/   # OCR backends
src/packdate/parse/       # formats, cues, MFG vs EXP (build this first)
src/packdate/pipeline.py  # extract() — target API
apps/demo/                # thin CLI / demos
docs/research/            # archive; verify before promoting
tests/fixtures/           # golden cases
```

## What “done” means for agent tasks

- Change matches the current ROADMAP milestone unless the maintainer scoped otherwise.
- New factual statements comply with **Verification of information**.
- `LICENSE` / dependency policy respected.
- Push only when asked (or when the maintainer’s standing instruction for this session includes publish).

## Maintainer

GitHub: [stofll/packdate](https://github.com/stofll/packdate)
