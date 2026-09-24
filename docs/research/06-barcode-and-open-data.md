# Barcodes and open product data (research notes, 2026-09-25)

## Executive takeaway

Barcode → product **identity** (name, brand, ingredients). It does **not** give the expiry of that physical pack. Expiry needs OCR (or manual entry) on the unit.

For a permissive OSS project, **Open Food Facts** (and Beauty/Products/Pet Food Facts) is the only practical open, redistributable data stack (ODbL + DbCL; images CC-BY-SA). Commercial barcode APIs (UPCitemdb, Go-UPC, Barcode Lookup, EAN-Search) generally **forbid** redistributing data into a public mirror.

Russia coverage on OFF is modest (~36.5k products tagged Russia at research time vs millions of shelf SKUs) → expect high unknown rates and a “add product / contrib back” UX.

## Recommended stack

| Layer | Choice |
|-------|--------|
| Decode | zxing-cpp / flutter_zxing (Apache/MIT) |
| Product DB | OFF API v3 + local SQLite from official dumps/delta |
| Expiry | Separate inventory table (not OFF) |
| Avoid in public DB | Proprietary barcode API dumps mixed with OFF |

## Key links

- https://world.openfoodfacts.org/data
- https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/
- https://github.com/openfoodfacts/openfoodfacts-dart
- https://github.com/openfoodfacts/smooth-app
- https://github.com/zxing-cpp/zxing-cpp
- https://github.com/khoren93/flutter_zxing

See also `02-full-report.md` for the comparison table and legal README checklist.
