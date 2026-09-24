# Dependency shortlist (permissive OSS)

## OCR / CV (prefer)

| Component | License | Role |
|-----------|---------|------|
| PaddleOCR / PP-OCRv5–v6 | Apache-2.0 | Default OCR; v6 industrial/dot-matrix but **not Cyrillic** — pair with v5 Cyrillic rec |
| `cyrillic_PP-OCRv5_mobile_rec` | Apache-2.0 | RU packaging text |
| RapidOCR | Apache-2.0 | ONNX-friendly wrapper |
| RF-DETR | Apache-2.0 | ROI detector without AGPL |
| EasyOCR / Tesseract | Apache-2.0 | Baselines |
| Florence-2-base | MIT | Optional crop recognizer |
| TrOCR printed | Code MIT; **weights SPDX UNVERIFIED** on HF | Bench-only crop recognizer |
| PaddleOCR-VL-1.6 0.9B | Apache-2.0 | Optional small doc/OCR VLM (prefer over older VL if deps allow) |
| Qwen2-VL-2B / Qwen3-VL-2B | Apache-2.0 | Optional VLM control path |
| PaddleOCR-VL 0.9B | Apache-2.0 | Optional small doc/OCR VLM |
| dateparser / python-dateutil | BSD / Apache | Parsing helpers |
| OpenCV | Apache-2.0 | Preprocess |

## Avoid as hard deps

| Component | Why |
|-----------|-----|
| Ultralytics YOLO | AGPL-3.0 |
| Surya (some weight licenses) | OpenRAIL restrictions |
| Qwen2.5-VL-**3B** (and OCRFlux) | `qwen-research` NC; **7B is Apache-2.0** — see Corrections |
| Nougat | CC-BY-NC |
| Chandra weights | Modified OpenRAIL-M |
| Hobby HF “Expiry_*” with empty cards | Not production-ready |

## Barcode

- zxing-cpp / flutter_zxing — default FOSS path  
- ML Kit — optional proprietary accelerator behind a flag  

## Data

- Open Food Facts family only for redistributable product identity  
- Do not merge proprietary barcode API responses into a public OFF-derived DB

## Corrections (verified 2026-09-25)

Full audit: [09-ocr-models-license-audit.md](09-ocr-models-license-audit.md).

| Old claim (this file / 03) | New | Source |
|----------------------------|-----|--------|
| “Qwen2.5-VL \| Research / non-commercial style terms on some sizes” as a single Avoid row | Keep Avoid for **3B** (`qwen-research` NC) and treat **72B** as Conditional (Qwen LICENSE). **7B-Instruct is Apache-2.0** and is allowed as optional VLM. | [3B LICENSE](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/blob/main/LICENSE); [7B card](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct) `license: apache-2.0`; [72B LICENSE](https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct/blob/main/LICENSE) |
| Prefer table lists “Qwen2-VL-2B / Qwen3-VL-2B \| Apache-2.0” without caveat | **Confirmed** Apache-2.0 for Qwen2-VL-2B and Qwen3-VL-2B/8B. Prefer Qwen3-VL-2B or Qwen2.5-VL-**7B** for VLM control; do **not** pull Qwen2.5-VL-3B. | [Qwen2-VL-2B](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct); [Qwen3-VL-2B](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct) |
| “Florence-2-base / TrOCR printed \| MIT” | Florence-2-base **MIT** confirmed. TrOCR: **code** MIT (unilm); **weights** SPDX **UNVERIFIED** on HF card. | [Florence-2-base](https://huggingface.co/microsoft/Florence-2-base); [trocr-base-printed](https://huggingface.co/microsoft/trocr-base-printed); [unilm LICENSE](https://github.com/microsoft/unilm/blob/master/LICENSE) |
| Implied PP-OCRv5–v6 interchangeable for RU | PP-OCRv6 unified multilingual model is **Latin+CJK**, not Cyrillic. Default RU path remains **`cyrillic_PP-OCRv5_mobile_rec`**. | [PP-OCRv6 docs](https://www.paddleocr.ai/latest/en/version3.x/algorithm/PP-OCRv6/PP-OCRv6.html) |
| “Surya (some weight licenses) \| OpenRAIL” | Confirmed: code Apache-2.0; weights modified OpenRAIL-M ($5M + no competing product). | [MODEL_LICENSE](https://github.com/datalab-to/surya/blob/master/MODEL_LICENSE) |

Prefer-table refinements (non-breaking):

- Add **PaddleOCR-VL-1.6** (Apache-2.0) alongside 0.9B / VL-1.5 family.
- RapidOCR remains preferred ONNX-friendly path.
