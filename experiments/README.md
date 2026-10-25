# Experimental Benchmarks & Evaluation Results

This directory contains real, measured experimental results generated on held-out test datasets and structured agronomic decision scenarios. **No values are fabricated.**

---

## Experiment A: Crop Disease Classification
- **Backbone Architecture:** MobileNetV2 (Pre-trained ImageNet transfer learning)
- **Dataset:** PlantVillage (David Hughes & Marcel Salathé, 2015, CC BY-SA 4.0)
- **Supported Classes:** 8 balanced classes across Tomato, Potato, and Corn
- **Hardware Platform:** x86_64 CPU (Intel/AMD standard desktop/laptop runtime)
- **Held-Out Test Sample Size:** 27 images (strictly separated from training and validation tuning)

### Quantitative Classification Metrics (Held-Out Test Set)
| Metric | Measured Value | Agronomic Significance |
|---|---|---|
| **Overall Accuracy** | **85.19%** | Correct foliar classification rate on held-out test data |
| **Macro Precision** | **0.8750** | Average purity across all 8 classes |
| **Macro Recall** | **0.8333** | Sensitivity in identifying true positive pathogen cases |
| **Macro F1-Score** | **0.8333** | Harmonic mean balancing precision and recall |
| **Weighted F1-Score** | **0.8519** | Sample-weighted harmonic mean |

### Per-Class Test Breakdown
| Target Class Name | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| `Tomato___Early_blight` | 0.5000 | 0.3333 | 0.4000 | 3 |
| `Tomato___Late_blight` | 1.0000 | 0.6667 | 0.8000 | 3 |
| `Tomato___healthy` | 0.5000 | 1.0000 | 0.6667 | 3 |
| `Potato___Early_blight` | 1.0000 | 1.0000 | 1.0000 | 3 |
| `Potato___Late_blight` | 1.0000 | 0.6667 | 0.8000 | 3 |
| `Potato___healthy` | 1.0000 | 1.0000 | 1.0000 | 3 |
| `Corn_(maize)___Common_rust` | 1.0000 | 1.0000 | 1.0000 | 3 |
| `Corn_(maize)___healthy` | 1.0000 | 1.0000 | 1.0000 | 6 |

---

## Experiment B: Irrigation Rule Matrix Verification
Tested across 6 standardized agronomic field scenarios (`data/sample_inputs.json`):

| Scenario ID | Test Conditions | Sourced Rule | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|---|
| `SC-01` | Tomato (Veg), Loam, Moisture: 48.5%, Rain: 0 mm | MAD Baseline (35%) | Defer irrigation | "Irrigation may not be needed yet." | **PASS** |
| `SC-02` | Tomato (Flowering), Sandy, Moisture: 22.0%, Rain: 0 mm | Deficit Trigger (49%) | Apply root irrigation | "Irrigation may be needed." (Urgency: High) | **PASS** |
| `SC-03` | Potato (Fruiting), Clay, Moisture: 32.0%, Rain: 0 mm | Buffer Zone Margin | Reassess in 24h | "Reassess after monitoring soil conditions." | **PASS** |
| `SC-04` | Corn, Moisture: None, Rain: None | Missing Data Check | Withhold decision | "Insufficient data to recommend irrigation." | **PASS** |
| `SC-05` | Potato, Moisture: 45%, Rain: 28.5 mm (24h) | Precipitation Override | Defer water application | "Irrigation may not be needed yet." | **PASS** |
| `SC-06` | Declared: Corn, Upload: Tomato Early Blight | Crop Mismatch Gating | Warn farmer & withhold | Crop Mismatch Warning (Deferred treatment) | **PASS** |

---

## Experiment C: Latency & Hardware Efficiency
- **Mean Inference Latency:** **25.75 ms** per image on standard CPU
- **95th Percentile Latency:** **43.91 ms**
- **Peak RAM Footprint:** &lt; 280 MB during active PyTorch forward pass
- **Model File Size:** 9.8 MB (`mobilenetv2_crop_disease.pth`)
- **Suitability:** Capable of running on edge computing hardware (Raspberry Pi 4 / rural low-bandwidth servers).
