"""GS1 element strings from decoded DataMatrix codes.

The input is text a decoder already produced (e.g. zxing-cpp): raw with GS
(ASCII 29) separators, zxing's escaped form with "<GS>", or the human-readable
"(01)…(17)…" form.

AI (17) carries the expiry on EU FMD and US DSCSA drug packs. Russian marking
codes (МДЛП, «Честный ЗНАК») carry GTIN + serial + crypto tail and no expiry.
See docs/research/10-medicine-vs-food.md.
"""

from __future__ import annotations

import calendar
import re
from datetime import date

from packdate.result import (
    AbstainReason,
    Confidence,
    DateCandidate,
    Kind,
    Precision,
    Result,
    Source,
)

GS = "\x1d"
_FNC1_ALIASES = ("<GS>", "<FNC1>", "\xe8")  # zxing escaped form; FNC1 as ASCII 232
_SYMBOLOGY_ID = re.compile(r"^\][A-Za-z]\d")  # "]d2", "]C1", "]Q3", …

RULE_AI17 = "gs1_ai17"
# Day "00" in AI (17): no specific day, read as end of month. This reading and
# the healthcare ban on "00" are taken from secondary sources so far
# (docs/research/12-post-recognition.md, UNVERIFIED list), hence CHECK.
RULE_AI17_DAY00 = "gs1_ai17_day00"

# AI length by its first two digits. Covers the AIs seen on drug and food packs;
# anything else stops parsing rather than guessing.
_AI_LENGTH = {
    **dict.fromkeys(["00", "01", "02", "10", "11", "12", "13", "15", "16", "17"], 2),
    **dict.fromkeys(["20", "21", "22", "30", "37"], 2),
    **{str(p): 2 for p in range(90, 100)},
    **dict.fromkeys(["23", "24", "25", "40", "41", "42"], 3),
    **dict.fromkeys(
        ["31", "32", "33", "34", "35", "36", "39", "70", "71", "72", "80", "81", "82"], 4
    ),
}
# Element strings with a predefined total length (AI + data) need no GS after them.
_PREDEFINED_LENGTH = {
    "00": 20, "01": 16, "02": 16, "03": 16, "04": 18,
    "11": 8, "12": 8, "13": 8, "14": 8, "15": 8, "16": 8, "17": 8, "18": 8, "19": 8,
    "20": 4, "31": 10, "32": 10, "33": 10, "34": 10, "35": 10, "36": 10, "41": 16,
}  # fmt: skip
_HRI = re.compile(r"\((\d{2,4})\)([^(]*)")


def parse_gs1(text: str) -> dict[str, str]:
    """Element string → {AI: value}. Raises ValueError on malformed input."""
    text = text.strip()
    if text.startswith("("):
        elements = {ai: value for ai, value in _HRI.findall(text)}
        if not elements:
            raise ValueError("no (AI) groups found")
        return elements

    text = _SYMBOLOGY_ID.sub("", text)
    for alias in _FNC1_ALIASES:
        text = text.replace(alias, GS)
    text = text.lstrip(GS)

    elements: dict[str, str] = {}
    pos = 0
    while pos < len(text):
        prefix = text[pos : pos + 2]
        ai_len = _AI_LENGTH.get(prefix)
        if ai_len is None:
            raise ValueError(f"unknown AI prefix {prefix!r} at {pos}")
        ai = text[pos : pos + ai_len]
        if not ai.isdigit():
            raise ValueError(f"AI is not numeric: {ai!r}")
        if prefix in _PREDEFINED_LENGTH:
            end = pos + _PREDEFINED_LENGTH[prefix]
            if end > len(text):
                raise ValueError(f"AI ({ai}) is truncated")
            value, pos = text[pos + ai_len : end], end
            if pos < len(text) and text[pos] == GS:  # tolerated, though not required
                pos += 1
        else:
            end = text.find(GS, pos)
            end = len(text) if end == -1 else end
            value, pos = text[pos + ai_len : end], end + 1
        if not value:
            raise ValueError(f"AI ({ai}) has no value")
        elements[ai] = value
    if not elements:
        raise ValueError("empty element string")
    return elements


def gtin_check_digit_ok(gtin: str) -> bool:
    if not gtin.isdigit() or len(gtin) not in (8, 12, 13, 14):
        return False
    body, check = gtin[:-1], int(gtin[-1])
    total = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(body)))
    return (10 - total % 10) % 10 == check


def expiry_from_gs1(text: str) -> Result:
    """Expiry from a decoded GS1 code, plus GTIN / serial / batch in `extra`."""
    try:
        elements = parse_gs1(text)
    except ValueError:
        return Result.abstain(AbstainReason.INVALID_CODE, Source.DATAMATRIX)

    extra = {
        name: elements[ai]
        for ai, name in (("01", "gtin"), ("21", "serial"), ("10", "batch"))
        if ai in elements
    }
    if "gtin" in extra and not gtin_check_digit_ok(extra["gtin"]):
        return Result.abstain(AbstainReason.INVALID_CODE, Source.DATAMATRIX, extra=extra)
    if "17" not in elements:
        return Result.abstain(AbstainReason.CODE_WITHOUT_DATE, Source.DATAMATRIX, extra=extra)

    candidate = _ai17_candidate(elements["17"])
    if candidate is None:
        return Result.abstain(AbstainReason.INVALID_CODE, Source.DATAMATRIX, extra=extra)
    return Result(
        confidence=Confidence.CHECK if candidate.rule_id == RULE_AI17_DAY00 else Confidence.HIGH,
        source=Source.DATAMATRIX,
        candidates=(candidate,),
        chosen=candidate,
        extra=extra,
    )


def _ai17_candidate(value: str) -> DateCandidate | None:
    if len(value) != 6 or not value.isdigit():
        return None
    # 20YY. GS1's sliding century window differs only for YY >= 77 (it reads
    # them as 19YY), which no current pack carries as an expiry.
    year, month, day = 2000 + int(value[:2]), int(value[2:4]), int(value[4:])
    if not 1 <= month <= 12:
        return None
    last = calendar.monthrange(year, month)[1]
    if day == 0:
        return DateCandidate(
            iso_date=f"{year:04d}-{month:02d}",
            precision=Precision.MONTH,
            valid_through=date(year, month, last),
            rule_id=RULE_AI17_DAY00,
            kind=Kind.EXPIRY,
            raw=value,
        )
    if day > last:
        return None
    d = date(year, month, day)
    return DateCandidate(
        iso_date=d.isoformat(),
        precision=Precision.DAY,
        valid_through=d,
        rule_id=RULE_AI17,
        kind=Kind.EXPIRY,
        raw=value,
    )
