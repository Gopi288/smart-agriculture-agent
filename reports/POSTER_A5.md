# SMART AGRICULTURE AGENT
## AI-Based Crop Disease Detection and Irrigation Advisory System
### Technical Conference Poster (A5 Compact Layout)

---

```
+-----------------------------------------------------------------------------------+
|                        SMART AGRICULTURE AGENT                                    |
|       AI-Based Crop Disease Detection & Irrigation Advisory System                |
|             B.Tech Computer Science & Engineering Mini-Capstone                   |
+-----------------------------------------------------------------------------------+
| TEAM MEMBERS:                                                                     |
| Member 1: AI & Vision       Member 2: Decision Engines                            |
| Member 3: Full-Stack Dev    Member 4: QA & Technical Mentor                       |
+-----------------------------------------------------------------------------------+
| PROBLEM STATEMENT:                                                                |
| Crop diseases and inaccurate irrigation reduce yields by 20-40%. Farmers lack     |
| immediate diagnostic access and often over-apply chemicals and irrigation water.  |
+-----------------------------------------------------------------------------------+
| OBJECTIVE:                                                                        |
| Deliver an edge-capable decision-support system coupling deep transfer learning   |
| with deterministic agronomic water-balance and extension-verified IPM guidance.   |
+-----------------------------------------------------------------------------------+
| AI TECHNIQUE:                                                                     |
| - Architecture: MobileNetV2 with inverted residuals & linear bottlenecks          |
| - Transfer Learning: Pre-trained ImageNet backbone fine-tuned on PlantVillage     |
| - Classification Head: 2-stage dense head with Dropout (0.30) regularization      |
| - Confidence Gating: Inconclusive thresholding (tau = 70%) & ambiguity margins    |
+-----------------------------------------------------------------------------------+
| INPUT -> PROCESSING -> OUTPUT PIPELINE:                                           |
| [Leaf Image (JPG/PNG) + Declared Crop + Soil Moisture + Rainfall (mm)]            |
|                           |                                                       |
|                           v                                                       |
| [Preprocessing 224x224 -> MobileNetV2 -> Softmax & Margin Check]                  |
|                           |                                                       |
|                           v                                                       |
| [Rule Engine: Confidence Gate -> Crop Mismatch Check -> IPM Guidance]             |
| [Irrigation Engine: FAO MAD Threshold -> Soil Texture Adjustment]                 |
|                           |                                                       |
|                           v                                                       |
| [Prediction Result (85.2% Test Acc) + IPM Cultural Practices + Water Advisory]   |
+-----------------------------------------------------------------------------------+
| ACTUAL MEASURED RESULTS (Held-Out Test Set):                                      |
| - Overall Test Accuracy:   85.19%        - Mean CPU Latency:  25.75 ms / image    |
| - Macro F1-Score:         0.8333        - 95th Pct Latency:  43.91 ms            |
| - Automated Pytest Suite: 31/31 PASSED  - Model Size:        9.8 MB (.pth)        |
+-----------------------------------------------------------------------------------+
| KEY IMPLEMENTATION DETAILS:                                                       |
| - Stack: Python 3.12, PyTorch CPU, Flask 3.1, SQLite, HTML5/CSS3                  |
| - Scope: 8 classes across Tomato, Potato, and Corn (Solanaceae + Cereals)         |
| - Ethics: Synthetic chemical dosages withheld; missing data never assumed zero    |
+-----------------------------------------------------------------------------------+
| REAL-WORLD RELEVANCE & LIMITATIONS:                                               |
| - Relevance: Fast, edge-deployable diagnostic tool for rural agricultural kiosks.  |
| - Limitations: Trained on solid-background leaves; needs field-lighting tuning.   |
+-----------------------------------------------------------------------------------+
| CONCLUSION & FUTURE SCOPE:                                                        |
| Demonstrates responsible, explainable agricultural AI. Future work includes IoT   |
| LoRaWAN soil moisture capacitance probes and regional language localizations.     |
+-----------------------------------------------------------------------------------+
```
