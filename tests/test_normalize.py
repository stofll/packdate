import pytest

from packdate.parse.normalize import fold, normalize


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("O6.2O27", "06.2027"),
        ("l2/2026", "12/2026"),
        ("0б.2027", "0б.2027"),  # unknown confusables are left alone
        ("О6.2О27", "06.2027"),  # Cyrillic О
        ("до06.2027", "до06.2027"),  # «о» belongs to the word
        ("Lot 0624", "Lot 0624"),  # no digit run to fix
        ("Годен до", "Годен до"),
        ("０６．２０２７", "06.2027"),  # full-width → NFKC
    ],
)
def test_normalize(text, expected):
    assert normalize(text) == expected


def test_fold_keeps_length_and_matches_scripts():
    for text in ["ЕХР", "EXP", "Серия", "Cepия", "Годен до"]:
        assert len(fold(text)) == len(text)
    assert fold("ЕХР") == fold("EXP")
    assert fold("Серия") == fold("Cepия")
