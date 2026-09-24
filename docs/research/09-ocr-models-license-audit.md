# OCR / document-VLM license audit for packdate

**Access date:** 2026-09-25 (Europe/Moscow)  
**Scope:** Optional runtime dependencies for Apache-2.0 packdate (`packdate[ocr]` and optional VLM extras).  
**Policy:** Prefer Apache-2.0 / MIT / BSD; avoid AGPL hard deps, NC, OpenRAIL-restricted weights, and unclear licenses as hard deps. Distinguish **code** vs **weights**.  
**Verification rule:** Every SPDX / named-license claim cites a primary URL fetched on the access date. Unverifiable items are marked **UNVERIFIED**. No invented accuracy percentages.

---

## Summary shortlist (packdate)

| Role | Candidate | Why |
|------|-----------|-----|
| **Default OCR** | PaddleOCR + `cyrillic_PP-OCRv5_mobile_rec` (and/or PP-OCRv5 multilingual path) | Apache-2.0 code + Apache-2.0 weights; explicit Cyrillic rec model |
| **Default OCR (bench gate)** | PP-OCRv6 tiny/small/medium | Apache-2.0 project; industrial/dot-matrix improvements; **unified model is Latin+CJK, not Cyrillic** — keep v5 Cyrillic rec until a v6 Cyrillic model is verified |
| **Lighter install** | RapidOCR (ONNX of PP-OCR) | Apache-2.0 wrapper; Baidu holds upstream model copyright under Apache terms per RapidOCR README |
| **Baselines** | EasyOCR, Tesseract, docTR | Apache-2.0; EasyOCR has `ru` / Cyrillic script models |
| **Optional VLM** | PaddleOCR-VL / PaddleOCR-VL-1.6 (0.9B) | Apache-2.0; 109 languages including Russian (Cyrillic) per model card |
| **Optional VLM** | Qwen3-VL-2B-Instruct (or Qwen2-VL-2B / Qwen2.5-VL-**7B**) | Apache-2.0 on verified sizes; see per-size table |
| **Crop recognizer (bench)** | Florence-2-base (MIT); TrOCR printed (**weights license UNVERIFIED** on HF card) | Small; limited Cyrillic expectation |

**Do not** ship as hard optional deps without legal review: Surya/Chandra weights (modified OpenRAIL-M), Nougat (CC-BY-NC), OCRFlux (qwen-research NC), Qwen2.5-VL-**3B**, Qwen2.5-VL-**72B** / Qwen2-VL-**72B**, Ultralytics YOLO (AGPL), MinerU (Apache + commercial thresholds).

---

## How to read the tables

- **Commercial / redistribution OK?** for an Apache-2.0 library that *optionally depends* on the artifact (user installs extra; packdate does not vend weights into the core wheel unless separately cleared).
  - **Yes** — permissive SPDX (Apache-2.0 / MIT / BSD) on both code and weights (or weights clearly under same project Apache/MIT).
  - **Conditional** — permissive but size-specific, usage thresholds, attribution-only custom terms, or training-data caveats.
  - **No** — NC, research-only, AGPL copyleft for typical product use, or OpenRAIL commercial/competitor bans.
- **Recommendation:** Default candidate | Bench-only | Avoid | Needs legal review.

---

## 1. Classic / industrial OCR engines & wrappers

| Name | Primary repo / HF | Code license | Weights license | Commercial OK? | Cyrillic / multilingual | Packaging-date fitness (qualitative) | Install / runtime | Recommendation |
|------|-------------------|--------------|-----------------|----------------|-------------------------|--------------------------------------|-------------------|----------------|
| **PaddleOCR / PP-OCR** | [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | Apache-2.0 — [LICENSE](https://github.com/PaddlePaddle/PaddleOCR/blob/main/LICENSE) | Models released under project Apache-2.0; e.g. [cyrillic_PP-OCRv5_mobile_rec](https://huggingface.co/PaddlePaddle/cyrillic_PP-OCRv5_mobile_rec) `license: apache-2.0` | **Yes** | Dedicated Cyrillic rec: `cyrillic_PP-OCRv5_mobile_rec` (HF card). PP-OCRv6 unified: CN/EN/JA + Latin scripts — **not Cyrillic** ([PP-OCRv6 docs](https://www.paddleocr.ai/latest/en/version3.x/algorithm/PP-OCRv6/PP-OCRv6.html); [v3.7.0 release](https://github.com/PaddlePaddle/PaddleOCR/releases/tag/v3.7.0)) | Strong industrial baseline; v6 docs claim gains on digital displays, **dot-matrix**, tire prints, industrial text | PaddlePaddle CPU/GPU; HPI/ONNX/OpenVINO/TensorRT paths in docs; heavier than ONNX-only wrappers | **Default candidate** (v5 Cyrillic + v6 Latin industrial bench) |
| **RapidOCR** | [RapidAI/RapidOCR](https://github.com/RapidAI/RapidOCR) | Apache-2.0 — [LICENSE](https://github.com/RapidAI/RapidOCR/blob/main/LICENSE) | Upstream PP-OCR models (Baidu copyright); RapidOCR states project + converted ONNX under Apache-2.0 ([README](https://github.com/RapidAI/RapidOCR/blob/main/README.md)) | **Yes** (with NOTICE/attribution) | Inherits whatever PP-OCR models you load (use Cyrillic PP-OCR rec) | Same family as PP-OCR; good for CIJ/thermal *if* models + preprocess are right | **ONNX Runtime** CPU/GPU; lighter than full Paddle stack | **Default candidate** (lighter `packdate[ocr]` path) |
| **EasyOCR** | [JaidedAI/EasyOCR](https://github.com/JaidedAI/EasyOCR) | Apache-2.0 — [LICENSE](https://github.com/JaidedAI/EasyOCR/blob/master/LICENSE) | Bundled recognition checkpoints distributed with project (Apache-2.0 repo); no separate NC card found | **Yes** | `ru` in `cyrillic_lang_list` — [config.py](https://github.com/JaidedAI/EasyOCR/blob/master/easyocr/config.py) | Useful baseline; historically weaker than Paddle on stamps in third-party notes (do not treat as packdate-measured) | PyTorch; downloads weights on first use | **Bench-only** / optional baseline |
| **Tesseract** | [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) | Apache-2.0 — [LICENSE](https://github.com/tesseract-ocr/tesseract/blob/main/LICENSE) | Traineddata packs are separate; eng/rus packs commonly used under Apache-aligned tessdata projects — **confirm pack LICENSE** before bundling | **Yes** for engine; **Conditional** if bundling third-party traineddata | `rus` / Cyrillic traineddata available upstream | Weak on inkjet/dot-matrix without heavy preprocess; OK baseline | Native binary + `pytesseract`; CPU | **Bench-only** |
| **docTR** | [mindee/doctr](https://github.com/mindee/doctr) | Apache-2.0 — [LICENSE](https://github.com/mindee/doctr/blob/main/LICENSE) | Pretrained models distributed with project under Apache-2.0 | **Yes** | Multilingual models exist; **RU/Cyrillic strength UNVERIFIED** for packaging | Document-oriented; packaging stamps need ROI + preprocess | PyTorch/TensorFlow; CPU/GPU | **Bench-only** |
| **keras-ocr** | [faustomorales/keras-ocr](https://github.com/faustomorales/keras-ocr) | MIT — [LICENSE](https://github.com/faustomorales/keras-ocr/blob/master/LICENSE) | CRAFT/CRNN weights via project; treat as MIT-aligned unless a model card says otherwise | **Yes** | Primarily Latin/English craft+crnn demos; Cyrillic **weak / UNVERIFIED** | Aging stack; not ideal for RU packaging | TensorFlow/Keras | **Bench-only** (low priority) |

---

## 2. PaddleOCR / PP-OCR family (v5, v6, Cyrillic, RapidOCR, PaddleOCR-VL)

| Artifact | URL | Code | Weights | Commercial OK? | Cyrillic | Notes | Recommendation |
|----------|-----|------|---------|----------------|----------|-------|----------------|
| PaddleOCR toolkit | [GitHub LICENSE](https://github.com/PaddlePaddle/PaddleOCR/blob/main/LICENSE) | Apache-2.0 | — | Yes | — | Optional deps historically included AGPL pieces (e.g. PyMuPDF) — keep doc-parser extras optional | Default |
| `cyrillic_PP-OCRv5_mobile_rec` | [HF card](https://huggingface.co/PaddlePaddle/cyrillic_PP-OCRv5_mobile_rec) | (toolkit Apache-2.0) | `license: apache-2.0` | **Yes** | **Yes** (purpose-built) | Reported line accuracy on card is upstream’s own metric — not packing-date field accuracy | **Default candidate** |
| PP-OCRv6 tiny/small/medium | [Docs](https://www.paddleocr.ai/latest/en/version3.x/algorithm/PP-OCRv6/PP-OCRv6.html), [v3.7.0](https://github.com/PaddlePaddle/PaddleOCR/releases/tag/v3.7.0) | Apache-2.0 (repo) | Expected Apache-2.0 with Paddle models; **specific HF `license:` field for every v6 checkpoint: UNVERIFIED** (HF API returned empty for `PP-OCRv6_mobile_rec` on access date) | **Yes** if weights Apache (project norm) | **No in unified 50-lang model** (CN/EN/JA + Latin only per docs) | Explicit industrial / **dot-matrix** improvements | **Default candidate** for Latin industrial bench; pair with v5 Cyrillic for RU |
| PaddleOCR-VL 0.9B | [PaddlePaddle/PaddleOCR-VL](https://huggingface.co/PaddlePaddle/PaddleOCR-VL) | Apache-2.0 (PaddleOCR) | `license: apache-2.0`; LICENSE in repo | **Yes** | Card: **109 languages** incl. Russian (Cyrillic) | Doc/layout VLM; GPU preferred; vLLM path | **Optional VLM extra** |
| PaddleOCR-VL-1.6 | [PaddlePaddle/PaddleOCR-VL-1.6](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6) | Apache-2.0 | `license: apache-2.0` | **Yes** | Multilingual (same family) | Shipped with PaddleOCR ≥ 3.6; architecture compatible with 1.5 | **Optional VLM extra** (prefer over 1.0 if deps allow) |

---

## 3. Transformer OCR & small VLMs

| Name | Primary | Code license | Weights license | Commercial OK? | Cyrillic | Fitness | Runtime | Recommendation |
|------|---------|--------------|-----------------|----------------|----------|---------|---------|----------------|
| **TrOCR** (e.g. `microsoft/trocr-base-printed`) | [unilm/trocr](https://github.com/microsoft/unilm/tree/master/trocr), [HF](https://huggingface.co/microsoft/trocr-base-printed) | MIT — [unilm LICENSE](https://github.com/microsoft/unilm/blob/master/LICENSE) | **UNVERIFIED** — HF card has **no** `license:` YAML field (API `license: null` on 2026-09-25) | **Conditional** until HF/weights SPDX confirmed | Printed EN (SROIE); Cyrillic **not** claimed | Crop-line recognizer after ROI; not full-frame multilingual | transformers + torch; CPU possible, slow | **Bench-only**; **Needs legal review** before redistributing weights |
| **Florence-2-base** | [microsoft/Florence-2-base](https://huggingface.co/microsoft/Florence-2-base) | MIT (card `license: mit`, [LICENSE link](https://huggingface.co/microsoft/Florence-2-base/resolve/main/LICENSE)) | MIT (same card) | **Yes** | Generalist; Cyrillic OCR quality **UNVERIFIED** | `<OCR>` / `<OCR_WITH_REGION>` prompts; packaging stamps unknown | ~0.23B; GPU preferred | **Bench-only** |
| **GOT-OCR2.0** | [stepfun-ai/GOT-OCR2_0](https://huggingface.co/stepfun-ai/GOT-OCR2_0), [GitHub](https://github.com/Ucas-HaoranWei/GOT-OCR2.0) | Apache-2.0 (HF `license: apache-2.0`) | Apache-2.0 (card) | **Conditional** — GitHub historically notes **training data** CC-BY-NC; confirm whether that limits your use of weights | Multilingual tag | Strong general OCR hype; document-biased vs expiry crops | ~GPU; transformers custom code | **Bench-only** / **Needs legal review** (data license) |
| **olmOCR** (e.g. olmOCR-2-7B-1025) | [allenai/olmocr](https://github.com/allenai/olmocr), [HF](https://huggingface.co/allenai/olmOCR-2-7B-1025) | Apache-2.0 | `license: apache-2.0`; finetuned from Qwen2.5-VL-7B-Instruct | **Yes** (Apache); card also cites Ai2 Responsible Use Guidelines (policy, not SPDX) | Document English-centric; packaging Cyrillic **UNVERIFIED** | PDF page OCR toolkit; heavy for packdate core | 7B VLM; GPU / vLLM | **Bench-only** (doc bias) |
| **DeepSeek-OCR** | [deepseek-ai/DeepSeek-OCR](https://huggingface.co/deepseek-ai/DeepSeek-OCR) | MIT (card `license: mit`; [GitHub LICENSE](https://github.com/deepseek-ai/DeepSeek-OCR/blob/main/LICENSE)) | MIT (card) | **Yes** | Multilingual tag | Document/markdown oriented; not expiry-productized | GPU; vLLM support | **Bench-only** |
| **Nougat** | [facebookresearch/nougat](https://github.com/facebookresearch/nougat), [facebook/nougat-base](https://huggingface.co/facebook/nougat-base) | MIT (code) | **CC-BY-NC-4.0** — [LICENSE-MODEL.md](https://github.com/facebookresearch/nougat/blob/main/LICENSE-MODEL.md), HF `license: cc-by-nc-4.0` | **No** (NC weights) | Academic PDF EN | Wrong domain (scientific PDF → MD) | GPU | **Avoid** |
| **Surya** | [datalab-to/surya](https://github.com/datalab-to/surya) | Apache-2.0 — [LICENSE](https://github.com/datalab-to/surya/blob/master/LICENSE) | Modified OpenRAIL-M — [MODEL_LICENSE](https://github.com/datalab-to/surya/blob/master/MODEL_LICENSE) ($5M revenue/funding caps; no competing product/service) | **No** as hard optional dep for permissive commercial redistribution | Multilingual | Strong OCR quality claims — blocked by weight license | GPU | **Avoid** (weights) |
| **Chandra** | [datalab-to/chandra](https://github.com/datalab-to/chandra), [chandra-ocr-2](https://huggingface.co/datalab-to/chandra-ocr-2) | Apache-2.0 (code) | OpenRAIL / modified OpenRAIL-M; card: free under **$2M** funding/revenue; no competitive use ([Commercial Usage](https://huggingface.co/datalab-to/chandra-ocr-2)) | **No** as hard dep | Card shows Russian example / multilingual benches | Doc OCR; OpenRAIL blocks | GPU / vLLM | **Avoid** |
| **OCRFlux-3B** | [ChatDOC/OCRFlux-3B](https://huggingface.co/ChatDOC/OCRFlux-3B) | Toolkit separate | `license_name: qwen-research` → [Qwen RESEARCH LICENSE](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/blob/main/LICENSE) (**non-commercial**) | **No** | EN/ZH doc focus | PDF markdown toolkit | 3B GPU | **Avoid** |
| **MinerU** | [opendatalab/MinerU](https://github.com/opendatalab/MinerU) | **MinerU Open Source License** = Apache-2.0 + thresholds (100M MAU or USD 20M monthly revenue) + attribution — [LICENSE.md](https://github.com/opendatalab/MinerU/blob/master/LICENSE.md) | Depends on bundled models (check each) | **Conditional** | Doc parsing | Pipeline, not stamp OCR | Heavy | **Needs legal review** / Avoid as hard dep; old AGPL versions if pinned pre-relicense |

---

## 4. Qwen VL family — **check each size**

| Model | HF card | Weights license (verified) | Commercial OK? | Recommendation |
|-------|---------|----------------------------|----------------|----------------|
| **Qwen2-VL-2B-Instruct** | [card](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct) | `license: apache-2.0` | **Yes** | Optional VLM / control path |
| **Qwen2-VL-7B-Instruct** | [card](https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct) | `license: apache-2.0` | **Yes** | Optional VLM (heavier) |
| **Qwen2-VL-72B-Instruct** | [card](https://huggingface.co/Qwen/Qwen2-VL-72B-Instruct) | `license_name: tongyi-qianwen` (other) | **Conditional** — custom Tongyi terms; not Apache | Avoid for default; **Needs legal review** |
| **Qwen2.5-VL-3B-Instruct** | [card](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct) | `license_name: qwen-research` — [LICENSE](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/blob/main/LICENSE) **FOR NON-COMMERCIAL PURPOSES ONLY** | **No** | **Avoid** |
| **Qwen2.5-VL-7B-Instruct** | [card](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct) | `license: apache-2.0` | **Yes** | Optional VLM control (ROADMAP-aligned) |
| **Qwen2.5-VL-72B-Instruct** | [card](https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct) | `license_name: qwen` — [Qwen LICENSE AGREEMENT](https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct/blob/main/LICENSE) (commercial use OK under terms; **>100M MAU** needs separate license) | **Conditional** | Avoid as default extra; legal review if ever needed |
| **Qwen3-VL-2B-Instruct** | [card](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct) | `license: apache-2.0`; expanded OCR (32 languages claimed on card) | **Yes** | **Optional VLM** (preferred small control) |
| **Qwen3-VL-8B-Instruct** | [card](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct) | `license: apache-2.0` | **Yes** | Optional VLM (heavier) |

Multilingual / Cyrillic: Qwen2-VL cards claim European languages in-image; Qwen3-VL claims expanded OCR languages. **Packaging-date field quality remains UNVERIFIED** (measure on RU fixtures).

---

## 5. Newer 2025–2026 hyped OSS (spot check)

| Name | License note | For packdate |
|------|--------------|--------------|
| **dots.ocr** | Code often MIT; separate **custom model agreement** on HF — **Needs legal review** before depending | Bench-only after license read |
| **MonkeyOCR** | Reports: code Apache-2.0, some weights academic/NC — **UNVERIFIED** primary fetch (HF 401 on access date) | Do not shortlist until card fetched |
| **Hobby HF Expiry_*** | Empty/weak cards | Avoid as deps |

---

## 6. Explicit **Avoid** list (hard optional deps)

| Component | Reason | Primary citation |
|-----------|--------|------------------|
| **Ultralytics YOLO** | AGPL-3.0 copyleft | [ultralytics/ultralytics LICENSE](https://github.com/ultralytics/ultralytics/blob/main/LICENSE) |
| **Nougat weights** | CC-BY-NC-4.0 | [LICENSE-MODEL.md](https://github.com/facebookresearch/nougat/blob/main/LICENSE-MODEL.md), [HF nougat-base](https://huggingface.co/facebook/nougat-base) |
| **Surya weights** | Modified OpenRAIL-M ($5M + no competing product) | [MODEL_LICENSE](https://github.com/datalab-to/surya/blob/master/MODEL_LICENSE) |
| **Chandra weights** | Modified OpenRAIL-M ($2M on card + no API competition) | [chandra-ocr-2 README](https://huggingface.co/datalab-to/chandra-ocr-2) |
| **OCRFlux-3B** | qwen-research (NC) | [OCRFlux-3B](https://huggingface.co/ChatDOC/OCRFlux-3B) → [Qwen RESEARCH LICENSE](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/blob/main/LICENSE) |
| **Qwen2.5-VL-3B** | qwen-research NC | same LICENSE |
| **Qwen2.5-VL-72B / Qwen2-VL-72B** | Custom Qwen / Tongyi (not Apache); MAU clause on Qwen LICENSE | [72B Qwen LICENSE](https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct/blob/main/LICENSE), [Qwen2-VL-72B card](https://huggingface.co/Qwen/Qwen2-VL-72B-Instruct) |
| **MinerU as hard dep** | Apache + commercial thresholds + attribution; older releases AGPL | [LICENSE.md](https://github.com/opendatalab/MinerU/blob/master/LICENSE.md) |

---

## 7. Recommended extras sketch

```text
packdate[ocr]     → RapidOCR and/or paddleocr + cyrillic_PP-OCRv5_mobile_rec
                    (+ optional PP-OCRv6 for Latin/industrial A/B)
packdate[ocr-vl]  → paddleocr[doc-parser] / PaddleOCR-VL-1.6  OR  transformers + Qwen3-VL-2B / Qwen2.5-VL-7B
packdate[ocr-bench] → easyocr, pytesseract, florence-2 (dev only)
```

Core package stays dependency-light; extras pull OCR stacks.

---

## 8. Conflicts / errata vs prior research archive

| Prior claim | Status after 2026-09-25 fetch | Correction |
|-------------|-------------------------------|------------|
| “Qwen2.5-VL is research/NC” ([08](08-dependencies-shortlist.md), [03](03-ocr-verdict.md)) | **Partially false as blanket** | **3B** = qwen-research NC; **7B** = Apache-2.0; **72B** = Qwen LICENSE (conditional). Errata in [README](README.md) already warned per-size; this audit confirms. |
| “Qwen2-VL-2B Apache” ([08](08-dependencies-shortlist.md)) | **Confirmed** | Keep |
| “PP-OCRv6 + cyrillic as one stack” ([03](03-ocr-verdict.md), ROADMAP) | **Misleading** | v6 unified model = CN/EN/JA + Latin **only**. Keep **`cyrillic_PP-OCRv5_mobile_rec`** for RU until a v6 Cyrillic checkpoint is published and licensed. |
| “Florence-2 / TrOCR MIT” ([08](08-dependencies-shortlist.md)) | Florence **confirmed MIT**; TrOCR **code MIT**, **weights SPDX missing on HF** | Soften TrOCR to Conditional / UNVERIFIED weights |
| “Surya OpenRAIL” | **Confirmed** (code Apache ≠ weights) | Avoid weights |
| “Nougat NC” | **Confirmed** CC-BY-NC-4.0 weights | Avoid |
| “Chandra OpenRAIL-ish” | **Confirmed** modified OpenRAIL-M | Avoid |
| “OCRFlux qwen-research” | **Confirmed** | Avoid |
| “MinerU AGPL” ([03](03-ocr-verdict.md) “old MinerU AGPL”) | **Stale for current master** | Current = Apache-based custom with MAU/revenue thresholds; pre-3.1 may still be AGPL |
| “olmOCR / DeepSeek avoid first (doc bias)” ([05](05-ocr-sota-notes.md)) | License **OK** (Apache / MIT); domain bias still valid | Reclassify as **Bench-only**, not license-Avoid |

---

## 9. Still **UNVERIFIED** / gaps

1. Exact Hugging Face `license:` metadata for each **PP-OCRv6_*** checkpoint (API empty / unauthorized for some IDs on access date) — rely on PaddleOCR Apache project norm until each card is opened.
2. Whether a **Cyrillic PP-OCRv6** recognition model exists yet.
3. **TrOCR** printed weights SPDX on HF (no license field).
4. **GOT-OCR2** training-data CC-BY-NC implications for commercial use of Apache weights.
5. **EasyOCR / keras-ocr / docTR** third-party weight provenance beyond repo LICENSE.
6. **Tesseract** `rus.traineddata` redistributable LICENSE for any tessdata pack you vendor.
7. **MonkeyOCR / dots.ocr** full weight agreements (partial search only).
8. Field fitness of any VLM on **RU inkjet/thermal packaging** — must be measured on packdate fixtures (no invented %).

---

## 10. Citation log (primary URLs fetched 2026-09-25)

- https://github.com/PaddlePaddle/PaddleOCR/blob/main/LICENSE  
- https://github.com/PaddlePaddle/PaddleOCR/releases/tag/v3.7.0  
- https://www.paddleocr.ai/latest/en/version3.x/algorithm/PP-OCRv6/PP-OCRv6.html  
- https://huggingface.co/PaddlePaddle/cyrillic_PP-OCRv5_mobile_rec  
- https://huggingface.co/PaddlePaddle/PaddleOCR-VL  
- https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6  
- https://github.com/RapidAI/RapidOCR/blob/main/LICENSE  
- https://github.com/JaidedAI/EasyOCR/blob/master/LICENSE  
- https://github.com/tesseract-ocr/tesseract/blob/main/LICENSE  
- https://github.com/mindee/doctr/blob/main/LICENSE  
- https://github.com/faustomorales/keras-ocr/blob/master/LICENSE  
- https://github.com/microsoft/unilm/blob/master/LICENSE  
- https://huggingface.co/microsoft/Florence-2-base  
- https://huggingface.co/microsoft/trocr-base-printed  
- https://huggingface.co/stepfun-ai/GOT-OCR2_0  
- https://huggingface.co/allenai/olmOCR-2-7B-1025  
- https://huggingface.co/deepseek-ai/DeepSeek-OCR  
- https://github.com/facebookresearch/nougat/blob/main/LICENSE-MODEL.md  
- https://huggingface.co/facebook/nougat-base  
- https://github.com/datalab-to/surya/blob/master/MODEL_LICENSE  
- https://huggingface.co/datalab-to/chandra-ocr-2  
- https://huggingface.co/ChatDOC/OCRFlux-3B  
- https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/blob/main/LICENSE  
- https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct  
- https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct/blob/main/LICENSE  
- https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct  
- https://huggingface.co/Qwen/Qwen2-VL-72B-Instruct  
- https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct  
- https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct  
- https://github.com/opendatalab/MinerU/blob/master/LICENSE.md  
- https://github.com/ultralytics/ultralytics/blob/main/LICENSE  

---

*Archive note: historical; re-verify before promoting into README / ARCHITECTURE marketing claims.*
