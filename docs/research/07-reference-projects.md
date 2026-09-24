# Reference projects and MVP shape (research notes, 2026-09-25)

## Fork vs inspiration

| Repo | Role |
|------|------|
| [openfoodfacts/smooth-app](https://github.com/openfoodfacts/smooth-app) | Flutter + barcode + OFF reference — **not** a pantry/OCR fork base |
| [Thigas-Tech/pantry_app](https://github.com/Thigas-Tech/pantry_app) | Best Flutter pantry reference (OFF, manual expiry, notifications), MIT |
| [begiedz/Pantrly](https://github.com/begiedz/Pantrly) | Minimal RN + OFF |
| [officialfshot-web/ShelfLife](https://github.com/officialfshot-web/ShelfLife) | Android on-device expiry OCR (ML Kit + regex), MIT |
| [Ps23102004/expirationradar](https://github.com/Ps23102004/expirationradar) | Tiered pipeline + provenance UI |
| [dadaloop82/EverShelf](https://github.com/dadaloop82/EverShelf) | Product/UX inspiration (PWA + AI OCR) |
| [grocy/grocy](https://github.com/grocy/grocy) | Inventory model inspiration |
| [felizang/expdate](https://github.com/felizang/expdate) | ExpDate architecture + dataset |
| [AnanasPizzaMigliore/ExpRec](https://github.com/AnanasPizzaMigliore/ExpRec) | Mobile ExpDate-style research pipeline |
| [HieuNTg/Date-Recognition](https://github.com/HieuNTg/Date-Recognition) | Ideas only — **no LICENSE** (do not copy code) |
| [kivancgunduz/expiration-date-detection](https://github.com/kivancgunduz/expiration-date-detection) | MIT, small educational |

## Difficulty

| Block | Difficulty |
|-------|------------|
| Barcode | Easy |
| OFF lookup | Easy–medium (RU gaps) |
| Expiry OCR | Hard |
| Reminders / inventory UX | Medium |

Market pattern (BEEP / Pantrly / pantry_app): barcode + **manual** date in v0; OCR as assist + confirm later.

## Suggested public roadmap

1. Scaffold + parse + fixtures  
2. Barcode + OFF (if building an app)  
3. Reminders → v0.1 **without** OCR in the critical path  
4. OCR experimental + confirm  
5. Dataset / good-first-issues  

Details: `02-full-report.md`, `03-ocr-verdict.md`.
