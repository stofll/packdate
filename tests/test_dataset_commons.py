"""The download helper must not replace a person's reviewed label with a draft."""

import importlib.util
import json
from pathlib import Path


def test_download_preserves_existing_labels_and_only_adds_missing(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "commons_ru_drugs", Path(__file__).resolve().parents[1] / "datasets/commons_ru_drugs.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "__file__", str(tmp_path / "commons_ru_drugs.py"))
    draft = {"valid_through": "2027-06-30", "notes": "draft"}
    (tmp_path / "commons_ru_drugs.labels.json").write_text(
        json.dumps({"labels": {"File:existing.jpg": draft, "File:new.jpg": draft}}),
        encoding="utf-8",
    )
    images = tmp_path / "images"
    images.mkdir()
    corrected = '{"valid_through": null, "notes": "human reviewed negative"}\n'
    (images / "existing.json").write_text(corrected, encoding="utf-8")
    rows = [{"title": "File:existing.jpg", "file": "existing.jpg"},
            {"title": "File:new.jpg", "file": "new.jpg"}]

    module.write_labels(rows, images)
    assert (images / "existing.json").read_text(encoding="utf-8") == corrected
    assert json.loads((images / "new.json").read_text(encoding="utf-8")) == draft
    module.write_labels(rows, images)
    assert (images / "existing.json").read_text(encoding="utf-8") == corrected
