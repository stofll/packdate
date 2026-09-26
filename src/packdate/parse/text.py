"""Parse OCR text from a medicine pack into a Result.

Policy (docs/PARSER.md): a date becomes the expiry only when an expiry cue
points at it; everything else is a candidate for the user to pick. When in
doubt, abstain.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from packdate.parse.dates import DateMatch, find_dates, iso_date, valid_through
from packdate.parse.lexicon import Cue, CueType, batch_value_span, find_cues
from packdate.parse.normalize import fold, normalize
from packdate.result import (
    AbstainReason,
    Confidence,
    DateCandidate,
    Kind,
    Precision,
    Result,
    Source,
)

# Max characters between a cue and its date.
MAX_GAP = 24
MAX_GAP_WEAK = 3  # bare «до» must be right before the date
MAX_GAP_COLUMNS = 48  # "MFG EXP\n01.2025 01.2028": cue row, then date row


@dataclass(frozen=True)
class _Pairing:
    cue: Cue
    columns: bool  # paired by position in a row of cues


def parse_text(text: str, source: Source = Source.OCR) -> Result:
    norm = normalize(text)
    folded = fold(norm)
    cues = find_cues(folded)
    dates = find_dates(_mask_batch_values(folded, cues))
    pairings = _pair(cues, dates)

    candidates: list[DateCandidate] = []
    month_first: set[DateCandidate] = set()  # candidates read as MM/DD
    expiry_cue_paired_invalid = False
    for i, match in enumerate(dates):
        pairing = pairings.get(i)
        cue_text = norm[pairing.cue.span[0] : pairing.cue.span[1]] if pairing else None
        # MM/DD is an imported-pack convention; next to a Russian cue it is not a reading.
        alt = () if cue_text and _CYRILLIC.search(cue_text) else match.alt_readings
        if not match.readings and not alt:
            if pairing and pairing.cue.type is CueType.EXPIRY:
                expiry_cue_paired_invalid = True
            continue
        if match.needs_cue and pairing is None:
            continue
        kind = _KIND[pairing.cue.type] if pairing else Kind.UNKNOWN
        raw = norm[match.span[0] : match.span[1]]
        for n, (d, precision) in enumerate(match.readings + alt):
            last_day, rule_id = valid_through(d, precision)
            candidates.append(
                DateCandidate(
                    iso_date=iso_date(d, precision),
                    precision=precision,
                    valid_through=last_day,
                    rule_id=rule_id,
                    kind=kind,
                    raw=raw,
                    span=match.span,
                    cue=cue_text,
                )
            )
            if n >= len(match.readings):
                month_first.add(candidates[-1])

    ordered = tuple(sorted(candidates, key=lambda c: _KIND_ORDER[c.kind]))
    expiry = [c for c in ordered if c.kind is Kind.EXPIRY]
    has_expiry_cue = any(c.type is CueType.EXPIRY and not c.weak for c in cues)

    if not expiry:
        if has_expiry_cue or expiry_cue_paired_invalid:
            reason = AbstainReason.CUE_WITHOUT_DATE
        elif any(c.kind is Kind.UNKNOWN for c in ordered):
            reason = AbstainReason.NO_CUE
        elif ordered:
            reason = AbstainReason.MFG_ONLY
        else:
            reason = AbstainReason.NO_DATE
        return Result.abstain(reason, source, ordered)

    if len({c.valid_through for c in expiry}) > 1:
        return Result.abstain(AbstainReason.AMBIGUOUS, source, ordered)

    chosen = expiry[0]
    mfg = [c for c in ordered if c.kind is Kind.MFG]
    if any(_first_day(c) > chosen.valid_through for c in mfg):
        return Result.abstain(AbstainReason.INCONSISTENT, source, ordered)

    index = next(i for i, m in enumerate(dates) if m.span == chosen.span)
    pairing = pairings[index]
    uncertain = chosen in month_first or pairing.cue.weak or pairing.columns
    return Result(
        confidence=Confidence.CHECK if uncertain else Confidence.HIGH,
        source=source,
        candidates=ordered,
        chosen=chosen,
    )


_KIND = {CueType.EXPIRY: Kind.EXPIRY, CueType.MFG: Kind.MFG}
_CYRILLIC = re.compile("[а-яё]", re.IGNORECASE)
_KIND_ORDER = {Kind.EXPIRY: 0, Kind.UNKNOWN: 1, Kind.MFG: 2}


def _first_day(c: DateCandidate) -> date:
    return c.valid_through.replace(day=1) if c.precision is Precision.MONTH else c.valid_through


def _mask_batch_values(folded: str, cues: list[Cue]) -> str:
    chars = list(folded)
    for cue in cues:
        if cue.type is CueType.BATCH and (span := batch_value_span(folded, cue)):
            chars[span[0] : span[1]] = " " * (span[1] - span[0])
    return "".join(chars)


def _pair(cues: list[Cue], dates: list[DateMatch]) -> dict[int, _Pairing]:
    """Tie dates to the cues right before them.

    Events are walked left to right as runs: a run of cues, then a run of
    dates. One cue → it takes the first date. N cues followed by exactly N
    dates → paired in order (column layout). Anything else → no pairing.
    """
    # Batch cues are left out: their value is already masked, and they must not
    # turn "Серия 123 Годен до 06.2027" into a two-cue column row.
    events: list[tuple[int, str, int]] = [
        (c.span[0], "cue", i) for i, c in enumerate(cues) if c.type is not CueType.BATCH
    ]
    events += [(d.span[0], "date", i) for i, d in enumerate(dates)]
    events.sort()

    pairings: dict[int, _Pairing] = {}
    i = 0
    while i < len(events):
        if events[i][1] != "cue":
            i += 1
            continue
        j = i
        while j < len(events) and events[j][1] == "cue":
            j += 1
        k = j
        while k < len(events) and events[k][1] == "date":
            k += 1
        groups = _merge_same_type([cues[e[2]] for e in events[i:j]])
        run = [e[2] for e in events[j:k]]
        if run:
            first_gap = dates[run[0]].span[0] - groups[-1].span[1]
            if len(groups) == 1:
                limit = MAX_GAP_WEAK if groups[0].weak else MAX_GAP
                if first_gap <= limit:
                    pairings[run[0]] = _Pairing(groups[0], columns=False)
            elif len(groups) == len(run) and first_gap <= MAX_GAP_COLUMNS:
                for cue, date_index in zip(groups, run):
                    pairings[date_index] = _Pairing(cue, columns=True)
        i = k
    return pairings


def _merge_same_type(run: list[Cue]) -> list[Cue]:
    """ "Годен до / EXP" is one expiry cue, not two columns."""
    merged: list[Cue] = []
    for cue in run:
        if merged and merged[-1].type is cue.type:
            prev = merged[-1]
            merged[-1] = Cue(
                cue.type, cue.text, (prev.span[0], cue.span[1]), weak=prev.weak and cue.weak
            )
        else:
            merged.append(cue)
    return merged
