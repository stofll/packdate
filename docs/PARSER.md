# Parser policy (medicines, v0.0.x)

How `packdate.parse` turns text into a [Result](ARCHITECTURE.md#result-contract). Stdlib only. Tests: `tests/test_parse_text.py`, `tests/test_gs1.py`, `tests/test_normalize.py`.

```python
from packdate.parse import parse_text, expiry_from_gs1

parse_text("Серия 010624\nГоден до: 06.2027").to_dict()
# iso_date "2027-06", valid_through "2027-06-30", rule_id "eaeu76_end_of_month", confidence "high"

expiry_from_gs1(decoded_datamatrix_text)  # AI (17) on EU/US packs; RU codes → abstain + GTIN/serial
```

## Steps

1. **Normalize** — NFKC; inside digit runs, `O/o/О/о → 0` and `l/I/| → 1` (not at a run edge that touches a letter, so «до06.2027» keeps its «о»).
2. **Fold** — lowercase + Cyrillic/Latin homoglyphs to one form, so «ЕХР» matches EXP and «Cepия» matches «Серия». Folding is 1:1, so offsets stay valid.
3. **Cues** — expiry («годен до», «годен», «срок годности», EXP, use by, …), weak expiry (bare «до»), MFG («дата изготовления», MFG, …), batch («серия», LOT, …). List: `parse/lexicon.py`.
4. **Mask batch values** — the token after a batch cue is never read as a date («Серия 010624»).
5. **Dates** — patterns below; a match that fails the calendar still consumes its span, so `06/15/2027` never degrades into `06/15`.
6. **Pair** cues with dates, then **decide** (tables below).

## Formats

| Pattern | Example | Precision | Notes |
|---|---|---|---|
| `ДД.ММ.ГГГГ`, `ДД.ММ.ГГ` (`.` `/` `-` `_`) | `15.03.2027` | day | DMY by default; with `/` and a non-Russian cue, MM/DD is kept as another reading (confidence `check`). `ДД-ММ-ГГ` needs a cue: phone numbers look the same |
| `ГГГГ-ММ-ДД` (`-` `.` `/` `_`) | `2027-06-15`, `2021.08.03` | day | repeated separator; invalid full dates cannot fall back to month precision (tests: `tests/test_parse_text.py`) |
| `[ДД] MON ГГГГ` (EN / RU month names) | `30 JUN 2027`, `12 ИЮЛ 2026` | day / month | two-digit year needs a cue |
| `ГГГГ-ММ`, `ГГГГ.ММ`, `ГГГГ/ММ` | `2027-06` | month | |
| `ММ.ГГГГ`, `ММ/ГГГГ`, `ММ_ГГГГ`, `ММ ГГГГ` | `06.2027` | month | EAEU №76 п.6 |
| `ММ.ГГ` (`.` `/` `-` `_`) | `06.27` | month | needs a cue: too easy to confuse with doses (`10.25 мг`) |
| `ММГГ`, `ММГГГГ`, `ДДММГГ`, `ДДММГГГГ` (no separator) | `0727`, `15032027` | month / day | needs a cue: batch numbers look the same. Six digits → `ММГГГГ` if valid, else `ДДММГГ` |

Years must be 2000–2099; two-digit years are 20YY.

## Rules (`valid_through`)

| `rule_id` | When | Last good day |
|---|---|---|
| `eaeu76_end_of_month` | month precision | last day of the month — EAEU №76 п.30 ([research/10](research/10-medicine-vs-food.md)) |
| `printed_day` | day precision | the printed day, inclusive. **Inclusivity for medicines is not confirmed by a primary source yet** (cosmetics under ТР ТС 009 exclude the day — [research/12](research/12-post-recognition.md)) |
| `gs1_ai17` | AI (17) `YYMMDD` | that day |
| `gs1_ai17_day00` | AI (17) with day `00` | last day of the month; confidence `check` — source for this reading is secondary so far |

## Pairing

- Events are walked left to right as runs: cues, then dates.
- One cue → it takes the first date after it, within 24 characters (3 for bare «до»).
- Consecutive cues of the same type merge: «Годен до / EXP 06.2027» is one cue.
- N cues followed by exactly N dates → paired in order (column layout: `MFG EXP` / `01.2025 01.2028`), confidence `check`.
- Any other shape → no pairing; the dates stay `unknown` candidates.

## Decision

| Situation | Result |
|---|---|
| One distinct expiry date (repeats allowed) | committed, `high` |
| …from bare «до», column layout, or an MM/DD reading | committed, `check` |
| Expiry earlier than an MFG date | abstain `inconsistent` |
| Several different expiry dates (incl. DD/MM vs MM/DD) | abstain `ambiguous` |
| Expiry cue, no valid date for it | abstain `cue_without_date` |
| Dates, none tied to an expiry cue | abstain `no_cue` |
| Only MFG dates | abstain `mfg_only` |
| No dates | abstain `no_date` |

MFG never becomes the expiry. Candidates are always returned (expiry first, then unknown, then MFG) so the UI can offer them as chips.

## GS1 element strings

`parse_gs1` accepts raw text with GS (ASCII 29), zxing's escaped `<GS>`, a leading symbology identifier (`]d2`) or FNC1, and the `(01)…(17)…` human-readable form. Fixed-length AIs (01, 17, 31xx–36xx, …) need no separator; others end at GS. Unknown AIs stop parsing (`invalid_code`) rather than guess. GTIN check digits are verified.

Russian marking codes (01 + 21 + 91 + 92, or 01 + 21 + 93) have no AI (17): `code_without_date`, with GTIN and serial in `extra`.

## Known gaps

- Spaces inside a digit group (`20 27`) are not read.
- Full dates with space-only separators (`22 06 2022`) or month-first names (`APR-28-2023`) can produce incorrect partial month readings. See the [ExpDate diagnostic](benchmarks/expdate-2026-09-26.md#interpretation-and-next-work) for reproducible examples; these formats still need fail-closed handling.
- A date printed before its cue (`18072024 Годен до`) is not paired.
- Shelf life relative to manufacture («дата изготовления 08.2017», «срок годности 2,5 года») is not derived.
- Food (ТР ТС 022) and cosmetics (ТР ТС 009) rules are not implemented — see [ROADMAP](../ROADMAP.md) milestone 6.
- The 24-character pairing window and the confidence categories are first guesses; the bench (milestone 4) should tune them.
