"""Agricultural Decision Support Assistant Service.

Provides responsive agronomic knowledge retrieval, Integrated Pest Management (IPM) guidance,
irrigation explanations (FAO-56), and safety advisories for farmers and students.
"""

from typing import Any, Dict, List
from app.utils.crop_registry import CROP_REGISTRY, get_crop_data


class AgriculturalAssistant:
    """Intelligent rule- and knowledge-based agricultural advisory assistant."""

    DEFAULT_PROMPTS = [
        "What is FAO-56 crop coefficient (Kc) and how does it determine water need?",
        "How can I manage Tomato Early Blight using IPM practices?",
        "What happens if soil moisture drops below 30% during the flowering stage?",
        "Why does recent heavy rainfall override irrigation recommendations?",
        "How do I prevent Potato Late Blight during humid, overcast weather?",
        "What are the optimal soil moisture ranges and root depths for Rice and Wheat?",
    ]

    def answer_query(self, query: str) -> Dict[str, Any]:
        """Process farmer query and return structured agricultural advice.

        Args:
            query: User's agronomic question.

        Returns:
            Dictionary with title, response body, referenced crops, category, and disclaimer.
        """
        q = (query or "").strip().lower()

        # 1. FAO-56 / Kc inquiry
        if any(w in q for w in ["kc", "crop coefficient", "fao-56", "fao56", "evapotranspiration", "eto"]):
            return {
                "title": "FAO-56 Crop Coefficient (Kc) & Crop Water Requirement",
                "category": "Irrigation Science",
                "body": (
                    "In the FAO-56 Penman-Monteith method, crop evapotranspiration under standard conditions (ETc) "
                    "is calculated as **ETc = Kc × ETo**, where ETo is reference grass evapotranspiration and Kc is "
                    "the crop coefficient reflecting crop canopy, height, leaf area index, and phenological stage.\n\n"
                    "- **Initial / Seedling (Kc ≈ 0.35 - 0.60):** Ground cover is low (<10%), water loss is mostly soil evaporation.\n"
                    "- **Mid-Season / Flowering / Fruiting (Kc ≈ 1.05 - 1.25):** Full vegetative canopy and peak transpiration. Water stress now causes severe yield reduction.\n"
                    "- **Late / Maturity (Kc ≈ 0.40 - 0.80):** Canopy senescence and drying prior to harvest."
                ),
                "referenced_crops": ["Maize / Corn", "Tomato", "Wheat", "Rice"],
                "actionable_tips": [
                    "Increase irrigation frequency during flowering and fruit/grain formation.",
                    "Reduce water applications approaching physiological maturity to prevent root rot and disease.",
                ]
            }

        # 2. Early Blight inquiry
        if any(w in q for w in ["early blight", "alternaria", "target spot"]):
            return {
                "title": "Integrated Management of Early Blight (Alternaria solani)",
                "category": "Plant Pathology & IPM",
                "body": (
                    "Early Blight is a destructive fungal pathogen primarily affecting tomatoes and potatoes. "
                    "It is characterized by dark brown concentric rings ('target boards') on older lower leaves, "
                    "often bordered by chlorotic yellow halos.\n\n"
                    "**Epidemiology:** Thrives in warm temperatures (24-29°C) with alternating periods of high humidity "
                    "or rain and dry weather."
                ),
                "referenced_crops": ["Tomato", "Potato"],
                "actionable_tips": [
                    "Implement a 3-year crop rotation with non-solanaceous crops (e.g. cereals, legumes).",
                    "Employ drip irrigation or soaker hoses to avoid wetting foliage.",
                    "Prune bottom 20-30 cm of foliage to improve canopy aeration and prevent soil splash.",
                    "Apply protective copper or bio-fungicide sprays early when lower leaves show first symptoms.",
                ]
            }

        # 3. Late Blight inquiry
        if any(w in q for w in ["late blight", "phytophthora", "water-soaked"]):
            return {
                "title": "Integrated Management of Late Blight (Phytophthora infestans)",
                "category": "Plant Pathology & IPM",
                "body": (
                    "Late Blight is an oomycete disease notorious for historical crop devastation (Irish Potato Famine). "
                    "It presents as rapidly expanding pale-green to dark water-soaked lesions that turn necrotic, "
                    "frequently accompanied by a delicate white mildew mold on the undersides of leaves during high relative humidity (>90%).\n\n"
                    "**Epidemiology:** Proliferates rapidly under cool, wet, foggy conditions (12-20°C)."
                ),
                "referenced_crops": ["Potato", "Tomato"],
                "actionable_tips": [
                    "Plant only certified, disease-free seed tubers.",
                    "Destroy volunteer potato plants and cull piles that act as primary overwintering sources.",
                    "Apply preventive copper-based fungicides ahead of forecasted continuous rainy periods.",
                    "Promptly eradicate heavily infected plants to protect nearby healthy blocks.",
                ]
            }

        # 4. Moisture deficit during flowering inquiry
        if any(w in q for w in ["moisture drop", "flowering", "deficit", "30%", "below 30"]):
            return {
                "title": "Critical Moisture Depletion During Flowering Stage",
                "category": "Water Balance & Agronomy",
                "body": (
                    "When soil moisture drops below 30-35% during flowering or anthesis, crops experience acute reproductive water stress. "
                    "Plants produce abscisic acid (ABA), triggering stomatal closure to limit transpiration, which spikes internal leaf temperatures "
                    "and impairs pollen viability.\n\n"
                    "**Direct Consequences:**\n"
                    "- **Tomato/Pepper:** Flower bud abortion, blossom drop, blossom-end rot (calcium deficiency).\n"
                    "- **Maize:** Silk desiccation, poor pollination, kernel abortion.\n"
                    "- **Legumes:** Pod drop and poor seed sizing."
                ),
                "referenced_crops": ["Tomato", "Corn", "Soybean", "Pepper"],
                "actionable_tips": [
                    "Initiate priority irrigation immediately to restore root-zone soil moisture to 60-70% available capacity.",
                    "Avoid midday overhead irrigation in hot weather; irrigate in early morning or evening via drip lines.",
                ]
            }

        # 5. Heavy rainfall override inquiry
        if any(w in q for w in ["rainfall", "heavy rain", "override", "rain override"]):
            return {
                "title": "Why Precipitation Records Override Sensor Depletion Rules",
                "category": "Decision Engine Logic",
                "body": (
                    "The Smart Agriculture Agent enforces a strict rainfall safety override: if cumulative rainfall in the past 24-48 hours "
                    "exceeds 15 mm (or 25 mm in 48 hours), artificial irrigation is suppressed regardless of a dry surface sensor reading.\n\n"
                    "**Agronomic Justification:**\n"
                    "- Heavy rainfall saturates the root zone and creates perched water tables.\n"
                    "- Surface capacitance sensors may temporarily read dry if percolation has moved moisture downward.\n"
                    "- Irrigating immediately on top of heavy rain causes soil anoxia (root suffocating), damping-off, Pythium root rot, and fertilizer leaching."
                ),
                "referenced_crops": ["All 24 Supported Crops"],
                "actionable_tips": [
                    "Delay irrigation until 48-72 hours post-storm and verify moisture at 15-30 cm root depth.",
                    "Inspect field drainage ditches to avoid prolonged standing water.",
                ]
            }

        # 6. Rice & Wheat inquiry
        if any(w in q for w in ["rice", "wheat", "paddy", "cereal"]):
            return {
                "title": "Irrigation and Agronomic Profiles: Rice vs. Wheat",
                "category": "Cereal Agronomy",
                "body": (
                    "- **Rice (Oryza sativa):** Semi-aquatic crop with shallow fibrous roots (30-60 cm). Optimal moisture is 70-95% saturation. "
                    "Alternate Wetting and Drying (AWD) is recommended to conserve up to 30% water while curbing methane emissions.\n"
                    "- **Wheat (Triticum aestivum):** Cool-season crop with deep roots (90-150 cm). Sensitive irrigation stages include Crown Root "
                    "Initiation (CRI, 21 DAS), tillering, flowering, and milk/dough stages. Over-watering causes lodging and stripe rust."
                ),
                "referenced_crops": ["Rice", "Wheat"],
                "actionable_tips": [
                    "Rice: Utilize field water tubes to practice safe AWD.",
                    "Wheat: Prioritize the CRI stage (20-25 days after sowing) as the single most vital irrigation.",
                ]
            }

        # 7. Check if query mentions a specific crop from the 24 registry
        for crop_name, data in CROP_REGISTRY.items():
            if crop_name.lower() in q:
                diseases = data.get("common_diseases", [])
                disease_summary = ""
                if diseases:
                    d = diseases[0]
                    disease_summary = f"**Key Pathogen:** {d['name']}\n- *Symptoms:* {d['symptoms']}\n- *IPM Control:* {d['ipm_practices']}\n\n"

                ai_status = "Supported by MobileNetV2 Neural Foliar Classifier" if data.get("ai_model_supported") else "Agronomic & FAO-56 Knowledge Base Supported (AI field model pending training)"

                return {
                    "title": f"Agronomic Profile: {crop_name} ({data.get('scientific_name')})",
                    "category": f"{data.get('category')} Crop Profile",
                    "body": (
                        f"{data.get('description')}\n\n"
                        f"- **AI Image Classification Status:** {ai_status}\n"
                        f"- **Base Moisture Stress Depletion Threshold:** {data.get('base_depletion_threshold')}%\n"
                        f"- **Optimal Soil Moisture Range:** {data.get('optimal_moisture_range')[0]}% - {data.get('optimal_moisture_range')[1]}%\n"
                        f"- **Rooting Depth Zone:** {data.get('rooting_depth_cm')}\n"
                        f"- **Preferred Soils:** {', '.join(data.get('preferred_soil', []))}\n\n"
                        f"{disease_summary}"
                    ),
                    "referenced_crops": [crop_name],
                    "actionable_tips": [
                        f"Maintain soil moisture within {data.get('optimal_moisture_range')[0]}-{data.get('optimal_moisture_range')[1]}% during critical reproductive stages.",
                        "Inspect crops weekly using a diagonal zigzag field walk pattern.",
                    ]
                }

        # General Agronomic Response
        return {
            "title": "Agronomic Guidance & Advisory",
            "category": "General Decision Support",
            "body": (
                f"Your query regarding *'{query}'* touches on core agro-ecosystem management. "
                "The Smart Agriculture Agent platform integrates machine-learning foliar disease classification "
                "with FAO-56 hydrological water balance modeling across 24 standard agricultural crops.\n\n"
                "**Key Decision Support Principles:**\n"
                "1. **Never irrigate without checking moisture data or recent rainfall.**\n"
                "2. **Look for early focal symptoms (leaf lesions, chlorosis, wilting) before pathogen establishment.**\n"
                "3. **Combine cultural, physical, biological, and chemical controls in Integrated Pest Management (IPM).**"
            ),
            "referenced_crops": ["Tomato", "Potato", "Corn", "Rice", "Wheat"],
            "actionable_tips": [
                "Select one of the suggested agronomy prompts on the left to explore specific topics.",
                "Visit the Supported Crops Explorer to review detailed profiles for all 24 supported varieties.",
            ]
        }
