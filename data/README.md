# Agricultural Dataset & Knowledge Base Documentation

## 1. Dataset Origin & Licensing
- **Dataset:** PlantVillage (David Hughes & Marcel Salathé, 2015)
- **Publication Citation:** Hughes, D., & Salathé, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics*. arXiv:1511.08060.
- **License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
- **Attribution:** PlantVillage project at Penn State University and EPFL.

## 2. Supported Target Scope (8 Classes Across 3 Crops)
| Crop | Disease Label | Scientific Pathogen | Pathogen Classification |
|---|---|---|---|
| Tomato | `Tomato___Early_blight` | *Alternaria solani* | Fungal pathogen |
| Tomato | `Tomato___Late_blight` | *Phytophthora infestans* | Oomycete (Water mold) |
| Tomato | `Tomato___healthy` | None detected | Healthy baseline |
| Potato | `Potato___Early_blight` | *Alternaria solani* | Fungal pathogen |
| Potato | `Potato___Late_blight` | *Phytophthora infestans* | Oomycete (Water mold) |
| Potato | `Potato___healthy` | None detected | Healthy baseline |
| Corn (Maize) | `Corn_(maize)___Common_rust` | *Puccinia sorghi* | Fungal rust pathogen |
| Corn (Maize) | `Corn_(maize)___healthy` | None detected | Healthy baseline |

## 3. Data Integrity & Leakage Prevention
- **Stratified Partitioning:** Stratified random split into Training (70%), Validation (15%), and Held-out Test (15%) partitions.
- **Reproducibility:** Seed fixed at `42`.
- **Zero Leakage:** Training augmentations (random flips, affine rotations, jitter) are strictly confined to the training split. Validation and test splits receive solely deterministic scaling and normalization.

## 4. Knowledge Base Structure (`disease_knowledge.json`)
Every entry is grounded in university agricultural extension and governmental agency sources (USDA ARS, UC IPM, Cornell Cooperative Extension, FAO, Purdue Extension). Chemical pesticide dosages are strictly withheld.
