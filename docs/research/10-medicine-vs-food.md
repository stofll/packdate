# Medicines vs food as the first domain (research notes, 2026-09-25)

**Access date:** 2026-09-25. Every claim links a primary source (law text, official docs, LICENSE file). Items that could not be opened are marked **UNVERIFIED**.

## Executive takeaway

- **Russian DataMatrix codes do not carry the expiry date** — neither for medicines (МДЛП) nor for the marked food groups. The code holds GTIN + serial + crypto tail; expiry lives in the ЦРПТ database and is reachable only online with a market-participant token. "Decode DataMatrix → AI (17)" does **not** work for RU packs.
- **EU (FMD) and US (DSCSA) drug codes do carry expiry and batch** by law, so a GS1 element-string parser for AI (17)/(10) is still worth having.
- **Medicines are still the easier first domain**, because their printed date grammar is fixed by EAEU rules (month + year, end-of-month semantics). Food dates under ТР ТС 022/2011 range from hour precision to "годен N суток" relative to manufacture, plus "see the lid" references.

## 1. Medicines, МДЛП (ПП РФ №1556, п.5, current edition)

Code structure (fixed order): FNC1 → **(01)** GTIN 14 digits → **(21)** serial 13 chars + GS → **(91)** verification key 4 chars + GS → **(92)** verification code 44 chars.

- **No AI (17) expiry and no AI (10) batch in the code.** Paragraphs 7–10 of п.5 lost force on 2019-09-17 (ПП №1118); their former content is **UNVERIFIED**.
- Only GTIN and serial are duplicated as human-readable text. Batch and expiry date are reported to the monitoring system on introduction into circulation (annexes to ПП 1556).

## 2. Food groups under «Честный ЗНАК»

| Group | Code structure | Expiry in code |
|---|---|---|
| Dairy (ПП 2099, п.46, ed. 2026-08-18) | 01 + 21 (6 chars, first = country) + GS + 93 (4), optional 3103 (weight) | No |
| Beer (ПП 2173, п.45) | 01 + 21 (7) + GS + 93, optional 335Y (volume) | No |
| Soft drinks / juices (ПП 887, п.47) | 01 + 21 (13) + GS + 93 | No |
| Dietary supplements / БАД (ПП 886, п.49–50) | long: 01 + 21 (13) + 91 + 92 (83 chars); short: 01 + 21 + 93 (37 chars) | No |

- An experimental dairy format with a 13-char serial did include expiry; its emission stopped on 2021-01-20, but such codes stay valid until they leave circulation (markirovka.ru). The exact AI (17 / 7003) and a 72-hour threshold are **UNVERIFIED** (seen only in a search snippet).
- Packaged water (ПП 841) code structure: **UNVERIFIED**.
- Online path: True API `/codes/check` needs a participant Bearer token; the response reportedly has `expireDate` / `productionDate` (forum answer on markirovka.ru, not official docs). Terms for a third-party consumer app: **UNVERIFIED**.
- The consumer «Честный ЗНАК» app shows the expiry date. Its landing page says the code "stores" it, but under the marking rules the date comes from the ГИС МТ database, not the code.

## 3. International context

- **EU FMD (Reg. 2016/161).** Art. 4: the unique identifier includes product code, serial (≤ 20 chars), national number if required, **batch and expiry date**. Art. 5: encoded in Data Matrix ECC200. Expiry is readable offline from the code.
- **US DSCSA.** 21 USC 360eee(14): product identifier = NDC + serial + lot + **expiration date**, human- and machine-readable; 360eee-1 requires a 2D Data Matrix on the package.

## 4. Printed text rules

**Medicines** (EAEU Council Decision №76, as amended by Decision №32 of 2025-05-15):

- п.5: batch and expiry are mandatory on primary packaging including blisters, as «годен до…», «годен…» or «до…».
- п.6: on blisters and tube seams the formats `ММ ГГГГ`, `ММ.ГГГГ`, `ММ/ГГГГ`, `ММ_ГГГГ` and two-digit-year variants (`ММ ГГ`, `ММ.ГГ`, …) are allowed.
- п.30: month + year is shown and **the last day of the month is implied**; for shelf life under 12 months the day is shown too.

**Food** (ТР ТС 022/2011):

- Art. 4.7: shelf life ≤ 72 h → «годен до» + hour, day, month; 72 h – 3 months → day, month, year; > 3 months → «годен до конца» + month and year, or a full date.
- «годен N суток/месяцев/лет» is allowed, so expiry must be derived from the manufacture date.
- Instead of the date, the label may point to where it is printed.
- Synonyms: «срок годности», «употребить до», and "similar in meaning" wording.
- Art. 4.6: manufacture date has the same precision as the expiry; for drinks it may be «дата розлива».

Distribution of print technologies (CIJ / laser / embossing) between drugs and food: **UNVERIFIED**.

## 5. DataMatrix decoders

| Library | License | DataMatrix / GS1 | Bindings |
|---|---|---|---|
| zxing-cpp | Apache-2.0 | ECC200; `ContentType.GS1`; text modes `HRI` (default), `Escaped` (GS → `<GS>`), `Hex` / bytes | PyPI `zxing-cpp` 3.1.1 (2026-07-29); Android / iOS wrappers |
| pylibdmtx | MIT | DataMatrix | Python |
| libdmtx | BSD-2-Clause | DataMatrix | C |
| OpenCV BarcodeDetector | not rechecked | EAN-8/13, UPC-A/E only — **no DataMatrix** | — |
| Google ML Kit | proprietary (Google APIs ToS) | Data Matrix supported | on-device, no Python |

- AI (91), (92), (93) are not fixed-length in GS1, so field ends are found by GS. Parse raw bytes or `Escaped` text with our own code. `HRI` behaviour on RU crypto tails: **UNVERIFIED**.
- Robustness on phone photos: anecdotal only. zxing-cpp issue #782 reports roughly half of small low-resolution codes decoded; the maintainer suggested 200% upscale, dilate, and threshold tuning.

## 6. Recommendation

Start with medicines. Pipeline:

1. Decode DataMatrix (zxing-cpp) and parse AIs.
2. If AI (17) is present (EU/US packs) → date from the code, high confidence.
3. RU pack (01/21/91/92) → keep GTIN + serial as identity / dedup key; no date from the code.
4. OCR «Годен до» / «до» and «Серия» / «Лот» lines.
5. Normalize `ММ.ГГ(ГГ)` to the last day of the month; use the full date when the day is printed.
6. Plausibility check.

Risks:

- Accuracy on RU packs depends entirely on OCR.
- Embossed dates on blisters and tube seams are hard for OCR; blisters often lose their box.
- Old stock without a code; the mandatory-marking timeline and share of unmarked stock are **UNVERIFIED**.
- Printed date and МДЛП record can disagree (markirovka.ru example: «07.22» vs «07.07.22»).
- БАД are marked as food with two code variants; whether their dates follow ТР ТС 022 rather than EAEU №76: **UNVERIFIED**.
- Transition period of Decision №32/2025: older packs may use other formats.
- Official expiry via API requires a participant token.

## Sources

| URL | Confirms |
|---|---|
| https://base.garant.ru/72136156/ | ПП 1556: п.5 (01/21/91/92), GTIN + serial as text, expiry reported to the system |
| https://www.consultant.ru/document/cons_doc_LAW_371342/642d1ea3c72f69619538c3fee9af61de7a81e0d0/ | ПП 2099: п.46, п.39, п.42 |
| https://markirovka.ru/knowledge/fast_start/start/sostav-koda-markirovki-molochnoy-produktsii | Old dairy format with expiry, stopped 2021-01-20 |
| https://markirovka.ru/knowledge/tovarnye-gruppy/pivo-pivniye-napitki/sostav-koda-markirovki-pivo | Beer code (ПП 2173) |
| https://markirovka.ru/knowledge/tovarnye-gruppy/bezalcohol-napitki/sostav-koda-markirovki-ba-napitki | Soft drinks code (ПП 887) |
| https://markirovka.ru/knowledge/tovarnye-gruppy/badi/sostav-koda-markirovki-bad | БАД code (ПП 886), two structures |
| https://markirovka.ru/community/developers/est-li-kakoe-to-rest-api-dlya-polucheniya-informatsii-o-tovare--90 | True API `/codes/check`, token, `expireDate` (forum answers) |
| https://markirovka.ru/community/lekarstva-bady-i-antiseptiki/ischeslenie-sroka-godnosti-lekarstvennykh-preparatov | Operator position: expiry = last day of month |
| https://xn--80ajghhoc2aj1c8b.xn--p1ai/potrebitelyam/ | Consumer app shows expiry |
| https://www.consultant.ru/document/cons_doc_LAW_207463/bf1a5662b9086f8bef30460195e7520e1a9014ab/ | EAEU №76 п.5, п.6 (formats, blister, tube) |
| https://www.consultant.ru/document/cons_doc_LAW_207463/4671afcc16aa2d4873cbe8b84c0ca1d50a103d97/ | EAEU №76 п.30 (last day of month; day if < 12 months) |
| https://sudact.ru/law/reshenie-komissii-tamozhennogo-soiuza-ot-09122011-n_3/tr-ts-0222011/statia-4/4.7/ | ТР ТС 022/2011 Art. 4.7 |
| https://sudact.ru/law/reshenie-komissii-tamozhennogo-soiuza-ot-09122011-n_3/tr-ts-0222011/statia-4/4.6/ | ТР ТС 022/2011 Art. 4.6 |
| https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0161 | FMD Art. 4–5 |
| https://www.govinfo.gov/content/pkg/USCODE-2023-title21/html/USCODE-2023-title21-chap9-subchapV-partH-sec360eee.htm | DSCSA product identifier |
| https://www.govinfo.gov/content/pkg/USCODE-2023-title21/html/USCODE-2023-title21-chap9-subchapV-partH-sec360eee-1.htm | DSCSA 2D Data Matrix |
| https://github.com/zxing-cpp/zxing-cpp | Apache-2.0, DataMatrix ECC200 |
| https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/master/core/src/ReaderOptions.h | Text modes HRI / Escaped |
| https://raw.githubusercontent.com/zxing-cpp/zxing-cpp/master/core/src/ContentType.h | `ContentType::GS1` |
| https://pypi.org/project/zxing-cpp/ | Python package 3.1.1 |
| https://raw.githubusercontent.com/NaturalHistoryMuseum/pylibdmtx/master/LICENSE.txt | pylibdmtx MIT |
| https://raw.githubusercontent.com/dmtx/libdmtx/master/LICENSE | libdmtx BSD-2-Clause |
| https://docs.opencv.org/4.x/d6/d25/tutorial_barcode_detect_and_decode.html | OpenCV: EAN/UPC only |
| https://developers.google.com/ml-kit/vision/barcode-scanning | ML Kit supports Data Matrix |
| https://github.com/zxing-cpp/zxing-cpp/issues/782 | Small low-quality codes decode ~half the time (anecdotal) |

## UNVERIFIED

- Old dairy code format (AI 17 / 7003, 72 h threshold); former content of ПП 1556 п.5 paragraphs 7–10.
- Packaged water code structure (ПП 841).
- True API terms for a third-party consumer app.
- Whether drug manufacturers voluntarily add AI (17)/(10) to RU codes.
- OpenCV license (from memory); zxing-cpp `HRI` mode on RU crypto tails.
- Effective date and transition period of EAEU Decision №32/2025; EAEU Recommendation №2/2020 text.
- Print technologies used for drugs vs food.
- Mandatory drug-marking dates and share of unmarked old stock.
- Date format rules for БАД.
- Systematic phone-photo DataMatrix decode benchmarks.
