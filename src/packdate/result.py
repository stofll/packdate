"""Result types shared by the parser and the extraction pipeline.

See docs/ARCHITECTURE.md#result-contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class Precision(StrEnum):
    DAY = "day"
    MONTH = "month"


class Kind(StrEnum):
    EXPIRY = "expiry"
    MFG = "mfg"
    UNKNOWN = "unknown"


class Confidence(StrEnum):
    HIGH = "high"  # prefill, one tap to confirm
    CHECK = "check"  # show candidates, nothing preselected
    NONE = "none"  # abstained


class Source(StrEnum):
    OCR = "ocr"
    DATAMATRIX = "datamatrix"


class AbstainReason(StrEnum):
    NO_DATE = "no_date"  # no date-like text at all
    NO_CUE = "no_cue"  # dates found, none tied to an expiry cue
    CUE_WITHOUT_DATE = "cue_without_date"  # expiry cue with no valid date after it
    MFG_ONLY = "mfg_only"  # only manufacture dates
    AMBIGUOUS = "ambiguous"  # several different expiry dates
    INCONSISTENT = "inconsistent"  # expiry earlier than manufacture
    CODE_WITHOUT_DATE = "code_without_date"  # GS1 code has no AI (17)
    INVALID_CODE = "invalid_code"  # GS1 element string could not be parsed


@dataclass(frozen=True)
class DateCandidate:
    """One date reading found in the input."""

    iso_date: str  # "2027-06" (month) or "2027-06-15" (day)
    precision: Precision
    valid_through: date  # last good day after applying rule_id
    rule_id: str
    kind: Kind
    raw: str  # matched text
    span: tuple[int, int] = (0, 0)  # offsets in the normalized text
    cue: str | None = None  # matched cue text, if any

    def to_dict(self) -> dict:
        return {
            "iso_date": self.iso_date,
            "precision": self.precision.value,
            "valid_through": self.valid_through.isoformat(),
            "rule_id": self.rule_id,
            "kind": self.kind.value,
            "raw": self.raw,
            "span": list(self.span),
            "cue": self.cue,
        }


@dataclass(frozen=True)
class Result:
    """Committed reading (if any) plus everything needed to confirm it."""

    confidence: Confidence
    source: Source
    candidates: tuple[DateCandidate, ...] = ()
    chosen: DateCandidate | None = None
    abstain_reason: AbstainReason | None = None
    bboxes: tuple[tuple[float, float, float, float], ...] = ()  # filled by the pipeline
    extra: dict[str, str] = field(default_factory=dict)  # e.g. GTIN / serial from a code

    @property
    def iso_date(self) -> str | None:
        return self.chosen.iso_date if self.chosen else None

    @property
    def precision(self) -> Precision | None:
        return self.chosen.precision if self.chosen else None

    @property
    def valid_through(self) -> date | None:
        return self.chosen.valid_through if self.chosen else None

    @property
    def rule_id(self) -> str | None:
        return self.chosen.rule_id if self.chosen else None

    @property
    def kind(self) -> Kind:
        return self.chosen.kind if self.chosen else Kind.UNKNOWN

    @classmethod
    def abstain(
        cls,
        reason: AbstainReason,
        source: Source,
        candidates: tuple[DateCandidate, ...] = (),
        extra: dict[str, str] | None = None,
    ) -> Result:
        return cls(
            confidence=Confidence.NONE,
            source=source,
            candidates=candidates,
            abstain_reason=reason,
            extra=extra or {},
        )

    def to_dict(self) -> dict:
        return {
            "iso_date": self.iso_date,
            "precision": self.precision.value if self.precision else None,
            "valid_through": self.valid_through.isoformat() if self.valid_through else None,
            "rule_id": self.rule_id,
            "kind": self.kind.value,
            "confidence": self.confidence.value,
            "abstain_reason": self.abstain_reason.value if self.abstain_reason else None,
            "source": self.source.value,
            "candidates": [c.to_dict() for c in self.candidates],
            "bboxes": [list(b) for b in self.bboxes],
            "extra": dict(self.extra),
        }
