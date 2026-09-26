"""Download photos of Russian-market medicine packs from Wikimedia Commons.

Sources: Category:Pharmaceutical drugs of Russia and
Category:Photographs by Retired electrician/medical (checked 2026-09-25:
177 files; CC0, CC BY-SA 4.0, CC BY 3.0/4.0, public domain).

Writes `<out>/images/*.jpg` (1280 px wide thumbnails) and `<out>/manifest.json`
with title, license, author and source URL per file — keep it for attribution.
Photos have no expiry labels; see apps/demo/evaluate.py for the label format.

    python datasets/commons_ru_drugs.py D:/packdate-data/commons-ru-drugs
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
CATEGORIES = [
    "Category:Pharmaceutical drugs of Russia",
    "Category:Photographs by Retired electrician/medical",
]
WIDTH = 1280
USER_AGENT = "packdate-dataset-script/0.1 (https://github.com/stofll/packdate)"


def api(**params) -> dict:
    data = urllib.parse.urlencode({"format": "json", **params}).encode()
    req = urllib.request.Request(API, data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def category_files(category: str) -> list[str]:
    files, cont = [], None
    while True:
        params = {"action": "query", "list": "categorymembers", "cmtitle": category}
        params |= {"cmtype": "file", "cmlimit": "500"}
        if cont:
            params["cmcontinue"] = cont
        r = api(**params)
        files += [m["title"] for m in r["query"]["categorymembers"]]
        cont = r.get("continue", {}).get("cmcontinue")
        if not cont:
            return files


def file_info(titles: list[str]) -> list[dict]:
    r = api(
        action="query",
        titles="|".join(titles),
        prop="imageinfo",
        iiprop="url|size|extmetadata",
        iiurlwidth=str(WIDTH),
        iiextmetadatafilter="LicenseShortName|LicenseUrl|Artist",
    )
    rows = []
    for page in r["query"]["pages"].values():
        ii = page["imageinfo"][0]
        meta = ii.get("extmetadata", {})
        rows.append(
            {
                "title": page["title"],
                "source": ii["descriptionurl"],
                "license": meta.get("LicenseShortName", {}).get("value"),
                "license_url": meta.get("LicenseUrl", {}).get("value"),
                "author": re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip(),
                "thumb_url": ii.get("thumburl") or ii["url"],
            }
        )
    return rows


def fetch(url: str, attempts: int = 4) -> bytes:
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(5 * (attempt + 1))
    raise AssertionError("unreachable")


def local_name(title: str) -> str:
    stem = title.removeprefix("File:").rsplit(".", 1)[0]
    safe = re.sub(r"[^\w\-]+", "_", stem).strip("_")[:80]
    return f"{safe}_{hashlib.sha1(title.encode()).hexdigest()[:6]}.jpg"


def main(out: Path) -> int:
    titles = sorted({t for c in CATEGORIES for t in category_files(c)})
    titles = [t for t in titles if t.lower().endswith((".jpg", ".jpeg", ".png"))]
    rows = [row for i in range(0, len(titles), 40) for row in file_info(titles[i : i + 40])]

    images = out / "images"
    images.mkdir(parents=True, exist_ok=True)
    for n, row in enumerate(rows, 1):
        row["file"] = local_name(row["title"])
        target = images / row["file"]
        if not target.exists():
            target.write_bytes(fetch(row["thumb_url"]))
            time.sleep(0.5)  # be polite to upload.wikimedia.org
        print(f"[{n}/{len(rows)}] {row['license']:<14} {row['file']}")

    (out / "manifest.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_labels(rows, images)
    return 0


def write_labels(rows: list[dict], images: Path) -> None:
    """Add missing draft sidecars; preserve existing labels and human corrections."""
    labels_path = Path(__file__).with_name("commons_ru_drugs.labels.json")
    labels = json.loads(labels_path.read_text(encoding="utf-8"))["labels"]
    by_title = {row["title"]: row["file"] for row in rows}
    written, kept = 0, 0
    for title, label in labels.items():
        if title in by_title:
            sidecar = (images / by_title[title]).with_suffix(".json")
            try:
                with sidecar.open("x", encoding="utf-8") as stream:
                    stream.write(json.dumps(label, ensure_ascii=False, indent=2))
                written += 1
            except FileExistsError:
                kept += 1
    print(f"labels written: {written}; existing labels preserved: {kept}; catalog labels: {len(labels)}")


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "commons-ru-drugs")))
