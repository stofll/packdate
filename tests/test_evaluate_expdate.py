"""Metric/label regressions using synthetic annotations; no model download."""

import importlib.util
from pathlib import Path

import pytest

from packdate.recognize import TextLine

spec = importlib.util.spec_from_file_location(
    "evaluate_expdate", Path(__file__).resolve().parents[1] / "datasets/evaluate_expdate.py"
)
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def annotation(text, parts):
    return {
        "transcription": text,
        "dmy_ann": [
            {"cls": kind, "transcription": value, "bbox": [i * 10, 0, i * 10 + 8, 10]}
            for i, (kind, value) in enumerate(parts)
        ],
    }


@pytest.mark.parametrize("text,parts,expected,issue", [
    ("2021.08.03", [("year", "2021"), ("month", "08"), ("day", "03")], "2021-08-03", None),
    ("03/08/21", [("day", "03"), ("month", "08"), ("year", "21")], "2021-08-03", None),
    ("JUN 2023", [("month", "JUN"), ("year", "2023")], "2023-06", None),
    ("08/03", [("month", "08"), ("day", "03")], None, "missing_year_or_month"),
    ("2021.02.29", [("year", "2021"), ("month", "02"), ("day", "29")], None, "invalid_calendar_date"),
    ("2021.08.03", [("year", "2021"), ("month", "09"), ("day", "03")], None, "component_transcription_disagreement"),
    ("2021.08.03", [("year", "2021"), ("month", "08"), ("month", "03")], None, "invalid_components"),
])
def test_expected_is_independent_and_does_not_guess(text, parts, expected, issue):
    assert bench.expected_date(annotation(text, parts)) == (expected, issue)


@pytest.mark.parametrize("actual,match", [
    ("EXP 2021 / 08 / 03", True),
    ("20210803", True),
    ("2021.08.04", False),
    ("2O21.08.03", False),
    ("1202108034", False),
    ("", False),
])
def test_transcription_matching(actual, match):
    assert bench.transcription_present("2021.08.03", actual) is match


def test_matching_text_elsewhere_in_image_does_not_count():
    lines = [TextLine("2021.08.03", 0.99, (0, 0, 90, 20)),
             TextLine("2021.08.04", 0.99, (0, 80, 90, 100))]
    text = bench.region_text(lines, [0, 80, 100, 100])
    assert text == "2021.08.04"
    assert not bench.transcription_present("2021.08.03", text)


def test_month_precision_is_not_an_exact_day_and_unknown_is_not_negative():
    assert bench.outcome({"iso_date": "2021-08"}, "2021-08-03") == "false"
    assert bench.outcome({"iso_date": "2021-08"}, None) == "unscored_label"
    assert bench.outcome({"iso_date": None}, "2021-08-03") == "abstain"


def test_errors_and_unscored_labels_do_not_inflate_accuracy():
    row = {
        "expected_iso": "2021-08-03", "label_issue": None, "outcome": "exact",
        "full_text_match": True, "crop_text": None, "candidate_match": True,
        "result": {"abstain_reason": None},
    }
    summary = bench.summarize([
        row, {"error": "unreadable"},
        {**row, "expected_iso": None, "label_issue": "missing_year_or_month", "outcome": "unscored_label"},
        {**row, "outcome": "false"},
    ])
    assert summary["images"] == 4
    assert summary["errors"] == 1
    assert summary["iso_scored"] == 2
    assert summary["exact_printed_iso_rate"] == 0.5
    assert summary["false_on_committed"] == 0.5
    assert summary["oracle_crop_scored"] == 0
    assert bench.summarize([])["exact_printed_iso_rate"] is None


def test_reparse_uses_full_frame_text_without_injecting_expiry_cue():
    row = {
        "expected_iso": "2021-08-03", "label_issue": None,
        "ocr_text": "2021.08.03", "annotation": {"transcription": "2021.08.03"},
        "full_text_match": True, "crop_text": None,
    }
    original = {"schema_version": 1, "complete": True, "rows": [row]}
    replay = bench.reparse_report(original)
    assert replay["rows"][0]["result"]["iso_date"] is None
    assert replay["rows"][0]["candidate_match"] is True
    assert replay["summary"]["pipeline_outcomes"] == {"abstain": 1}
    assert "result" not in original["rows"][0]
    with pytest.raises(ValueError, match="complete"):
        bench.reparse_report({**original, "complete": False})
