from datetime import date

import pytest

from packdate.parse import parse_text
from packdate.result import AbstainReason, Confidence, Kind, Precision, Source

# (text, valid_through, confidence)
COMMITTED = [
    # EAEU №76 п.6 formats, month precision → last day of month (п.30)
    ("Годен до: 06.2027", date(2027, 6, 30), Confidence.HIGH),
    ("годен до 02.2028", date(2028, 2, 29), Confidence.HIGH),  # leap year
    ("ГОДЕН ДО 06 2027", date(2027, 6, 30), Confidence.HIGH),
    ("Годен до 11/2026", date(2026, 11, 30), Confidence.HIGH),
    ("Годен до 11_2026", date(2026, 11, 30), Confidence.HIGH),
    ("годен 04.27", date(2027, 4, 30), Confidence.HIGH),
    ("Срок годности до 09.2026", date(2026, 9, 30), Confidence.HIGH),
    # full date when the day is printed
    ("Годен до: 15.03.2027", date(2027, 3, 15), Confidence.HIGH),
    ("Годен до 15.03.27", date(2027, 3, 15), Confidence.HIGH),
    # imported packs
    ("EXP 06/27", date(2027, 6, 30), Confidence.HIGH),
    ("EXP: 2027-06", date(2027, 6, 30), Confidence.HIGH),
    ("EXP 2027-06-15", date(2027, 6, 15), Confidence.HIGH),
    ("EXP 30 JUN 2027", date(2027, 6, 30), Confidence.HIGH),
    ("EXP JUN 2027", date(2027, 6, 30), Confidence.HIGH),
    ("Годен до 12 ИЮЛ 2026", date(2026, 7, 12), Confidence.HIGH),
    ("Use by 01.2030", date(2030, 1, 31), Confidence.HIGH),
    # OCR noise and glued text
    ("Годен до O6.2O27", date(2027, 6, 30), Confidence.HIGH),
    ("Годен до 06. 2027", date(2027, 6, 30), Confidence.HIGH),
    ("EXP06/2027", date(2027, 6, 30), Confidence.HIGH),
    ("ЕХР 06.2027", date(2027, 6, 30), Confidence.HIGH),  # Cyrillic "ЕХР"
    ("Гoдeн дo 06.2027", date(2027, 6, 30), Confidence.HIGH),  # Latin lookalikes
    # cue and date on separate OCR lines
    ("Годен до:\n06.2027", date(2027, 6, 30), Confidence.HIGH),
    # merged cues, repeated identical dates
    ("Годен до / EXP 06.2027", date(2027, 6, 30), Confidence.HIGH),
    ("Годен до 06.2027\nEXP 06.2027", date(2027, 6, 30), Confidence.HIGH),
    # batch numbers are not dates
    ("Серия 010624\nГоден до 06.2027", date(2027, 6, 30), Confidence.HIGH),
    ("Lot 0624 Exp 06.2027", date(2027, 6, 30), Confidence.HIGH),
    ("Серия: 12.2024 Годен до 12.2027", date(2027, 12, 31), Confidence.HIGH),
    # MFG next to EXP
    ("Дата изготовления 06.2024 Годен до 06.2027", date(2027, 6, 30), Confidence.HIGH),
    ("MFG 01.2025 EXP 01.2028", date(2028, 1, 31), Confidence.HIGH),
    # weaker evidence → CHECK
    ("до 11.2026", date(2026, 11, 30), Confidence.CHECK),  # bare «до»
    ("до06.2027", date(2027, 6, 30), Confidence.CHECK),
    ("MFG EXP\n01.2025 01.2028", date(2028, 1, 31), Confidence.CHECK),  # column layout
    ("EXP 06/15/2027", date(2027, 6, 15), Confidence.CHECK),  # only MM/DD is valid
    # no separators (always need a cue)
    ("Годен до 0727", date(2027, 7, 31), Confidence.HIGH),  # MMYY
    ("Годен до 072027", date(2027, 7, 31), Confidence.HIGH),  # MMYYYY
    ("Годен до 150327", date(2027, 3, 15), Confidence.HIGH),  # DDMMYY
    ("Годен до 15032027", date(2027, 3, 15), Confidence.HIGH),  # DDMMYYYY
    # a Russian cue rules out the MM/DD reading
    ("Годен до: 01/07/2021", date(2021, 7, 1), Confidence.HIGH),
    # OCR text from Wikimedia Commons photos (datasets/commons_ru_drugs.labels.json)
    ("Серия 490724\nГоден до 0727", date(2027, 7, 31), Confidence.HIGH),
    ("Серия 571217 / Годен до 0120", date(2020, 1, 31), Confidence.HIGH),
    ("СЕРИЯ 0530424 ГОДЕН ДО 04 2029", date(2029, 4, 30), Confidence.HIGH),
    ("Серия GCO377\nРЕДНИЗОДОН\nГоден до 02/2027", date(2027, 2, 28), Confidence.HIGH),
]


@pytest.mark.parametrize(("text", "expected", "confidence"), COMMITTED)
def test_commits_expiry(text, expected, confidence):
    result = parse_text(text)
    assert result.valid_through == expected
    assert result.confidence is confidence
    assert result.kind is Kind.EXPIRY
    assert result.abstain_reason is None


ABSTAINED = [
    ("", AbstainReason.NO_DATE),
    ("Хранить при температуре не выше 25 °C", AbstainReason.NO_DATE),
    ("Таблетки 10.25 мг", AbstainReason.NO_DATE),  # MM.YY without a cue is ignored
    ("06.2027", AbstainReason.NO_CUE),
    ("Годен до:", AbstainReason.CUE_WITHOUT_DATE),
    ("Годен до 13.2027", AbstainReason.CUE_WITHOUT_DATE),
    ("Годен до 31.02.2027", AbstainReason.CUE_WITHOUT_DATE),
    ("Годен до 06.1999", AbstainReason.CUE_WITHOUT_DATE),  # outside 2000–2099
    ("Срок годности указан на упаковке", AbstainReason.CUE_WITHOUT_DATE),
    ("Дата изготовления: 06.2024", AbstainReason.MFG_ONLY),
    ("Годен до 06.2027 Годен до 07.2027", AbstainReason.AMBIGUOUS),
    ("EXP 06/07/2027", AbstainReason.AMBIGUOUS),  # DD/MM and MM/DD both valid
    ("Дата изг. 06.2028 Годен до 06.2027", AbstainReason.INCONSISTENT),
    ("Годен до / Серия\n06.2027 123456", AbstainReason.CUE_WITHOUT_DATE),
    ("0727", AbstainReason.NO_DATE),  # no-separator date without a cue
    ("Тел. (343) 25-01-83", AbstainReason.NO_DATE),  # phone, not a date
    ("Годен до 06/15/2027", AbstainReason.CUE_WITHOUT_DATE),  # MM/DD next to a Russian cue
    ("18072024 Годен до", AbstainReason.CUE_WITHOUT_DATE),  # date before the cue
    ("0150524 03 2027", AbstainReason.NO_CUE),  # embossed blister, no cue in frame
]


@pytest.mark.parametrize(("text", "reason"), ABSTAINED)
def test_abstains(text, reason):
    result = parse_text(text)
    assert result.abstain_reason is reason
    assert result.confidence is Confidence.NONE
    assert result.iso_date is None
    assert result.valid_through is None


def test_mfg_is_never_the_expiry():
    result = parse_text("Дата изготовления 06.2024 Годен до 06.2027")
    assert result.iso_date == "2027-06"
    assert [(c.iso_date, c.kind) for c in result.candidates] == [
        ("2027-06", Kind.EXPIRY),
        ("2024-06", Kind.MFG),
    ]


def test_abstain_keeps_candidates_for_the_user():
    result = parse_text("EXP 06/07/2027")
    assert {c.iso_date for c in result.candidates} == {"2027-07-06", "2027-06-07"}


def test_uncued_date_is_a_candidate():
    result = parse_text("06.2027")
    assert [(c.iso_date, c.kind) for c in result.candidates] == [("2027-06", Kind.UNKNOWN)]


def test_chosen_fields():
    result = parse_text("Годен до: 06.2027")
    assert result.iso_date == "2027-06"
    assert result.precision is Precision.MONTH
    assert result.rule_id == "eaeu76_end_of_month"
    assert result.source is Source.OCR
    chosen = result.chosen
    assert chosen.raw == "06.2027"
    assert chosen.cue == "Годен до"


def test_day_precision_rule():
    result = parse_text("Годен до 15.03.2027")
    assert result.precision is Precision.DAY
    assert result.rule_id == "printed_day"


def test_to_dict_is_json_ready():
    import json

    data = parse_text("Годен до: 06.2027").to_dict()
    assert json.loads(json.dumps(data, ensure_ascii=False)) == data
    assert data["valid_through"] == "2027-06-30"
    assert data["confidence"] == "high"
    assert data["abstain_reason"] is None
