"""Text normalization for OCR output.

Both steps after NFKC map one character to one character, so offsets in the
normalized text and in the folded text are the same.
"""

from __future__ import annotations

import re
import unicodedata

# Letters OCR confuses with digits. Applied only inside digit runs.
_DIGIT_CONFUSABLES = str.maketrans(
    {
        "O": "0",
        "o": "0",
        "О": "0",  # Cyrillic
        "о": "0",  # Cyrillic
        "l": "1",
        "I": "1",
        "|": "1",
    }
)
_CONFUSABLE_CHARS = "OoОоlI|"
_RUN = re.compile(rf"[\d{_CONFUSABLE_CHARS}]+(?:[./\-_,][\d{_CONFUSABLE_CHARS}]+)*")

# Cyrillic and Latin letters that look alike, folded to one Latin form so that
# cues match whichever script OCR picked ("ЕХР" vs "EXP", "Cepия" vs "Серия").
_HOMOGLYPHS = str.maketrans(
    {
        "а": "a",
        "в": "b",
        "е": "e",
        "ё": "e",
        "к": "k",
        "м": "m",
        "н": "h",
        "о": "o",
        "р": "p",
        "с": "c",
        "т": "t",
        "у": "y",
        "х": "x",
    }
)


def normalize(text: str) -> str:
    """NFKC, then fix letter/digit confusions inside digit runs."""
    text = unicodedata.normalize("NFKC", text)
    return _RUN.sub(lambda m: _fix_run(text, m), text)


def _fix_run(text: str, m: re.Match[str]) -> str:
    run = m.group()
    if sum(ch.isdigit() for ch in run) < 2:
        return run
    start, end = 0, len(run)
    # A confusable at the edge that touches a letter belongs to a word: "до06.2027".
    if m.start() > 0 and text[m.start() - 1].isalpha():
        while start < end and run[start] in _CONFUSABLE_CHARS:
            start += 1
    if m.end() < len(text) and text[m.end()].isalpha():
        while end > start and run[end - 1] in _CONFUSABLE_CHARS:
            end -= 1
    return run[:start] + run[start:end].translate(_DIGIT_CONFUSABLES) + run[end:]


def fold(text: str) -> str:
    """Lowercase and fold homoglyphs, for matching only (same length as input)."""
    lowered = text.lower()
    if len(lowered) != len(text):  # rare characters that expand on lowercasing
        lowered = "".join(ch.lower() if len(ch.lower()) == 1 else ch for ch in text)
    return lowered.translate(_HOMOGLYPHS)
