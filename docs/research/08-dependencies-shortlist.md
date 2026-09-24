# Dependency shortlist (permissive OSS)

## OCR / CV (prefer)

| Component | License | Role |
|-----------|---------|------|
| PaddleOCR / PP-OCRv5–v6 | Apache-2.0 | Default OCR; v6 notes industrial/dot-matrix |
| `cyrillic_PP-OCRv5_mobile_rec` | Apache-2.0 | RU packaging text |
| RapidOCR | Apache-2.0 | ONNX-friendly wrapper |
| RF-DETR | Apache-2.0 | ROI detector without AGPL |
| EasyOCR / Tesseract | Apache-2.0 | Baselines |
| Florence-2-base / TrOCR printed | MIT | Optional crop recognizers |
| Qwen2-VL-2B / Qwen3-VL-2B | Apache-2.0 | Optional VLM control path |
| PaddleOCR-VL 0.9B | Apache-2.0 | Optional small doc/OCR VLM |
| dateparser / python-dateutil | BSD / Apache | Parsing helpers |
| OpenCV | Apache-2.0 | Preprocess |

## Avoid as hard deps

| Component | Why |
|-----------|-----|
| Ultralytics YOLO | AGPL-3.0 |
| Surya (some weight licenses) | OpenRAIL restrictions |
| Qwen2.5-VL | Research / non-commercial style terms on some sizes |
| Nougat | CC-BY-NC |
| Chandra weights | Modified OpenRAIL-M |
| Hobby HF “Expiry_*” with empty cards | Not production-ready |

## Barcode

- zxing-cpp / flutter_zxing — default FOSS path  
- ML Kit — optional proprietary accelerator behind a flag  

## Data

- Open Food Facts family only for redistributable product identity  
- Do not merge proprietary barcode API responses into a public OFF-derived DB  
