# After recognition: parse → confirm → store → remind (research notes, 2026-09-25)

**Access date:** 2026-09-25. Items not confirmed from a primary source are marked **UNVERIFIED**.

## Executive takeaway

- **A month-precision date cannot be collapsed to one ISO day without a rule.** Cosmetics (ТР ТС 009/2011) «До 06.2027» means expired on 2027-05-31; food (ТР ТС 022/2011) «годен до конца 06.2027» means 2027-06-30; medicines (EAEU №76 п.30, see [10](10-medicine-vs-food.md)) imply the last day of the stated month. Store `precision` + `valid_through` + `rule_id`.
- **«Употребить до» in ТР ТС 022 is a synonym of «годен до»**, not an equivalent of EU "use by". Do not infer `kind=use_by` from the Russian cue.
- **None of the four reviewed apps keeps raw OCR output next to the user-confirmed value** (expirationradar overwrites on edit). packdate needs that layer to turn corrections into fixtures.

## 1. Date-semantics edge cases for the parser

| # | Case | Handling | Source |
|---|---|---|---|
| 1 | «Годен до конца» + month/year (food, > 3 months) | precision = month; valid_through = last day of month | ТР ТС 022 Art. 4.7 п.1(3) [S1] |
| 2 | «Годен до» + hour, day, month (≤ 72 h) | precision = hour; year may be missing and must be inferred | [S1] п.1(1) |
| 3 | «Годен N суток / мес. / лет», «годен N часов» | `mfg` + duration → derived date, flagged `derived` | [S1] п.2 |
| 4 | «Срок годности не ограничен при соблюдении условий хранения» | `never_expires` flag, not an ISO date | [S1] п.4 |
| 5 | Cue followed by a location ("см. на крышке") | cue without date → abstain, ask for another photo | [S1] п.3; ТР ТС 009 Art. 9 [S3]; EU 1169 Annex X 1(b) [S4] |
| 6 | «Употребить до», «срок годности» = «годен до» | RU `kind` = generic expiry, no use_by / best_before split | [S1] п.5 |
| 7 | «Дата изготовления» with hour / day / month-year; «год изготовления» for sugar; bottling or egg sorting date | `kind=mfg` with precision; never confuse with expiry | ТР ТС 022 Art. 4.6 [S2] |
| 8 | Cosmetics «До 06.2027» | expires on the **last day of the previous month** (2027-05-31); «До дд.мм.гггг» excludes that day | ТР ТС 009 Art. 9 [S3] |
| 9 | Cosmetics «Дата изготовления» + «Срок годности N мес.» | derived from mfg + duration | [S3] |
| 10 | EU "Best before" (with day) / "Best before end" (month-year or year) | precision day / month / year; year-only → end of year | EU 1169/2011 Annex X п.1(a),(c) [S4] |
| 11 | EU "use by" = safety, "best before" = quality; after "use by" the food is deemed unsafe | affects `kind` and reminder tone | Art. 24(1) [S4]; UK FSA [S5] |
| 12 | "Frozen on …" | separate `kind` = frozen_on, not an expiry | Annex X п.3 [S4] |
| 13 | Storage-dependent shelf life; after-opening storage | storage condition as a separate field; after-opening is its own rule | 1169 Art. 25(2) [S4]; ТР ТС 022 Art. 4.1 (**UNVERIFIED**) |
| 14 | Cosmetics PAO symbol + N months (shelf life > 30 months) | `pao_months`; date = user-entered opening date + N | EU 1223/2009 Art. 19(1)(c) [S6] |
| 15 | GS1 AI (17) with day "00" | GS1 regex allows day 00 [S7]; healthcare disallows "00" since 2025-01-01 [S8]; "00" = last day of month per search snippet only [S9] | [S7][S8][S9] |
| 16 | Frozen / thawed item | expiry recalculated on move in/out of freezer; −1 = never | grocy `StockService.php` [R1] |

expirationradar maps a month-only date to the **first** day of the month ("pessimistic", `dates.py`) [R4] — yet another policy; packdate must make its policy explicit per `rule_id`.

## 2. How open pantry apps model expiry (all four MIT)

- **grocy** [R1] (PHP):
  - `products` is the template: `default_best_before_days`, `_after_open`, `_after_freezing`, `_after_thawing`, `due_type`. `stock` is the batch: `best_before_date`, `purchased_date`, `open`, `opened_date`, `location_id`, `stock_id`.
  - `due_type`: 1 = best before, 2 = expiration; only type 2 counts as expired.
  - "Never expires" = `default_best_before_days = -1`, stored as `2999-12-31`.
  - On opening: new date = today + `after_open`, **capped at the original date**.
  - "Due soon" = `stock_due_soon_days = 5`.
- **Thigas-Tech/pantry_app** [R2] (Flutter): `InventoryItem` with `barcode` (FK), `expiry_date` (ISO, nullable, "last safe day inclusive"), `location`, `quantity/unit`, `date_added`. Product template separate from shelf instance; retention-based deletion.
- **officialfshot-web/ShelfLife** [R3] (Android) — mostly anti-patterns:
  - hard-coded confidence: 0.9 if a date is found, else 0.3;
  - generic DD/MM/YYYY pattern checked before cue patterns (EXP, Best before);
  - past dates dropped, so expired items cannot be recognized;
  - `Calendar` apparently lenient (not verified by running);
  - **if no date is found, silently uses today + 7 days**;
  - no date editing in the confirm overlay.
- **Ps23102004/expirationradar** [R4] (Python) — best provenance model:
  - every field is `Field{value, source, confidence}`;
  - `source` priority BARCODE > OCR > VISION; USER overrides all; ESTIMATED lowest and shown with an explicit label;
  - `parse_dates` returns a sorted candidate list;
  - confidence from a table: pattern kind × cue present;
  - edits set `source=USER, confidence=1` **and lose the original value**.

## 3. Human-in-the-loop confirmation

- **Apple HIG, Machine learning** [G1]: calibrate confidence before showing it; show it as understandable categories; let people correct with familiar controls and remember corrections; let them undo a correction; "Never rely on corrections to make up for low-quality results".
- **Google PAIR, Explainability + Trust** [G2]: display options — categories, N-best (useful at low confidence), numbers (risky), visualization; weigh the cost of errors; overstated confidence leads to blind acceptance.
- **AWS A2I + Textract** [G3], reference only (A2I no longer accepts new customers): route to a human when key confidence < threshold (`ImportantFormKeyConfidenceCheck`), when a key (our date cue) is missing (`MissingImportantFormKey`), and a random `Sampling` share for audit.

Implications for packdate:

- categories `high` / `check` / `none` instead of percentages;
- crop with bbox next to the recognized date;
- candidates as chips (N-best), one-tap selection;
- at low confidence nothing preselected; never auto-save;
- explicit `abstain_reason`: `cue_without_date`, `ambiguous_dmy`, `mfg_only`, ….

## 4. Storage and feedback loop

- **Reference: Label Studio** [G4] (Apache-2.0) keeps predictions separate from annotations; a prediction has `model_version`, `score`, `result`; boxes in percent of `original_width/height`.
- For packdate: store `extraction` (immutable pipeline output + versions) separately from `confirmation` (the human decision). A correction + crop can be exported as a labeled fixture: `photo`, `raw_ocr`, `expected{iso, kind, precision}`.
- Privacy (recommendation, not a citation): photos local by default; strip EXIF / GPS; export to a dataset only with explicit opt-in per item. Apple HIG [G1]: "Always secure people's information".

## 5. Reminders

- **pantry_app** [R2]: two local notifications per item (1 day before and on the day, 09:00); IDs `itemId*2` / `itemId*2+1`; `inexactAllowWhileIdle`; reschedule everything on start, skip past dates.
- **ShelfLife** [R3]: WorkManager every 12 h; "soon" = 0..3 days; notify at ≤ 1 day.
- **grocy** [R1]: user setting "due soon" = 5 days.
- **expirationradar** [R4]: daily digest, `days=5`, idempotent per day.
- Platform limits: Android 14 denies exact alarms by default [P1]; iOS keeps 64 pending notifications — documented only for legacy `UILocalNotification` [P2]. A daily digest with rolling rescheduling is more robust than one notification per item.

## Proposed minimal data model

```
product(id, barcode?, gtin?, name, category?,
        default_shelf_days?, default_days_after_open?, pao_months?)   -- template, as in grocy
item(id, product_id?, serial?, location, quantity,
     status(active|consumed|discarded), opened_at?, added_at)
expiry(item_id, kind(use_by|best_before|expiry|mfg|frozen_on|unknown),
       iso_date?, precision(hour|day|month|year),
       valid_through?,                   -- last good day after applying the rule
       rule_id, never_expires bool,
       derived_from?{mfg_date, shelf_value, shelf_unit},
       storage_condition?, source(datamatrix|ocr|user|derived|estimated),
       confirmed bool)
extraction(id, item_id?, image_path (local), crop_path?, bboxes json,
           raw_ocr_text, ocr_backend+version, parser_version,
           result json {iso_date, kind, confidence, candidates, abstain_reason},
           created_at)                   -- immutable
confirmation(extraction_id, action(accept|pick_candidate|edit|reject),
             final_value json, edited_fields, confirmed_at,
             export_consent bool)        -- label for fixtures
reminder_policy(scope(global|category|product), days_before[], hour_local)
```

On opening: `valid_through = min(original, opened_at + days_after_open)` (grocy rule [R1]).

## Sources

| ID | Source |
|---|---|
| S1 | ТР ТС 022/2011 Art. 4.7 — https://www.consultant.ru/document/cons_doc_LAW_124614/b3dc5be1288e1b6de39f7097b87c4a4dba39d263/ |
| S2 | ТР ТС 022/2011 Art. 4.6 — https://www.consultant.ru/document/cons_doc_LAW_124614/475339efd09154e577d5c9cabdaf4652db8cf825/ |
| S3 | ТР ТС 009/2011 Art. 9 (meganorm copy) — https://meganorm.ru/Data2/1/4293800/4293800253.htm |
| S4 | EU 1169/2011 Art. 24, 25, Annex X — https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32011R1169 |
| S5 | UK — https://www.gov.uk/understanding-food-labelling/best-before-and-use-by-dates |
| S6 | EU 1223/2009 Art. 19 — https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32009R1223 |
| S7 | GS1 AI 17 — https://ref.gs1.org/ai/17 |
| S8 | GS1 UK — https://www.gs1uk.org/insights/news/change-of-date-format-for-regulated-healthcare-products |
| S9 | GS1 GSCN 21-040 — https://www.gs1.org/docs/barcodes/GSCN_21-040_HealthcareExpDate.pdf (search snippet only) |
| R1 | grocy: `services/StockService.php`, `views/productform.blade.php`, `config-dist.php`, `grocy.openapi.json` — https://github.com/grocy/grocy |
| R2 | pantry_app: `lib/models/inventory_item.dart`, `lib/services/notification_service.dart` — https://github.com/Thigas-Tech/pantry_app |
| R3 | ShelfLife: `ml/ExpiryDateScanner.kt`, `ui/screens/ScannerScreen.kt`, `notifications/ExpiryCheckWorker.kt` — https://github.com/officialfshot-web/ShelfLife |
| R4 | expirationradar: `expirationradar/models.py`, `dates.py`, `web/app.js` — https://github.com/Ps23102004/expirationradar |
| G1 | https://developer.apple.com/design/human-interface-guidelines/machine-learning |
| G2 | https://pair.withgoogle.com/chapter/explainability-trust/ |
| G3 | https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-json-humantaskactivationconditions-textract-example.html |
| G4 | https://github.com/HumanSignal/label-studio/blob/develop/docs/source/guide/predictions.md |
| P1 | https://developer.android.com/about/versions/14/changes/schedule-exact-alarms |
| P2 | https://developer.apple.com/documentation/uikit/uilocalnotification |

## UNVERIFIED

1. GS1 General Specifications wording that day "00" = last day of month, and whether the 2025 "00" ban extends beyond regulated healthcare (only S9 search snippet; S8 confirms healthcare).
2. ТР ТС 022 Art. 4.1 requirement to state after-opening storage (search snippet only).
3. Whether the meganorm copy of ТР ТС 009 matches the current official EAEU text.
4. Microsoft HAX guideline titles (Amershi et al., CHI 2019) — pages blocked.
5. The 64-notification limit for the current `UNUserNotificationCenter` API.
6. Full text of the Android 14 exact-alarms page (only the heading confirmed).
7. ShelfLife `Calendar` leniency (`32/13` rollover) — inferred from code, not run.
8. Real packs with several shelf lives per storage regime ("+2…+6 °C — N days; −18 °C — M months") — no regulation found for a specific format.
