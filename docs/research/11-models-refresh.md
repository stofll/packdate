# Model refresh: gaps not covered by 01–09 (research notes, 2026-09-25)

**Access date:** 2026-09-25. Complements [09-ocr-models-license-audit.md](09-ocr-models-license-audit.md); does not repeat it. Pages blocked by Cloudflare / bot checks are marked **UNVERIFIED**.

## 1. On-device OCR with Cyrillic

- **Google ML Kit Text Recognition v2 does not support Cyrillic.** The official languages page lists Latin, plus Chinese, Devanagari, Japanese, Korean in v2; no `ru`/`uk`/`be`/`kk`. The only Cyrillic row is Ossetian (`os`) in a "Mapped" table, which looks like a docs artifact. Open feature request: googlesamples/mlkit #801. **ML Kit stays barcode-only for RU**; the ML Kit OCR suggestion in 01/02 does not apply to RU packs.
- **Apple Vision** (`VNRecognizeTextRequest` / `RecognizeTextRequest`): Apple publishes no static list; `supportedRecognitionLanguages()` returns it at runtime per revision. A third-party README (bytefer/macos-vision-ocr) lists `ru-RU`, `uk-UA` on macOS 14.4. **UNVERIFIED** — check by calling the API on a device.
- **PaddleOCR mobile.** PaddleOCR 3.x docs have official Android (ONNX Runtime 1.21.1, minSdk 26, AAR SDK) and iOS (ONNX Runtime with CPU / XNNPACK / Core ML, iOS 16+) demos with PP-OCRv6_small/tiny and PP-OCRv5_mobile only. The SDK loads `rec/inference.onnx` + `inference.yml`, so swapping in a Cyrillic rec model looks possible but is not documented (**UNVERIFIED**).
- **Sizes (HF API):** `cyrillic_PP-OCRv5_mobile_rec` `inference.pdiparams` = 7,972,691 bytes (~8.0 MB), apache-2.0, Paddle format only (no ONNX on HF). `PP-OCRv5_mobile_det` ≈ 4.7 MB. Det + rec ≈ 12–13 MB before conversion.
- **RapidOCR** (official model list): Russian = `LangRec cyrillic`, PP-OCRv5 mobile, rapidocr ≥ 3.5.0. Engines: onnxruntime, openvino, paddle, MNN (≥ 3.6.0), TensorRT (≥ 3.7.0). The same list shows PP-OCRv6 languages as CJK + Latin — **no Cyrillic in v6**, consistent with the README errata.
- **Tesseract fallback:** `tessdata_fast/rus.traineddata` = 3,861,738 bytes (GitHub API). Traineddata license: **UNVERIFIED** (already open in 09 §9).

## 2. Expiry datasets and models (2025–2026)

- **ExpDate license: CC BY 4.0.** The official dataset page (`felizang.github.io/expdate/index_expdate.html`) allows research and commercial use with attribution. Sizes from the same page: Products-Real 1,767 images (1,102 train / 665 test), Products-Synth ~12,000, Date-Synth 128,000, Components-Synth 450,000; 13 date formats. Products-Real includes pharma packs. The CC BY-SA 4.0 footer on the project homepage belongs to the site template (Nerfies), not the dataset.
  - The HF mirror `dimun/ExpirationDate` is tagged `afl-3.0`, which differs from the source. Attribute via the official page, not the mirror.
- **arXiv:** searches for expiration / expiry date, best-before, dot-matrix OCR, inkjet, date code (2025–2026) found nothing on packaging expiry.
- **HF datasets:** nothing significant. `anuragzepto/expiry-ocr` (2025-11) has no card or license. `aihpi/bottle-cap-date-stamps` still CC BY 4.0 (updated 2026-07-03).
- **HF models:** `flowxai/expiryner` (Apache-2.0, 2026-09) is text NER for pharma documents, not vision; trained on synthetic data, F1 = 1.0 (authors call it a pipeline check). `SkalskiP/Qwen2.5-VL-3B-Instruct-date-stamp` is a LoRA on the NC-licensed 3B base — **avoid**.
- **Pharma:** Springer NCA article (2026-06-13, doi 10.1007/s00521-026-12229-2) compares Tesseract, EasyOCR, TrOCR, CRNN on pharma packaging; paywalled; data availability cites ExpDate only. Kaggle `nitesh31mishra/medicine-tablet-pack-image-dataset` (~437 images scraped from Google Images) — license **UNVERIFIED**, scraped origin is a red flag.
- **Roboflow Universe** (pages behind Cloudflare; search snippets show CC BY 4.0): `ml-model-tlmqd/expiry-date-recognition`, `college-37gbk/expiry-date-detection-wowdr`, `choi-t72ze/expiration-date-w0s6o`, `nguyen-luat-gia-khoi/expired-date-dataset`, `prtica-em-pesquisa/product-expiration`, `expiry-ocr/expiry-ocr`. All licenses **UNVERIFIED** until the pages are opened manually.

## 3. Small VLMs with permissive licenses (2026)

Checked via HF API and model cards. Parameter counts from `safetensors.total`.

| Model | License (verified) | Params | Note |
|---|---|---|---|
| Qwen3.5-0.8B / 2B / 4B | apache-2.0 + LICENSE | 0.87B / 2.27B | Released 2026-02, text + image. Cyrillic OCR quality **UNVERIFIED** |
| GLM-OCR (zai-org) | MIT (+ PP-DocLayoutV3 Apache-2.0) | 1.33B | `ru` in `language:`; information extraction by strict JSON schema. **Best "second opinion" candidate** |
| MiniCPM-V-4.6 | apache-2.0 ("weights and code") | 1.30B | 2026-04, on-device positioning |
| Gemma 4 (E2B / E4B / …) | **Apache-2.0** (`license_link` → `ai.google.dev/gemma/apache_2`) | E2B: 5.1B total | Gemma 1–3 / 3n use `license: gemma`; **Gemma 4 moved to Apache**. Separate Prohibited Use Policy: **UNVERIFIED** |
| LightOnOCR-2-1B | apache-2.0 | 1.0B | 11 languages, no `ru` |
| FireRed-OCR | apache-2.0 | 2.1B | Fine-tune of Qwen3-VL-2B |
| granite-docling-258M, SmolVLM2 | apache-2.0 | 0.26B / 0.5–2.2B | Document models, no Cyrillic on cards |
| moondream-2b-2025-04-14 | apache-2.0 | 1.9B | Moondream 3 / 3.1 — **avoid**, own Moondream Model License 1.0 (text not loaded) |
| LFM2 / 2.5-VL (Liquid) | `lfm1.0` | — | **Avoid** |
| HunyuanOCR | `other` | — | **Avoid** |

## 4. OCR vs VLM benchmarks on expiry / dot-matrix / CIJ

No dedicated benchmark found. Closest:

- SCPE 2024 (doi 10.12694/scpe.v25i6.4967, CC BY 4.0): fine-tuned EasyOCR + text LLaMA 2 for filtering (text LLM, not VLM); no comparable numbers in the abstract.
- arXiv 2502.06445: VLMs vs RapidOCR / EasyOCR on video frames, general domain; numbers not quoted here.

The packdate stratified bench (inkjet, thermal, embossed) would be a new public contribution.

## 5. Cloud VLM as an offline labeling oracle (not runtime)

- **Anthropic Commercial Terms, D.4** (effective 2025-06-17): may not "build a competing product… including to train competing AI models". Anthropic does not train on customer data.
- **Gemini API Terms** (updated 2026-04-28): may not "develop models that compete with the Services". On the free tier, uploaded content is used to improve Google products and may be read by human reviewers — use the paid tier or anonymized data for package photos.
- **OpenAI:** similar "develop models that compete" clause per search snippet; page behind Cloudflare, **UNVERIFIED**.

Takeaway: labeling golden evaluation fixtures with human review is very likely fine. Training our own detector / OCR on those labels is a gray zone and needs legal review. Record label provenance on fixtures.

## Sources

| Topic | URL |
|---|---|
| ML Kit v2 languages | https://developers.google.com/ml-kit/vision/text-recognition/v2/languages |
| ML Kit Cyrillic request | https://github.com/googlesamples/mlkit/issues/801 |
| Apple Vision (third-party) | https://github.com/bytefer/macos-vision-ocr |
| Paddle Android / iOS | https://www.paddleocr.ai/latest/en/version3.x/inference_deployment/cross_platform/android_deployment.html , …/ios_deployment.html |
| Cyrillic rec / v5 det | https://huggingface.co/api/models/PaddlePaddle/cyrillic_PP-OCRv5_mobile_rec?blobs=true , …/PP-OCRv5_mobile_det |
| RapidOCR models | https://rapidai.github.io/RapidOCRDocs/main/model_list/ |
| ExpDate dataset | https://felizang.github.io/expdate/index_expdate.html |
| Pharma NCA 2026 | https://link.springer.com/article/10.1007/s00521-026-12229-2 |
| SCPE 2024 | https://www.scpe.org/index.php/scpe/article/view/4967 |
| VLM cards | https://huggingface.co/zai-org/GLM-OCR , /Qwen/Qwen3.5-2B , /openbmb/MiniCPM-V-4.6 , /google/gemma-4-E2B-it , /lightonai/LightOnOCR-2-1B , /moondream/moondream3.1-9B-A2B |
| Gemma 4 license | https://ai.google.dev/gemma/docs/gemma_4_license (redirects to /gemma/apache_2) |
| Terms | https://www.anthropic.com/legal/commercial-terms , https://ai.google.dev/gemini-api/terms , https://openai.com/policies/row-terms-of-use/ |

## UNVERIFIED

1. Official Apple Vision language list (`ru-RU`).
2. Cyrillic PP-OCR model in Paddle mobile demos (`inference.onnx` swap).
3. Tesseract `rus.traineddata` license.
4. Licenses of the Roboflow Universe datasets listed above.
5. License and origin of the Kaggle pharma pack dataset.
6. Cyrillic OCR quality of Qwen3.5, MiniCPM-V-4.6, Gemma 4.
7. Moondream Model License 1.0 terms.
8. Whether a separate Prohibited Use Policy applies to Gemma 4.
9. Exact current OpenAI terms wording.
