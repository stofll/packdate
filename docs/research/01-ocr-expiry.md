# Отчёт: распознавание сроков годности на фото упаковок (фундамент для OSS)

**Дата ресёрча:** 2026-09-25 (Europe/Moscow)  
**Цель:** свой open-source проект (библиотека + демо), а не коммерческий продукт.

---

## 1. Executive summary

Задача **не решается одним OCR «из коробки»**. Рабочий консенсус индустрии и papers 2022–2026:

**detect ROI даты → crop → OCR/recognize → parse + disambiguate (EXP vs MFG) → confidence / HITL**

Ниши «готовой зрелой библиотеки expiry-OCR» **нет**: GitHub-поиск даёт десятки репо с **0–11★**, часто без лицензии или устаревшие. **Переиспользовать как зависимости** стоит зрелые OCR/детектор (Apache), а **продуктовый слой (парсер дат, RU-подсказки, disambiguation, API библиотеки)** — писать самим. Это и есть ниша OSS.

Ключевые цифры из источников (контекст разный — не смешивать):
- ExpDate (Seker & Ahn, 2022): **97.74%** recognition на своём бенчмарке, **13 форматов**, 1767 real + synth.
- Tohoku G-RIPS 2025: EasyOCR ~**70.8%** → PaddleOCR **96.7%** (Y-M-D) на своих боксах.
- OCR+LLM filter (Springer, датасет ExpDate 665 img): PaddleOCR+Llama → **~81%** (реалистичнее «полевых» фото).
- Habr/Go+Tesseract (300 img): **183/300** корректных дат (~61% end-to-end).
- Dot-matrix / CIJ (ETASR 2026): без препроцесса CER **18.4%** → с morph **2.3%**.

**Для OSS-репо:** лицензия **Apache-2.0 или MIT**; **избегать Ultralytics YOLO (AGPL-3.0)** как обязательной зависимости, если хотите permissive license — брать **RF-DETR (Apache-2.0)** или ONNX-экспорт чужих весов с явной лицензией.

Штрихкоды — **отдельный поток** (ZXing / ML Kit Barcode / zxing-cpp); не смешивать с expiry-пайплайном.

---

## 2. Подходы (архитектура пайплайна)

### 2.1 Классика: full-image OCR + regex
Tesseract / EasyOCR / PaddleOCR / ML Kit / Apple Vision → regex/`dateparser` → «взять максимальную дату».

- Плюс: быстро для MVP прототипа.
- Минус: шум (состав, бренд, штрихкод-цифры), путаница MFG/EXP, мелкий штамп.
- Источник: [Habr](https://habr.com/ru/articles/749218/), репо [ak1m1tsu/expire-date](https://github.com/ak1m1tsu/expire-date) (★3).

### 2.2 Two-stage (рекомендуемый де-факто)
1. **Детектор ROI** классов `date` / `due` / `prod` / `code` (схема ExpDate).
2. **OCR только crop**.
3. **Парсер**: форматы + префиксы EXP/BB/USE BY/годен до + выбор expiry.

Источники: [ExpDate](https://felizang.github.io/expdate/), [HieuNTg/Date-Recognition](https://github.com/HieuNTg/Date-Recognition), Tohoku PDF, Roboflow blogs.

### 2.3 Специализированные модели
- ExpDate: Date detect → **DMY detect** → char recognize (FCN), 13 форматов.
- Custom CTC/CRNN на crop (Date-Recognition: CER 0.05 на их synth — осторожно с generalization).
- VLM (Gemini и т.п.): удобно для прототипа, **плохо для OSS-ядра** (закрытый API, стоимость, невоспроизводимость).

### 2.4 Препроцесс (критичен для штампов)
CLAHE, adaptive threshold, dilation 3×3 для CIJ/dot-matrix, selective SR при low confidence, deboss/lighting для embossed.

---

## 3. Сложности (чеклист для дизайна OSS)

| Сложность | Почему ломает | Что делать в пайплайне |
|-----------|---------------|------------------------|
| Форматы ДД.ММ.ГГГГ / MM/DD / JUL25 / YYMMDD | Ambiguous parse | Явный locale (RU → DMY), whitelist форматов, reject ambiguous |
| Stamped / embossed / CIJ | Tesseract ~55–60% char на dot-matrix (ameera3) | ROI + morph/SR + date-constrained OCR |
| Блики, кривая банка | OCR на full frame падает | Guidance UI + многокадр + glare-aware preprocess |
| Кириллица vs латиница | «годен до», «срок годности», BEST BEFORE | Multilingual OCR + словарь cue-слов |
| Без разделителей `251225` | Regex ломается | Кандидаты + calendar validation |
| MFG vs EXP | Две даты на этикетке | Классы `prod`/`due` + «latest if EXP cue» |
| Мелкий шрифт | | Crop + upsample / SR |

Русский рынок: мало публичных RU-датасетов; ExpDate/бразильский — другой locale. **Свой RU/CIS датасет — главный вклад OSS.**

---

## 4. OSS-проекты и библиотеки

### 4.1 Domain-specific (expiry) — слабая база, идеи важнее кода

| Название | URL | ★ (на 2026-09-25) | Лицензия | Свежесть | Применимость для своего OSS |
|----------|-----|-------------------|----------|----------|------------------------------|
| **ExpDate** (paper + dataset + exe) | [felizang/expdate](https://github.com/felizang/expdate), [project](https://felizang.github.io/expdate/), [ScienceDirect OA](https://www.sciencedirect.com/science/article/pii/S0957417422006728) | ★3 | Paper CC open access; **лицензия датасета на GDrive — проверить перед редистрибуцией** | 2022 + страница жива | **Эталон архитектуры и 13 форматов**; не форкать как основу lib |
| **Date-Recognition (DateReg)** | [HieuNTg/Date-Recognition](https://github.com/HieuNTg/Date-Recognition) | ★1 | **LICENSE отсутствует (404)** — **нельзя форкать/копировать код без явного разрешения** | pushed 2026-06 | **Идеи**: pipeline class, prefix strip, O→0, latest=expiry; веса на ExpDate-подобных synth |
| **expiration-date-detection** | [kivancgunduz/…](https://github.com/kivancgunduz/expiration-date-detection) | ★11 | **MIT** | 2022, учебный BeCode | Можно смотреть API/FastAPI; стек FCOS+Tesseract устарел |
| **expire-data-model** | [abdullah-bl/…](https://github.com/abdullah-bl/expire-data-model) | ★0 | не указана в выдаче | YOLOv11 + OCR scripts | Паттерн конвертации аннотаций; не foundation |
| **OCR_Expiration_Date** | [ameera3/…](https://github.com/ameera3/OCR_Expiration_Date) | н/д (мед.) | н/д | academic | Dot-matrix ensemble insights |
| **ak1m1tsu/expire-date** | [GitHub](https://github.com/ak1m1tsu/expire-date) | ★3 | н/д | код к Habr | Regex + max-date heuristic (Go) |
| Brazilian YOLO detect-only | paper [ERAMIA-RS 2025](https://sol.sbc.org.br/index.php/eramiars/article/view/39448); Roboflow universe (в paper: products-expiration-dates) | — | Roboflow terms | 668 img, F1 **0.812** detect | Fine-tune детектора; **не OCR** |
| HF YOLO+OCR | [krishuggingface/Expiry_Date_Detection](https://huggingface.co/krishuggingface/Expiry_Date_Detection) | — | проверить карточку | — | Только как reference, не как core |

**Вывод:** форкать «готовый expiry-проект» почти не из чего. **Писать свой репо**, заимствуя **паттерны** и **датасеты** (с attribution).

### 4.2 Инфраструктура (брать как dependency, не вендорить)

| Компонент | URL | ★ / лицензия | Роль |
|-----------|-----|---------------|------|
| **PaddleOCR** | [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | ~88k★, **Apache-2.0** | Лучший default OCR для упаковок (много сравнений) |
| **EasyOCR** | [JaidedAI/EasyOCR] | ~30k★, **Apache-2.0** | Fallback / A/B |
| **Tesseract** | [tesseract-ocr/tesseract] | ~76k★, **Apache-2.0** | Baseline; слабее на штампах |
| **RF-DETR** | [roboflow/rf-detr](https://github.com/roboflow/rfdetr) | **Apache-2.0** (Nano–L) | Детектор ROI **без AGPL** |
| **Ultralytics YOLO** | ultralytics | **AGPL-3.0** | Только если весь проект AGPL или Enterprise |
| **dateparser** | [scrapinghub/dateparser](https://github.com/scrapinghub/dateparser) | BSD-3 | Парсинг после нормализации |
| **python-dateutil** | — | Apache-2.0 / BSD | Strict formats |
| **ente/mobile_ocr** | [ente/mobile_ocr](https://github.com/ente/mobile_ocr) | ★28, **MIT** | Flutter on-device: Android PP-OCRv5 ONNX + iOS Vision |
| OpenCV | — | Apache-2.0 | Preprocess |

**Лицензионная совместимость (важно для OSS):**
- Свой репо **MIT или Apache-2.0** + deps Apache/MIT/BSD → OK.
- **AGPL YOLO** в runtime → юридически тянет AGPL на дистрибутив приложения (или коммерческая лицензия Ultralytics). Для permissive OSS: **не делать hard dependency**.
- PaddleOCR: остерегаться **опциональных AGPL-deps** (исторически PyMuPDF) — не включать в default extras.
- Датасеты ≠ код: ExpDate/Roboflow — читать terms до включения в репо.

---

## 5. Статьи, блоги, обсуждения — ключевые выводы

| Источник | Вывод |
|----------|--------|
| [Seker & Ahn ESWA 2022 / ExpDate](https://doi.org/10.1016/j.eswa.2022.117310) | Эталон: detect → DMY → recognize; 97.74% на своём сете; открытый датасет |
| [Tohoku G-RIPS 2025 PDF](https://www.mccs.tohoku.ac.jp/g-rips/report/2025/pdf/IHI_final_pres_v2.pdf) | YOLO ROI + **PaddleOCR >> EasyOCR**; regex post-process |
| [ETASR 2026 CIJ/YOLOv8+PaddleOCR](https://etasr.com/index.php/ETASR/article/view/20202) | Dot-matrix: morph критичен; 229 ms на Pi4 |
| [IOP 2026 degradation-aware SR](https://iopscience.iop.org/article/10.1088/2631-8695/ae9a2b) | YOLOv11 ROI + selective SR + EasyOCR |
| [Medicine YOLOv8 seg](https://doi.org/10.37391/ijeer.130432) | Preprocess (wavelet/BM3D/CLAHE) + OCR; CER 0.9% в идеале |
| [OCR+LLM Springer](https://www.springerprofessional.de/ocr-and-llm-pipeline-for-reliable-expiration-date-reading-in-acc/52451958) | LLM как **фильтр**, не генератор; ~81% с PaddleOCR |
| [Habr Go+Tesseract](https://habr.com/ru/articles/749218/) | Regex DMY; max of two dates; Tesseract слабо; автор сам рекомендует Python/EasyOCR |
| [Roboflow + Gemini](https://blog.roboflow.com/expiration-date-inspection/) (Jan 2026) | VLM удобен, но не OSS-ядро |
| Reddit r/computervision | Двухстадийность, свет, emboss — главные боли |

---

## 6. Готовые API/SDK (из коробки для упаковки)

| API/SDK | Что умеет для expiry на упаковке | Для OSS |
|---------|----------------------------------|---------|
| **Google Cloud Vision** | TEXT_DETECTION / DOCUMENT_TEXT — **сырой текст + bbox**, **нет** семантики «expiry» | Опциональный cloud backend; парсер свой |
| **AWS Textract** | AnalyzeExpense: даты **счетов**, не food packaging | Не целевой |
| **Azure Document Intelligence** | Invoice/due date — документы, не FMCG stamp | Не целевой |
| **ML Kit Text Recognition** | On-device OCR; парсинг дат — свой | Хорош для Android demo-app рядом с lib |
| **Apple Vision** | VNRecognizeTextRequest on-device | iOS demo |
| **ML Kit / ZXing** | Штрихкоды | **Отдельный модуль**, не expiry |

**Вывод:** облака = OCR-backend, не «expiry API». Ценность OSS — **семантический слой поверх OCR**.

---

## 7. Что взять в свой репо vs писать с нуля

### Брать / переиспользовать (dependency или inspiration)

| Что | Как |
|-----|-----|
| PaddleOCR PP-OCRv5 (server/mobile) | Default recognizer, Apache |
| RF-DETR или свой fine-tune → ONNX | Детектор ROI без AGPL |
| Схема классов ExpDate: `date`, `due`, `prod`, `code` | Совместимость с публичными датасетами |
| Идеи DateReg: strip EXP/BB/MFG/NSX/HSD; O→0; latest under EXP cue | Переписать, **не копировать** (нет LICENSE) |
| dateparser / dateutil + свой strict layer | Парсинг |
| ExpDate + Brazilian Roboflow как **eval/train seeds** | Attribution + license check |
| ente/mobile_ocr паттерны | Если Flutter demo |
| OpenCV preprocess recipes из papers | Свой `preprocess.py` |

### Писать с нуля (ядро ценности OSS)

1. **`packdate` library API**: `extract(image) → {iso_date, kind: use_by|best_before|mfg|unknown, confidence, candidates[], bboxes}`  
2. **RU+EN+возможно TT cue lexicon**: годен до, срок годности, употребить до, best before, use by, exp, bb, mfg…  
3. **Format grammar + calendar validation** (отсечь 32.13.2025)  
4. **Disambiguation policy** (документированная)  
5. **Confidence / abstain** → HITL  
6. **CLI + pytest на синтетике и golden fixtures**  
7. **Свой небольшой RU датасет** (даже 200–500 фото) — главный community asset  
8. Demo app (Streamlit/FastAPI) **отдельным пакетом** `packdate-demo`, чтобы lib оставалась тонкой  

### Не брать в core

- Ultralytics как обязательный import (если MIT/Apache)  
- Gemini/GPT как единственный путь  
- Код без LICENSE  
- Смешение barcode+expiry в одном классе без границ модулей  

### Рекомендуемая структура монорепо

```
packdate/                 # Apache-2.0 library
  src/packdate/
    detect/   # RF-DETR/ONNX wrapper
    recognize/# PaddleOCR/EasyOCR backends
    parse/    # formats, cues, disambiguation
    pipeline.py
  tests/fixtures/
apps/demo-web/              # optional
apps/demo-mobile/           # optional, ML Kit/Vision
datasets/                   # scripts + LICENSE notes, не обязательно веса в git
docs/architecture.md
```

---

## 8. Оценка сложности MVP (1–2 недели соло) и стек

### Реально за 1–2 недели
- Lib scaffold + PaddleOCR full-frame + RU/EN regex/dateparser + CLI  
- Streamlit demo + ручная правка  
- 50–100 своих фото как smoke test  
- README with limitations  

### Сложно / phase 2
- Robust stamped/CIJ/embossed  
- Fine-tuned detector на RU упаковке  
- On-device parity iOS/Android  
- >90% field accuracy без HITL  
- Полный набор форматов ExpDate + JUL25 без разделителей  

### Рекомендуемый стек

| Цель | Стек |
|------|------|
| **OSS lib + веб-прототип** | Python 3.11+, PaddleOCR, OpenCV, RF-DETR или временно YOLO *только* если license=AGPL, FastAPI/Streamlit, pytest |
| **Мобильное демо** | Flutter + ente/mobile_ocr **или** Kotlin+ML Kit / Swift+Vision; тяжёлый пайплайн — на сервер с той же lib |
| **Лицензия репо** | **Apache-2.0** (патентный grant + совместимость с Paddle/RF-DETR) |

Штрихкод: отдельный модуль `packdate.barcode` (zxing-cpp / ML Kit), результат рядом, не вместо даты.

---

## 9. Метрики качества

Считать раздельно:
- **Detect mAP / F1** (ROI)
- **CER/WER** на crop
- **End-to-end date accuracy** (ISO совпало)
- **Abstain rate** (низкая confidence → UI)

Типичные порядки (из источников, не универсальны):
- Controlled / paper: 95–98%  
- Field + Tesseract/naive: ~60–70%  
- Strong OCR + ROI + parse: ~80–97% в зависимости от домена  
- Dot-matrix без препроцесса: CER двузначный  

**HITL обязателен** для consumer MVP: показать crop + кандидата + «исправить». False expiry опаснее false reject.

---

## 10. Риски и антипаттерны

1. Full-image OCR без ROI  
2. Один regex под все страны  
3. Всегда брать max date без cue (ошибка на гарантии/промо-датах)  
4. Заявить 97% по ExpDate как product SLA  
5. AGPL YOLO в MIT-проекте без аудита  
6. Форк репо без LICENSE  
7. VLM-only core (не OSS-friendly)  
8. Игнор MFG vs EXP  
9. Смешать barcode flow в тот же accuracy claim  
10. Обучать только на synth → провал на реальных штампах  

---

## 11. Конкретные рекомендации для своего OSS

1. **Название ниши:** «permissive, reproducible expiry-date pipeline for packaging» — мало конкурентов с нормальной лицензией и тестами.  
2. **License: Apache-2.0.**  
3. **v0.1 (неделя):** parse-first + PaddleOCR; abstain; CLI; 30 golden images.  
4. **v0.2:** детектор ROI (RF-DETR fine-tune на ExpDate schema + свои RU).  
5. **v0.3:** dot-matrix preprocess; multilingual cues; mobile thin client.  
6. **Публиковать как библиотеку** `packdate`; приложение — example.  
7. **Не форкать** HieuNTg/Date-Recognition (нет LICENSE); **можно** цитировать архитектуру и ExpDate paper.  
8. **Можно** изучать MIT-код kivancgunduz; не опираться на него как на SOTA.  
9. Главный moat: **RU/CIS датасет + честный бенчмарк + HITL UX**, не «ещё одна YOLO обёртка».

---

### Ограничения этого ресёрча

- GitHub API rate limit: часть ★/license через WebFetch/search, не полный API dump.  
- `acseker.github.io/ExpDateWebsite` → **404** на момент запроса; актуальная витрина: [felizang.github.io/expdate](https://felizang.github.io/expdate/).  
- Точная SPDX-лицензия датасета ExpDate на Google Drive **не подтверждена** в открытом README — перед включением в репо проверить файл лицензии.  
- Roboflow Universe pages частично за Cloudflare — URL датасета брать из paper PDF.
