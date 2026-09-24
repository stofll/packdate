# Исследование: OSS-проект «срок годности на фото + штрихкод»

**Дата:** 25 сентября 2026 (МСК)  
**Цель:** фундамент для своего open-source проекта (не SaaS)

---

## Краткий вывод

Сделать публичный MVP **реально за 2–3 недели**, если в v0 штрихкод + карточка товара + **ручной ввод даты**, а OCR срока — отдельный experimental-слой с обязательным подтверждением.

| Блок | Сложность | Почему |
|------|-----------|--------|
| Сканер штрихкода | Легко | zxing-cpp / flutter_zxing / ML Kit — зрелые |
| База товара по EAN | Легко–средне | Open Food Facts бесплатен и легален для OSS; в РФ покрытие слабое |
| OCR срока годности | Сложно | Штампы, блики, форматы дат, «годен до» vs дата производства |
| Напоминания / инвентарь | Средне | Локальные уведомления + SQLite — известный путь |

**Главное ограничение:** штрихкод **не даёт** срок конкретной пачки. Он даёт identity SKU. Срок почти всегда — OCR (или руки) с этой единицы.

Готовой зрелой библиотеки «expiry OCR» почти нет (репо на GitHub обычно 0–11★). Ниша своего OSS — **парсер дат + RU-подсказки + датасет + честный бенчмарк**, а не ещё одна обёртка над YOLO.

---

## 1. Распознавание срока на фото

### Рабочий пайплайн (консенсус papers 2022–2026)

1. Детектор области даты (ROI)  
2. Crop  
3. OCR  
4. Парсер форматов + cue-слова («годен до», EXP, BEST BEFORE)  
5. Разведение MFG vs EXP  
6. Confidence / abstain → человек подтверждает  

Full-image OCR + один regex — быстро для прототипа, но шумно и путает даты.

### Цифры из источников (не смешивать контексты)

- ExpDate (Seker & Ahn, 2022): **97.74%** на своём бенчмарке, 13 форматов  
- Tohoku G-RIPS 2025: EasyOCR ~**70.8%** → PaddleOCR **96.7%** на своих боксах  
- OCR+LLM (Springer): ~**81%** на ExpDate-подобных фото  
- Habr (Go+Tesseract, 300 фото): **~61%** корректных дат end-to-end  
- Dot-matrix/CIJ (ETASR 2026): CER **18.4%** → **2.3%** с морфологией  

В поле без HITL ожидать «магии >90%» нельзя. False expiry опаснее false reject — **confirm UI обязателен**.

### Что брать как dependency

| Компонент | Лицензия | Роль |
|-----------|----------|------|
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | Apache-2.0 | Лучший default OCR для упаковок |
| EasyOCR / Tesseract | Apache-2.0 | Fallback / baseline |
| [RF-DETR](https://github.com/roboflow/rfdetr) | Apache-2.0 | Детектор ROI **без AGPL** |
| dateparser / dateutil | BSD / Apache | Парсинг после нормализации |
| [ente/mobile_ocr](https://github.com/ente/mobile_ocr) | MIT | Паттерны Flutter on-device |

**Избегать как hard dependency:** Ultralytics YOLO (**AGPL-3.0**) в MIT/Apache-проекте; VLM (Gemini и т.п.) как единственное ядро.

### Domain-specific репо (слабые — идеи важнее кода)

| Проект | URL | Заметка |
|--------|-----|---------|
| ExpDate | https://felizang.github.io/expdate/ · https://github.com/felizang/expdate | Эталон архитектуры и 13 форматов; ★~3 |
| Date-Recognition | https://github.com/HieuNTg/Date-Recognition | Идеи пайплайна; **нет LICENSE — не копировать код** |
| expiration-date-detection | https://github.com/kivancgunduz/expiration-date-detection | MIT, ★~11, учебный, стек устарел |
| expire-date (Habr) | https://github.com/ak1m1tsu/expire-date · https://habr.com/ru/articles/749218/ | Regex + max-date heuristic |
| ShelfLife (Android) | https://github.com/officialfshot-web/ShelfLife | **Лучший reference** CameraX + ML Kit OCR + regex, MIT |
| ExpirationRadar | https://github.com/Ps23102004/expirationradar | Tiered pipeline + provenance UI |

### Писать с нуля (ценность OSS)

- API: `extract(image) → {iso_date, kind, confidence, candidates, bboxes}`  
- Словарь cue: годен до / срок годности / use by / best before / exp / mfg…  
- Grammar форматов + calendar validation  
- Политика disambiguation (документированная)  
- Abstain + HITL  
- Небольшой **RU/CIS датасет** (даже 200–500 фото) — главный community asset  

---

## 2. Штрихкоды и открытые базы

### Open Food Facts — единственный честный open-data путь

- Мир: **>4M** продуктов; **Russia ≈ 36 500** (замер API 2026-09-25) — для магазинной полки РФ **высокий % unknown**  
- Лицензия: **ODbL + DbCL**, фото **CC-BY-SA**  
- API v3: `GET …/api/v3/product/{barcode}`, User-Agent обязателен; ~15 req/min/IP  
- Bulk: **nightly dumps / JSONL / delta**, не scrape API  
- Поле `expiration_date` есть, но это crowdsourced строка без формата — **не замена OCR**  
- SDK: Dart, Python, JS, Kotlin…; приложение [smooth-app](https://github.com/openfoodfacts/smooth-app)  

Семейство: Open Beauty / Products / Pet Food Facts — тот же стек лицензий.

### Что нельзя класть в открытое зеркало OSS

UPCitemdb, Go-UPC, Barcode Lookup, EAN-Search — lookup возможен, но **запрет/нет лицензии на перераспределение**. GS1 и Честный ЗНАК — не open catalog (Честный ЗНАК максимум optional check маркировки).

### Сканеры для OSS

| Выбор | Лицензия | Комментарий |
|-------|----------|-------------|
| **zxing-cpp** / **flutter_zxing** | Apache-2.0 / MIT | Рекомендуемый FOSS-путь |
| ZBar | LGPL-2.1 | Осторожно с линковкой |
| mobile_scanner | BSD обёртка | На Android тянет **проприетарный ML Kit** |
| Scandit / Dynamsoft | Commercial | Не в core |

### Гибрид для OSS

```
Камера
 ├─ Barcode (zxing-cpp) → GTIN
 │     ├─ локальный кэш (SQLite из OFF dump/delta)
 │     └─ fallback OFF API → miss → «добавить» + WRITE в OFF
 └─ OCR срока → своя таблица inventory (это НЕ данные OFF)
```

В README обязательно: attribution ODbL, политика кеша, contrib-back, disclaimer as-is.

---

## 3. Готовые приложения и рыночный паттерн

Успешный MVP-паттерн (BEEP / Expiry, Pantrly, pantry_app): **barcode → имя/картинка; дату — руками; reminders**.

| Репо | Роль |
|------|------|
| [openfoodfacts/smooth-app](https://github.com/openfoodfacts/smooth-app) | Reference Flutter + barcode + OFF (**не** pantry/OCR) |
| [Thigas-Tech/pantry_app](https://github.com/Thigas-Tech/pantry_app) | Лучший Flutter reference: OFF + expiry UI + notifications, дата вручную, MIT |
| [begiedz/Pantrly](https://github.com/begiedz/Pantrly) | Минимальный RN + OFF |
| [officialfshot-web/ShelfLife](https://github.com/officialfshot-web/ShelfLife) | On-device OCR expiry (Kotlin), без barcode |
| [dadaloop82/EverShelf](https://github.com/dadaloop82/EverShelf) | PWA + AI OCR, ★~115 — inspiration UX, не fork |
| [grocy/grocy](https://github.com/grocy/grocy) | Self-hosted ERP, barcode + ручной срок, ★~9k |

**Не форкать** smooth-app / Grocy / EverShelf как основу. **Greenfield** + паттерны из pantry_app + ShelfLife OCR + OFF SDK.

С форумов: ML Kit ломается на dot-matrix; нужен crop зоны даты; парсер + ручное подтверждение; люди приходят чаще за списком покупок, чем за учётом холодильника (vc.ru «Чем богаты»).

---

## 4. Рекомендуемая структура своего репо

Лицензия: **Apache-2.0** (ближе к OFF) или **MIT** (проще для контрибьюторов).

```text
expiry-tracker/
  apps/mobile/                 # Flutter UI
  packages/
    barcode_scan/              # zxing wrapper
    off_client/                # OFF + cache policy
    packdate/                # ML Kit/Paddle + confidence
    expiry_parsers/            # pure Dart: regex, locale, templates (легко принимать PR)
    inventory_core/            # SQLite, reminders
  datasets/expiry_samples/     # кропы дат + expected.json
  docs/ARCHITECTURE.md
  .github/ISSUE_TEMPLATE/
  LICENSE · README · CONTRIBUTING
```

Community (как у OFF): good-first-issues на date regex и локали; PR с фикстурами фото; не принимать bulk AI-parsers без тестов.

---

## 5. Roadmap 2–6 недель (соло)

| Неделя | Результат |
|--------|-----------|
| 1 | Репо day 1: LICENSE, README, CI, список, ручной item, datepicker, SQLite |
| 2 | Barcode → OFF → prefill → ручной expiry → offline cache |
| 3 | Expired/Soon/OK + notifications → **релиз v0.1 без OCR** |
| 4 | `packdate` experimental: candidates + **обязательный confirm**, feature flag |
| 5 | Category templates, cue-слова RU/EN, provenance (OCR vs USER) |
| 6 | Dataset guidelines, good-first-issues, i18n → v0.2 |

Оценка часов: v0 barcode+manual **~40–60 ч**; OCR-assist **+40–80 ч**; «авто-OCR без правок» — **месяцы + датасет**.

### v0.1 библиотечного ядра OCR (если начинать с lib)

1. PaddleOCR full-frame + RU/EN parse + abstain + CLI + 30 golden images  
2. ROI-детектор (RF-DETR / ONNX)  
3. Dot-matrix preprocess + mobile thin client  

---

## 6. Практические рекомендации именно тебе

1. **Стартуй с v0 без OCR в критическом пути** — так делают и рынок, и живые OSS pantry-трекеры.  
2. **Данные только через OFF-семейство**, если хочешь честный open-source; коммерческие barcode API — максимум private fallback, не в публичное зеркало.  
3. **Ядро дифференциации:** `expiry_parsers` + RU датасет + честный бенчмарк + HITL, не «YOLO в README».  
4. **Лицензии:** Apache-2.0/MIT код; не тащить AGPL YOLO; не копировать репо без LICENSE.  
5. **В РФ** закладывай UX на unknown barcode («добавить продукт» + contrib в OFF).  
6. Модули barcode и expiry держи **раздельно**: разные accuracy claims, разные таблицы.

---

## Ключевые ссылки

**OCR / papers**  
- https://felizang.github.io/expdate/  
- https://doi.org/10.1016/j.eswa.2022.117310  
- https://habr.com/ru/articles/749218/  
- https://blog.roboflow.com/expiration-date-inspection/  

**OFF**  
- https://world.openfoodfacts.org/data  
- https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/  
- https://github.com/openfoodfacts/openfoodfacts-dart  
- https://github.com/openfoodfacts/smooth-app  

**Сканеры**  
- https://github.com/zxing-cpp/zxing-cpp  
- https://github.com/khoren93/flutter_zxing  

**Reference apps**  
- https://github.com/Thigas-Tech/pantry_app  
- https://github.com/officialfshot-web/ShelfLife  
- https://github.com/Ps23102004/expirationradar  

---

## Ограничения ресёрча

- Часть ★/license через поиск и страницы репо, не полный dump GitHub API.  
- Точная SPDX-лицензия датасета ExpDate на Google Drive требует проверки перед включением в репо.  
- Покрытие OFF по России — снимок API на дату ресёрча; цифры плывут.  
- Это технический фундамент, не юридическая консультация по ODbL/AGPL.
