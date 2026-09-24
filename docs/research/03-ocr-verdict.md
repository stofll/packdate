# Повторный ресёрч OCR: вердикт (2026-09-25)

## Одна фраза

**Общий OCR в 2025–2026 действительно силён и хайп на X/HF о нём справедлив. Задача «срок годности с фото упаковки» как готовый drop-in на Hugging Face — не решена.** Нужен пайплайн ROI → OCR → семантический парсер (+ HITL); это и есть ниша OSS.

---

## Две разные задачи

| | (A) General / document OCR | (B) Expiry on packaging |
|--|--|--|
| Статус | Сильно продвинут | Не productized как OSS |
| Хайп на X | GOT, olmOCR, DeepSeek-OCR, Qwen-VL, PaddleOCR-VL | Почти всегда про (A) |
| Типичные цифры | 80–96% на doc-бенчах | Lab ~97%; поле ~60–81% E2E |
| На HF | Много зрелых моделей | 1–3 любительских YOLO+Tesseract, downloads≈0 |

HalalBench 2026 (ingredient text на упаковке): best F1 ≈ **0.19** у общих движков — packaging ≠ solved.

---

## Что есть на Hugging Face именно под expiry

- `krishuggingface/Expiry_Date_Detection` — YOLO + Tesseract, Apache, downloads=0
- `harshauckoo/expiry_date_extraction`, `Moankhaled10/expiry-detection` — пустые/сырые карточки
- Spaces: один популярный тащит **Gemini SaaS**, не локальную OSS-модель
- `pike00/yolo-date-stamp-detector` — **другой домен** (date stamp на сканах фото)

**Нет** канонической open-weight модели: fine-tune на expiry crops + нормальная карточка + лицензия + полевой бенчмарк.

Ближе всего вне HF: ExpDate (датасет+paper), ExpRec (MDPI 2025, почти пустой GitHub), HieuNTg/Date-Recognition (нет LICENSE).

---

## Shortlist для бенчмарка на 50–100 RU фото

### Обязательно
1. **PP-OCRv5/v6** + `cyrillic_PP-OCRv5_mobile_rec` (Apache-2.0) — industrial/dot-matrix в v6, edge-friendly  
2. Сравнение: full frame vs crop ROI vs + preprocess для CIJ

### VLM-контроль (один)
3. **PaddleOCR-VL-1.5/1.6 (0.9B)** Apache **или** **Qwen2-VL-2B / Qwen3-VL-2B** Apache  

### Опционально
4. RapidOCR (ONNX-обёртка PP-OCR)  
5. Florence-2-base / TrOCR на crop  

### Не тащить в permissive OSS-core
Surya (OpenRAIL), Qwen2.5-VL (Research/NC), Nougat (NC), Chandra (OpenRAIL-ish), OCRFlux (qwen-research), старый MinerU AGPL

### Протокол «решает / нет» за вечер
Страты: inkjet, thermal, embossed, кривая банка, MFG+EXP, negatives.  
Порог: Exact ISO ≥ **90%** на non-null **и** False-ISO ≤ **5%** **и** embossed ≥ **70%**. Иначе gap остаётся.

---

## Датасеты

| Ресурс | Заметка |
|--------|---------|
| ExpDate (felizang + Drive; HF `dimun/ExpirationDate`) | Главный публичный expiry-сет; лицензию Drive проверить |
| `aihpi/bottle-cap-date-stamps` | CC BY 4.0, hard reflective stamps |
| TextOCR / ICDAR | Scene text pretrain, не expiry |
| RU packaging expiry | **Нет** крупного публичного — ваш вклад |

---

## Рекомендация для OSS

```
date ROI detector → PP-OCRv6 (+cyrillic)
  → parse (RU/EN cues, MFG vs EXP)
  → abstain + confirm UI
  → optional small VLM only on ambiguous
```

Ценность репо: не «ещё одна OCR-обёртка», а **parse + RU датасет + честный stratified бенчмарк**.

Оценка часов на проверку гипотезы «модель X уже решает»: **2–3 часа** на 40–60 своих фото по протоколу выше.
