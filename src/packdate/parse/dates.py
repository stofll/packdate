"""Date grammar for medicine packs and the rules that turn a reading into a
last good day.

Formats: EAEU Council Decision №76, п.6 (`ММ ГГГГ`, `ММ.ГГГГ`, `ММ/ГГГГ`,
`ММ_ГГГГ` and two-digit-year variants) and full dates when the day is printed
(п.30). Plus ISO-like `ГГГГ-ММ(-ДД)` and English month names seen on imported
packs. See docs/PARSER.md.
"""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass
from datetime import date

from packdate.parse.normalize import fold
from packdate.result import Precision

# Month precision: the pack is good through the last day of the stated month
# (EAEU №76 п.30).
RULE_END_OF_MONTH = "eaeu76_end_of_month"
# Day precision: good through the printed day, inclusive. Inclusivity for
# medicines is not confirmed by a primary source yet (docs/PARSER.md).
RULE_PRINTED_DAY = "printed_day"

MIN_YEAR, MAX_YEAR = 2000, 2099

_MONTHS = {
    # EN
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    # RU (genitive «мая» included)
    "янв": 1, "фев": 2, "мар": 3, "апр": 4, "май": 5, "мая": 5, "июн": 6,
    "июл": 7, "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12,
}  # fmt: skip
_MONTH_KEYS = {fold(k): v for k, v in _MONTHS.items()}
_MONTH_ALT = "|".join(sorted(map(re.escape, _MONTH_KEYS), key=len, reverse=True))

_SEP = r"\s*[./\-_]\s*"
_D = r"(?<!\d)"  # not preceded by a digit
_E = r"(?!\d)"  # not followed by a digit


@dataclass(frozen=True)
class DateMatch:
    """A syntactic date match. `readings` is empty when no calendar reading is valid."""

    span: tuple[int, int]
    raw: str
    readings: tuple[tuple[date, Precision], ...]
    needs_cue: bool  # two-digit-year month dates are too easy to confuse with other numbers
    month_first: bool = False  # includes an MM/DD reading (not the EAEU default)


def _year(text: str) -> int | None:
    y = int(text)
    if len(text) == 2:
        y += 2000
    return y if MIN_YEAR <= y <= MAX_YEAR else None


def _day_date(y: int | None, m: int, d: int) -> date | None:
    if y is None or not 1 <= m <= 12:
        return None
    if not 1 <= d <= calendar.monthrange(y, m)[1]:
        return None
    return date(y, m, d)


def _month_date(y: int | None, m: int) -> date | None:
    if y is None or not 1 <= m <= 12:
        return None
    return date(y, m, 1)


# Each pattern turns a match into (readings, needs_cue, month_first).
def _full_numeric(m: re.Match[str]):
    a, b, y = int(m["a"]), int(m["b"]), _year(m["y"])
    dmy = _day_date(y, b, a)
    readings = [(dmy, Precision.DAY)] if dmy else []
    month_first = False
    if m["sep"].strip() == "/":
        # Slash dates on imported packs may be MM/DD. Default is DMY (EAEU);
        # keep MDY as another reading instead of guessing.
        mdy = _day_date(y, a, b)
        if mdy and mdy != dmy:
            readings.append((mdy, Precision.DAY))
            month_first = True
    return readings, False, month_first


def _iso_day(m: re.Match[str]):
    d = _day_date(_year(m["y"]), int(m["m"]), int(m["d"]))
    return ([(d, Precision.DAY)] if d else []), False, False


def _iso_month(m: re.Match[str]):
    d = _month_date(_year(m["y"]), int(m["m"]))
    return ([(d, Precision.MONTH)] if d else []), False, False


def _month_year(m: re.Match[str]):
    d = _month_date(_year(m["y"]), int(m["m"]))
    return ([(d, Precision.MONTH)] if d else []), len(m["y"]) == 2, False


def _named(m: re.Match[str]):
    month = _MONTH_KEYS[m["mon"]]
    y = _year(m["y"])
    needs_cue = len(m["y"]) == 2
    if m["d"]:
        d = _day_date(y, month, int(m["d"]))
        return ([(d, Precision.DAY)] if d else []), needs_cue, False
    d = _month_date(y, month)
    return ([(d, Precision.MONTH)] if d else []), needs_cue, False


# Priority order: longer / more specific first. A syntactic match consumes its
# span even if the calendar rejects it, so "06/15/2027" never degrades into a
# shorter "06/15" reading.
_PATTERNS = [
    (
        re.compile(
            rf"{_D}(?P<a>\d{{1,2}})(?P<sep>{_SEP})(?P<b>\d{{1,2}})(?P=sep)(?P<y>\d{{4}}|\d{{2}}){_E}"
        ),
        _full_numeric,
    ),
    (
        re.compile(rf"{_D}(?P<y>\d{{4}})\s*-\s*(?P<m>\d{{1,2}})\s*-\s*(?P<d>\d{{1,2}}){_E}"),
        _iso_day,
    ),
    (
        re.compile(
            rf"{_D}(?:(?P<d>\d{{1,2}})[\s./\-]*)?(?<![^\W\d_])(?P<mon>{_MONTH_ALT})[^\W\d_]{{0,6}}\.?[\s./\-]*(?P<y>\d{{4}}|\d{{2}}){_E}"
        ),
        _named,
    ),
    (re.compile(rf"{_D}(?P<y>\d{{4}})\s*[./\-]\s*(?P<m>\d{{1,2}}){_E}"), _iso_month),
    (re.compile(rf"{_D}(?P<m>\d{{1,2}})(?:{_SEP}|\s+)(?P<y>\d{{4}}){_E}"), _month_year),
    (re.compile(rf"{_D}(?P<m>\d{{2}}){_SEP}(?P<y>\d{{2}}){_E}"), _month_year),
]


def find_dates(folded: str) -> list[DateMatch]:
    """All date-like matches in folded text, left to right, non-overlapping."""
    taken: list[tuple[int, int]] = []
    found: list[DateMatch] = []
    for pattern, interpret in _PATTERNS:
        for m in pattern.finditer(folded):
            start, end = m.span()
            if any(start < t_end and t_start < end for t_start, t_end in taken):
                continue
            taken.append((start, end))
            readings, needs_cue, month_first = interpret(m)
            found.append(DateMatch(m.span(), m.group(), tuple(readings), needs_cue, month_first))
    return sorted(found, key=lambda d: d.span)


def iso_date(d: date, precision: Precision) -> str:
    return d.isoformat() if precision is Precision.DAY else f"{d.year:04d}-{d.month:02d}"


def valid_through(d: date, precision: Precision) -> tuple[date, str]:
    """Last good day and the rule that produced it."""
    if precision is Precision.MONTH:
        return d.replace(day=calendar.monthrange(d.year, d.month)[1]), RULE_END_OF_MONTH
    return d, RULE_PRINTED_DAY
