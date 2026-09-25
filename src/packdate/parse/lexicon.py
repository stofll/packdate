"""Cue words for medicine packs (RU/EN).

Sources for the RU expiry cues: EAEU Council Decision №76, п.5 («годен до…»,
«годен…», «до…»); see docs/research/10-medicine-vs-food.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from packdate.parse.normalize import fold


class CueType(StrEnum):
    EXPIRY = "expiry"
    MFG = "mfg"
    BATCH = "batch"


@dataclass(frozen=True)
class Cue:
    type: CueType
    text: str
    span: tuple[int, int]
    weak: bool = False  # bare «до»: legal on packs, but also common in other phrases


_EXPIRY = [
    "годен до",
    "годн. до",
    "годен",
    "срок годности до",
    "срок годности",
    "использовать до",
    "употребить до",
    "exp. date",
    "expiry date",
    "expiration date",
    "expiry",
    "expires",
    "exp",
    "use by",
    "best before",
]
_EXPIRY_WEAK = ["до"]
_MFG = [
    "дата изготовления",
    "дата изг.",
    "дата изг",
    "дата производства",
    "дата выпуска",
    "изготовлено",
    "произведено",
    "manufacturing date",
    "manufactured",
    "mfg",
    "mfd",
]
_BATCH = ["серия", "сер.", "партия", "lot", "batch", "b.n."]


def _alternation(words: list[str]) -> str:
    # Longest first, so "годен до" wins over "годен" and "до".
    parts = sorted({re.escape(fold(w)) for w in words}, key=len, reverse=True)
    return "|".join(parts)


_PATTERNS: list[tuple[CueType, bool, str]] = [
    (CueType.EXPIRY, False, _alternation(_EXPIRY)),
    (CueType.EXPIRY, True, _alternation(_EXPIRY_WEAK)),
    (CueType.MFG, False, _alternation(_MFG)),
    (CueType.BATCH, False, _alternation(_BATCH)),
]
# Not inside a longer word; digits may touch the cue ("EXP06/2027"), and a cue
# ending in "." ("сер.") may touch anything.
_LETTER = r"[^\W\d_]"
_CUE_RE = re.compile(
    rf"(?<!{_LETTER})(?:"
    + "|".join(f"(?P<g{i}>{pattern})" for i, (_, _, pattern) in enumerate(_PATTERNS))
    + rf")(?:(?<=\.)|(?!{_LETTER}))"
)

# The batch value right after a batch cue: optional ":" / "№", then one token.
_BATCH_VALUE = re.compile(r"[\s:№#]*([\w\-]+)")


def find_cues(folded: str) -> list[Cue]:
    """All cues in folded text, left to right, non-overlapping."""
    cues = []
    for m in _CUE_RE.finditer(folded):
        for i, (cue_type, weak, _) in enumerate(_PATTERNS):
            if m.group(f"g{i}") is not None:
                cues.append(Cue(cue_type, m.group(), m.span(), weak))
                break
    return cues


def batch_value_span(folded: str, cue: Cue) -> tuple[int, int] | None:
    """Span of the batch number after a batch cue, so it is not read as a date."""
    m = _BATCH_VALUE.match(folded, cue.span[1])
    return m.span(1) if m else None
