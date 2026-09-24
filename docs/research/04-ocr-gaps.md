# Почему общий OCR ≠ expiry tracker (2026-09-25)

## Вердикт: частично — не решено как OSS-продукт

«Хороший общий OCR» ≠ готовый expiry tracker. Research на ExpDate ~97% на crop; industrial Cognex/Keyence — controlled line. Публичного open-weight стека с HF-карточкой + бенчмарком phone→inkjet/embossed почти нет.

HalalBench (food packaging OCR 2026): best F1 ≈ 0.19 на ingredient text — packaging ≠ solved.

## Gaps
- Нет публичного E2E phone→ISO date leaderboard
- Embossed / CIJ wild — мало open data
- HF: в основном YOLO+Tesseract demo; pike00 — другой домен (photo date stamps)
- Ближе всего E2E: HieuNTg/Date-Recognition, ExpRec (MDPI 2025) — research, не production card

## Eval protocol (1 вечер)
N≈40–60 stratified photos; Exact ISO ≥90%, False-ISO ≤5%, embossed ≥70% иначе gap.

Ключевые ссылки: felizang.github.io/expdate, doi:10.3390/a18050286 ExpRec, HalalBench arxiv 2604.22754, HF krishuggingface/Expiry_Date_Detection, HieuNTg/Date-Recognition
