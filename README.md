# Smart Agriculture Agent: AI-Based Crop Disease Detection & Irrigation Advisory System

An undergraduate B.Tech Computer Science and Engineering AI Mini-Capstone Project.

---

## 1. What the Project Does
The **Smart Agriculture Agent** is an end-to-end, edge-capable agricultural decision-support application that empowers farmers, students, and agronomists to:
1. Authenticate securely via session-based authentication with bcrypt-equivalent PBKDF2 password hashing, CSRF tokens, and open-redirect protection.
2. Select between **3 custom-crafted themes**: **Light Mode** (high-contrast agricultural daytime), **Dark Mode** (night/field eye-strain reduction), and **Glassmorphism Mode** (frosted translucent depth).
3. Navigate a modern **collapsible left-hand dashboard** with 10 views and keyboard shortcuts (`[` key).
4. Identify foliar crop diseases from uploaded leaf images using transfer-learning computer vision (**MobileNetV2**).
5. Review prediction confidence scores alongside uncertainty warnings and supported alternative hypotheses.
6. Access verified, extension-grounded non-chemical Integrated Pest Management (IPM) and sanitation guidance.
7. Calculate crop-specific irrigation requirements across **24 registered crops** using FAO-56 Management Allowed Depletion (MAD), phenological stage adjustments, soil texture holding capacity, and precipitation override rules.
8. Interact with an **Agricultural Decision Support Assistant** for instant Q&A on pathogens, moisture thresholds, and $K_c$ coefficients.
9. Inspect empirical benchmark evaluation metrics on the held-out test split (85.19% accuracy, 25.75 ms CPU latency).
10. Review chronological audit logs of previous analyses and download structured PDF/JSON field summary reports.

---

## 2. Default Demonstration Credentials
The application is pre-seeded with a demonstration farmer account:
- **Username:** `farmer_demo`
- **Password:** `FarmerPassword123!`
- **Role:** `farmer`

To create additional administrators or farmer accounts via the CLI:
```powershell
& ".\.venv\Scripts\python.exe" create_admin.py --username admin --email admin@smartagri.local --password "AdminSecretPass123!" --role admin
```

---

## 3. The 10 Views in the Application
The collapsible left-hand navigation sidebar provides 10 views:
1. **Dashboard (`/`):** Real-time system telemetry, model readiness status, quick action launcher, and recent analyses audit summary.
2. **Crop Disease Detection (`/disease/`):** Foliar image upload, MobileNetV2 neural vision inference, confidence threshold gating, hypothesis ranking, and IPM guidance.
3. **Irrigation Advisor (`/irrigation/`):** FAO-56 water-balance rule engine supporting all 24 registered crops with phenological stage sensitivity, soil texture adjustments, and weather override.
4. **Agricultural Assistant (`/assistant`):** Interactive agronomy decision assistant answering questions on plant pathogens, moisture depletion, and irrigation science.
5. **Audit History (`/history/`):** Chronological historical analyses with filtering and downloadable structured reports.
6. **Model Performance (`/performance`):** Empirical test benchmarks (85.19% Accuracy, 0.8333 Macro F1, 25.75 ms latency), confusion matrix, and architectural breakdown.
7. **Supported Crops Explorer (`/crops`):** Authoritative catalog of all 24 registered varieties with search, category filtering, botanical taxonomy, $K_c$ curves, and IPM disease profiles.
8. **About Project (`/about`):** Technical capstone documentation, software architecture, and 4-member student team distribution.
9. **Settings (`/settings`):** System configuration, theme switcher preview, decision threshold display ($\tau = 0.70$), SQLite database telemetry, and session management.
10. **Sign Out (`/auth/logout`):** Terminate authenticated session and redirect safely to the login screen.

---

## 4. The 24 Supported Crops & Architecture
To ensure scientific accuracy and capstone integrity, the crop registry (`app/utils/crop_registry.py`) cleanly separates AI visual models from agronomic knowledge:

| # | Crop Name | Botanical Name | Category | AI Foliar Model | FAO-56 Irrigation & IPM |
|---|---|---|---|:---:|:---:|
| 1 | **Tomato** | *Solanum lycopersicum* | Vegetable | ✅ (3 Classes) | ✅ ($K_c: 0.60 - 1.15$) |
| 2 | **Potato** | *Solanum tuberosum* | Vegetable | ✅ (3 Classes) | ✅ ($K_c: 0.50 - 1.15$) |
| 3 | **Maize / Corn** | *Zea mays* | Cereal | ✅ (2 Classes) | ✅ ($K_c: 0.30 - 1.20$) |
| 4 | **Pepper / Bell Pepper** | *Capsicum annuum* | Vegetable | Pending Field Data | ✅ ($K_c: 0.60 - 1.05$) |
| 5 | **Rice** | *Oryza sativa* | Cereal | Pending Field Data | ✅ ($K_c: 1.10 - 1.25$) |
| 6 | **Wheat** | *Triticum aestivum* | Cereal | Pending Field Data | ✅ ($K_c: 0.40 - 1.15$) |
| 7 | **Cotton** | *Gossypium hirsutum* | Cash Crop | Pending Field Data | ✅ ($K_c: 0.45 - 1.15$) |
| 8 | **Chilli** | *Capsicum frutescens* | Vegetable | Pending Field Data | ✅ ($K_c: 0.60 - 1.05$) |
| 9 | **Brinjal / Eggplant** | *Solanum melongena* | Vegetable | Pending Field Data | ✅ ($K_c: 0.60 - 1.05$) |
| 10 | **Groundnut / Peanut** | *Arachis hypogaea* | Oilseed | Pending Field Data | ✅ ($K_c: 0.40 - 1.15$) |
| 11 | **Soybean** | *Glycine max* | Oilseed | Pending Field Data | ✅ ($K_c: 0.40 - 1.15$) |
| 12 | **Sugarcane** | *Saccharum officinarum* | Cash Crop | Pending Field Data | ✅ ($K_c: 0.40 - 1.25$) |
| 13 | **Banana** | *Musa acuminata* | Fruit | Pending Field Data | ✅ ($K_c: 1.00 - 1.20$) |
| 14 | **Mango** | *Mangifera indica* | Fruit | Pending Field Data | ✅ ($K_c: 0.60 - 0.80$) |
| 15 | **Grapes** | *Vitis vinifera* | Fruit | Pending Field Data | ✅ ($K_c: 0.30 - 0.70$) |
| 16 | **Apple** | *Malus domestica* | Fruit | Pending Field Data | ✅ ($K_c: 0.50 - 0.95$) |
| 17 | **Citrus** | *Citrus sinensis* | Fruit | Pending Field Data | ✅ ($K_c: 0.70 - 0.70$) |
| 18 | **Cucumber** | *Cucumis sativus* | Vegetable | Pending Field Data | ✅ ($K_c: 0.60 - 1.00$) |
| 19 | **Onion** | *Allium cepa* | Vegetable | Pending Field Data | ✅ ($K_c: 0.70 - 1.05$) |
| 20 | **Chickpea** | *Cicer arietinum* | Pulse | Pending Field Data | ✅ ($K_c: 0.40 - 1.00$) |
| 21 | **Pigeon Pea** | *Cajanus cajan* | Pulse | Pending Field Data | ✅ ($K_c: 0.35 - 1.00$) |
| 22 | **Okra** | *Abelmoschus esculentus* | Vegetable | Pending Field Data | ✅ ($K_c: 0.50 - 1.00$) |
| 23 | **Mustard** | *Brassica juncea* | Oilseed | Pending Field Data | ✅ ($K_c: 0.35 - 1.05$) |
| 24 | **Sunflower** | *Helianthus annuus* | Oilseed | Pending Field Data | ✅ ($K_c: 0.35 - 1.15$) |

---

## 5. Three-Mode Theme Switcher
- **Light Theme (Default):** Clean, high-contrast agricultural palette (`#1b5e20`, `#f8faf8`) for bright daytime outdoor usage.
- **Dark Theme:** Low-glare dark green and charcoal background (`#0c140e`, `#142017`) with emerald accents (`#10b981`).
- **Glassmorphism Theme:** Translucent frosted panels (`backdrop-filter: blur(16px); background: rgba(...)`), delicate borders, and glowing highlights.
- **Instant Persistence:** Theme preferences are automatically saved in `localStorage` and applied before DOM rendering to completely eliminate Flash of Unstyled Content (FOUC).

---

## 6. Installation & Execution

### Prerequisites
- Windows 10/11 (PowerShell)
- Python 3.12 (64-bit) in dedicated virtual environment (`.venv`)

### Exact Windows PowerShell Commands
```powershell
# 1. Navigate to the project root directory
Set-Location "C:\Users\tammi\.gemini\antigravity\scratch\smart-agriculture-agent"

# 2. Start the Flask application
& ".\.venv\Scripts\python.exe" app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**
Sign in with `farmer_demo` / `FarmerPassword123!` or use the one-click demo filler on the login page.

---

## 7. Running Automated Tests
Run the complete automated pytest suite:
```powershell
& ".\.venv\Scripts\python.exe" -m pytest tests -v
```
**Test Suite Status:** **49 passed in ~19.0 seconds (100% test pass rate)** covering:
- Authentication, session security, CSRF protection, and open redirect prevention (`test_auth.py`).
- Neural model inference, preprocessing, and missing model safety (`test_classifier.py`).
- Agricultural recommendation rules, confidence gating, and crop mismatch (`test_recommendations.py`).
- FAO-56 irrigation calculations, moisture deficits, and rainfall overrides (`test_irrigation.py`).
- SQLite persistence and historical query logging (`test_history.py`).
- Route authorization, unauthenticated redirects, and API endpoints (`test_routes.py`).
- 24-crop registry, Agricultural Assistant, Model Performance, and theme switcher (`test_ui_and_crops.py`).
- Input validation, security file checking, and image tampering verification (`test_validation.py`).

---

## 8. Team Contributions (Four-Member Distribution)
- **Member 1 (AI & Vision Specialist):** PlantVillage dataset pipeline, MobileNetV2 transfer learning, evaluation metrics.
- **Member 2 (Agronomic Decision Architect):** `crop_registry.py`, gating rules, FAO-56 irrigation rules, Agricultural Assistant.
- **Member 3 (Full-Stack Software Engineer):** Flask 3.1 blueprints, SQLite authentication schema, 3-mode theme switcher, left sidebar, report generator.
- **Member 4 (QA & Technical Mentor):** Automated pytest suite (49 tests), latency benchmarks, security testing, capstone documentation.
