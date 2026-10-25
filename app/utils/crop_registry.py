"""Crop Registry for Smart Agriculture Agent.

Defines the centralized catalog of 24 supported crops with botanical classifications,
AI visual foliar model compatibility flags, FAO-56 crop coefficients (Kc),
optimal volumetric soil moisture thresholds, and Integrated Pest Management (IPM) knowledge.
"""

from typing import Any, Dict, List, Optional


CROP_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Tomato": {
        "id": "tomato",
        "name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "category": "Vegetable",
        "icon": "🍅",
        "ai_model_supported": True,
        "ai_classes": [
            "Tomato___Early_blight",
            "Tomato___Late_blight",
            "Tomato___healthy",
        ],
        "irrigation_supported": True,
        "base_depletion_threshold": 35.0,
        "optimal_moisture_range": (50.0, 75.0),
        "rooting_depth_cm": "30 - 60 cm",
        "preferred_soil": ["Loamy", "Sandy Loam"],
        "fao_kc": {"seedling": 0.60, "vegetative": 0.85, "flowering": 1.15, "fruiting": 1.15, "mature": 0.80},
        "description": "High-value solanaceous fruit vegetable with high water demand during flowering and fruit sizing. Highly susceptible to foliar fungal pathogens in warm, humid weather.",
        "common_diseases": [
            {
                "name": "Early Blight (Alternaria solani)",
                "symptoms": "Concentric dark brown rings ('target spots') on older leaves, surrounded by yellow chlorotic halos.",
                "ipm_practices": "3-year solanaceous crop rotation, drip irrigation to keep foliage dry, mulching to prevent soil splashing, prompt destruction of infected residues."
            },
            {
                "name": "Late Blight (Phytophthora infestans)",
                "symptoms": "Rapidly spreading water-soaked pale-green to dark necrotic lesions on leaves and stems; white fuzzy fungal growth under high humidity.",
                "ipm_practices": "Wide plant spacing for air circulation, copper preventative sprays prior to rainfall, certified disease-free seedlings."
            }
        ]
    },
    "Potato": {
        "id": "potato",
        "name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "category": "Vegetable",
        "icon": "🥔",
        "ai_model_supported": True,
        "ai_classes": [
            "Potato___Early_blight",
            "Potato___Late_blight",
            "Potato___healthy",
        ],
        "irrigation_supported": True,
        "base_depletion_threshold": 40.0,
        "optimal_moisture_range": (60.0, 80.0),
        "rooting_depth_cm": "30 - 50 cm",
        "preferred_soil": ["Sandy Loam", "Loamy"],
        "fao_kc": {"seedling": 0.50, "vegetative": 0.75, "flowering": 1.15, "fruiting": 1.15, "mature": 0.75},
        "description": "Shallow-rooted staple tuber crop. Extremely sensitive to water deficits during tuber initiation and bulking.",
        "common_diseases": [
            {
                "name": "Late Blight (Phytophthora infestans)",
                "symptoms": "Large, irregular brown-black lesions with water-soaked margins, leaf wilting, and tuber rot.",
                "ipm_practices": "Certified seed tubers, hill soil over tubers, preventive copper fungicides, avoid overhead irrigation."
            },
            {
                "name": "Early Blight (Alternaria solani)",
                "symptoms": "Brown to black spots with concentric rings, primarily attacking senescent lower leaves.",
                "ipm_practices": "Maintain balanced nitrogen fertility, avoid moisture stress, remove crop debris after harvest."
            }
        ]
    },
    "Corn": {
        "id": "corn",
        "name": "Corn",
        "scientific_name": "Zea mays",
        "category": "Cereal",
        "icon": "🌽",
        "ai_model_supported": True,
        "ai_classes": [
            "Corn_(maize)___Common_rust_",
            "Corn_(maize)___healthy",
        ],
        "irrigation_supported": True,
        "base_depletion_threshold": 30.0,
        "optimal_moisture_range": (50.0, 70.0),
        "rooting_depth_cm": "100 - 150 cm",
        "preferred_soil": ["Loamy", "Silt Loam", "Clayey"],
        "fao_kc": {"seedling": 0.30, "vegetative": 0.70, "flowering": 1.20, "fruiting": 1.10, "mature": 0.60},
        "description": "Deep-rooted major cereal. Peak water requirement occurs during silking and tasseling; drought stress during pollination causes irreversible yield loss.",
        "common_diseases": [
            {
                "name": "Common Rust (Puccinia sorghi)",
                "symptoms": "Cinnamon-brown oval pustules on both upper and lower leaf surfaces, erupting with powdery urediniospores.",
                "ipm_practices": "Plant resistant hybrid cultivars, early planting to avoid peak spore migration, rotate with legumes."
            }
        ]
    },
    "Pepper": {
        "id": "pepper",
        "name": "Pepper",
        "scientific_name": "Capsicum annuum",
        "category": "Vegetable",
        "icon": "🫑",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 35.0,
        "optimal_moisture_range": (55.0, 75.0),
        "rooting_depth_cm": "40 - 70 cm",
        "preferred_soil": ["Sandy Loam", "Loamy"],
        "fao_kc": {"seedling": 0.60, "vegetative": 0.80, "flowering": 1.05, "fruiting": 1.05, "mature": 0.90},
        "description": "Bell pepper requires steady moisture availability; fluctuating moisture induces blossom end rot and blossom drop.",
        "common_diseases": [
            {
                "name": "Bacterial Spot (Xanthomonas campestris)",
                "symptoms": "Small, water-soaked, blistering lesions on foliage turning dark brown with chlorotic borders.",
                "ipm_practices": "Use pathogen-free seeds, avoid working in wet foliage, apply copper bactericides preventively."
            }
        ]
    },
    "Rice": {
        "id": "rice",
        "name": "Rice",
        "scientific_name": "Oryza sativa",
        "category": "Cereal",
        "icon": "🌾",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 50.0,
        "optimal_moisture_range": (70.0, 95.0),
        "rooting_depth_cm": "30 - 60 cm",
        "preferred_soil": ["Clayey", "Clay Loam"],
        "fao_kc": {"seedling": 1.10, "vegetative": 1.15, "flowering": 1.25, "fruiting": 1.15, "mature": 0.90},
        "description": "Semi-aquatic staple cereal grown in flooded lowlands or saturated soils. High water demand through tillering and panicle development.",
        "common_diseases": [
            {
                "name": "Rice Blast (Magnaporthe oryzae)",
                "symptoms": "Diamond/spindle-shaped lesions with gray-white centers and brownish margins on leaf blades and neck nodes.",
                "ipm_practices": "Balanced nitrogen management (avoid excessive urea), water management (intermittent drying), resistant varieties."
            }
        ]
    },
    "Wheat": {
        "id": "wheat",
        "name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "category": "Cereal",
        "icon": "🍞",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 35.0,
        "optimal_moisture_range": (45.0, 65.0),
        "rooting_depth_cm": "90 - 150 cm",
        "preferred_soil": ["Loamy", "Clay Loam"],
        "fao_kc": {"seedling": 0.40, "vegetative": 0.70, "flowering": 1.15, "fruiting": 0.85, "mature": 0.40},
        "description": "Temperate cool-season grain. Critical irrigation stages: Crown Root Initiation (CRI), tillering, flowering, and dough stage.",
        "common_diseases": [
            {
                "name": "Yellow/Stripe Rust (Puccinia striiformis)",
                "symptoms": "Bright yellow pustules aligned in prominent parallel stripes along leaf veins.",
                "ipm_practices": "Cultivate rust-resistant genetic stocks, monitor early rabi season cold spikes, foliar propiconazole upon threshold."
            }
        ]
    },
    "Cotton": {
        "id": "cotton",
        "name": "Cotton",
        "scientific_name": "Gossypium hirsutum",
        "category": "Cash Crop",
        "icon": "☁️",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 35.0,
        "optimal_moisture_range": (45.0, 65.0),
        "rooting_depth_cm": "100 - 170 cm",
        "preferred_soil": ["Deep Black Clay (Vertisols)", "Loamy"],
        "fao_kc": {"seedling": 0.45, "vegetative": 0.75, "flowering": 1.15, "fruiting": 1.10, "mature": 0.70},
        "description": "Deep-taprooted fiber cash crop. Peak moisture demand during flowering and boll development; waterlogging during boll burst impairs lint quality.",
        "common_diseases": [
            {
                "name": "Bacterial Blight / Angular Leaf Spot (Xanthomonas citri)",
                "symptoms": "Angular, water-soaked leaf spots bounded by veinlets, later turning reddish-brown.",
                "ipm_practices": "Acid-delinted certified seed, crop residue destruction, avoid excessive late vegetative irrigation."
            }
        ]
    },
    "Chilli": {
        "id": "chilli",
        "name": "Chilli",
        "scientific_name": "Capsicum frutescens",
        "category": "Vegetable",
        "icon": "🌶️",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 35.0,
        "optimal_moisture_range": (50.0, 70.0),
        "rooting_depth_cm": "40 - 60 cm",
        "preferred_soil": ["Sandy Loam", "Loamy"],
        "fao_kc": {"seedling": 0.60, "vegetative": 0.80, "flowering": 1.05, "fruiting": 1.05, "mature": 0.85},
        "description": "High-value spice vegetable. Susceptible to damping-off in seedling stage and leaf curl under vector pressure.",
        "common_diseases": [
            {
                "name": "Chilli Leaf Curl Virus",
                "symptoms": "Upward curling and puckering of leaves, stunted internodes, severe reduction in fruit set.",
                "ipm_practices": "Vector control (whiteflies/thrips) via yellow sticky traps and neem oil sprays; barrier crops (corn/sorghum)."
            }
        ]
    },
    "Brinjal": {
        "id": "brinjal",
        "name": "Brinjal",
        "scientific_name": "Solanum melongena",
        "category": "Vegetable",
        "icon": "🍆",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 38.0,
        "optimal_moisture_range": (55.0, 75.0),
        "rooting_depth_cm": "50 - 80 cm",
        "preferred_soil": ["Silt Loam", "Clay Loam"],
        "fao_kc": {"seedling": 0.60, "vegetative": 0.80, "flowering": 1.05, "fruiting": 1.05, "mature": 0.85},
        "description": "Eggplant/Aubergine is a warm-season solanaceous vegetable with continuous fruiting habit requiring steady root-zone moisture.",
        "common_diseases": [
            {
                "name": "Phomopsis Blight (Phomopsis vexans)",
                "symptoms": "Circular brown leaf spots with pale centers and fruit rot causing sunken soft brown lesions.",
                "ipm_practices": "Seed treatment with Trichoderma viride, destruction of infected fallen fruits, crop rotation."
            }
        ]
    },
    "Groundnut": {
        "id": "groundnut",
        "name": "Groundnut",
        "scientific_name": "Arachis hypogaea",
        "category": "Oilseed",
        "icon": "🥜",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 32.0,
        "optimal_moisture_range": (50.0, 70.0),
        "rooting_depth_cm": "50 - 100 cm",
        "preferred_soil": ["Sandy Loam", "Red Sandy Soil"],
        "fao_kc": {"seedling": 0.40, "vegetative": 0.70, "flowering": 1.15, "fruiting": 0.95, "mature": 0.60},
        "description": "Subterranean geocarpic legume. Pegging and pod development stages are most sensitive to moisture stress.",
        "common_diseases": [
            {
                "name": "Tikka Leaf Spot (Cercospora arachidicola)",
                "symptoms": "Dark brown circular spots with bright yellow halos on upper leaf surface, causing defoliation.",
                "ipm_practices": "Foliar application of Mancozeb or neem seed kernel extract, early sowing, intercropping with pearl millet."
            }
        ]
    },
    "Soybean": {
        "id": "soybean",
        "name": "Soybean",
        "scientific_name": "Glycine max",
        "category": "Oilseed",
        "icon": "🌱",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 35.0,
        "optimal_moisture_range": (50.0, 70.0),
        "rooting_depth_cm": "60 - 130 cm",
        "preferred_soil": ["Loamy", "Clay Loam"],
        "fao_kc": {"seedling": 0.40, "vegetative": 0.70, "flowering": 1.15, "fruiting": 1.05, "mature": 0.50},
        "description": "Major protein and oilseed legume. Requires adequate moisture during flowering (R1-R2) and pod filling (R5-R6).",
        "common_diseases": [
            {
                "name": "Soybean Rust (Phakopsora pachyrhizi)",
                "symptoms": "Small polygonal tan to dark reddish brown lesions on lower leaf surfaces.",
                "ipm_practices": "Early detection, use of tolerant varieties, foliar strobilurin/triazole fungicide prior to canopy closure."
            }
        ]
    },
    "Sugarcane": {
        "id": "sugarcane",
        "name": "Sugarcane",
        "scientific_name": "Saccharum officinarum",
        "category": "Cash Crop",
        "icon": "🎋",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 45.0,
        "optimal_moisture_range": (60.0, 85.0),
        "rooting_depth_cm": "120 - 200 cm",
        "preferred_soil": ["Deep Loam", "Clayey"],
        "fao_kc": {"seedling": 0.40, "vegetative": 0.85, "flowering": 1.25, "fruiting": 1.25, "mature": 0.75},
        "description": "Perennial C4 grass with extensive biomass and high overall transpiration demand over a 10-18 month cropping cycle.",
        "common_diseases": [
            {
                "name": "Red Rot (Colletotrichum falcatum)",
                "symptoms": "Yellowing and withering of leaves; internal stem tissues show reddening with distinct white cross-patches.",
                "ipm_practices": "Sett treatment with carbendazim or hot water at 52°C, crop rotation, rouging diseased clumps."
            }
        ]
    },
    "Banana": {
        "id": "banana",
        "name": "Banana",
        "scientific_name": "Musa acuminata",
        "category": "Fruit",
        "icon": "🍌",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 45.0,
        "optimal_moisture_range": (65.0, 85.0),
        "rooting_depth_cm": "40 - 80 cm",
        "preferred_soil": ["Deep Rich Loamy", "Alluvial"],
        "fao_kc": {"seedling": 1.00, "vegetative": 1.10, "flowering": 1.20, "fruiting": 1.20, "mature": 1.10},
        "description": "Large herbaceous perennial with rapid leaf turnover. High transpiration rate and shallow root zone require frequent irrigation.",
        "common_diseases": [
            {
                "name": "Sigatoka Leaf Spot (Pseudocercospora fijiensis)",
                "symptoms": "Small yellowish chlorotic streaks running parallel to leaf veins, coalescing into necrotic brown streaks.",
                "ipm_practices": "De-leafing infected leaves to reduce inoculum, mineral oil and systemic fungicide rotation, optimal spacing."
            }
        ]
    },
    "Mango": {
        "id": "mango",
        "name": "Mango",
        "scientific_name": "Mangifera indica",
        "category": "Fruit",
        "icon": "🥭",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 30.0,
        "optimal_moisture_range": (45.0, 65.0),
        "rooting_depth_cm": "150 - 250 cm",
        "preferred_soil": ["Deep Well-drained Loamy"],
        "fao_kc": {"seedling": 0.60, "vegetative": 0.70, "flowering": 0.80, "fruiting": 0.80, "mature": 0.70},
        "description": "Deep-rooted perennial fruit orchard. Water withholding prior to flowering stimulates flower bud differentiation.",
        "common_diseases": [
            {
                "name": "Anthracnose (Colletotrichum gloeosporioides)",
                "symptoms": "Irregular dark brown necrotic spots on leaves, blossoms, and black tear-staining lesions on developing fruits.",
                "ipm_practices": "Prune dead twigs, post-harvest hot water fruit treatment (52°C for 5 min), copper oxychloride sprays."
            }
        ]
    },
    "Grapes": {
        "id": "grapes",
        "name": "Grapes",
        "scientific_name": "Vitis vinifera",
        "category": "Fruit",
        "icon": "🍇",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 32.0,
        "optimal_moisture_range": (45.0, 65.0),
        "rooting_depth_cm": "100 - 200 cm",
        "preferred_soil": ["Gravelly Loam", "Sandy Loam"],
        "fao_kc": {"seedling": 0.30, "vegetative": 0.55, "flowering": 0.70, "fruiting": 0.65, "mature": 0.45},
        "description": "Deciduous perennial vine grown on trellises. Regulated Deficit Irrigation (RDI) is widely practiced to optimize berry brix and quality.",
        "common_diseases": [
            {
                "name": "Downy Mildew (Plasmopara viticola)",
                "symptoms": "Yellowish oily 'oil spots' on upper leaf surface with delicate downy white mold on the underside.",
                "ipm_practices": "Canopy canopy management to enhance sunlight penetration, preventive copper sprays, bio-fungicides."
            }
        ]
    },
    "Apple": {
        "id": "apple",
        "name": "Apple",
        "scientific_name": "Malus domestica",
        "category": "Fruit",
        "icon": "🍎",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 35.0,
        "optimal_moisture_range": (50.0, 70.0),
        "rooting_depth_cm": "100 - 180 cm",
        "preferred_soil": ["Well-drained Loam", "Clay Loam"],
        "fao_kc": {"seedling": 0.50, "vegetative": 0.70, "flowering": 0.95, "fruiting": 0.95, "mature": 0.70},
        "description": "Temperate deciduous pome fruit tree. Water stress during cell division (fruitlet stage) permanently curtails final fruit size.",
        "common_diseases": [
            {
                "name": "Apple Scab (Venturia inaequalis)",
                "symptoms": "Velvety olive-green to black circular lesions on leaves and scabby corky spots on fruit surfaces.",
                "ipm_practices": "Shred fallen overwintering leaves, apply urea 5% at leaf fall, predictive Mills infection period sprays."
            }
        ]
    },
    "Citrus": {
        "id": "citrus",
        "name": "Citrus",
        "scientific_name": "Citrus sinensis",
        "category": "Fruit",
        "icon": "🍊",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 35.0,
        "optimal_moisture_range": (50.0, 70.0),
        "rooting_depth_cm": "80 - 150 cm",
        "preferred_soil": ["Well-drained Sandy Loam"],
        "fao_kc": {"seedling": 0.70, "vegetative": 0.70, "flowering": 0.65, "fruiting": 0.70, "mature": 0.70},
        "description": "Evergreen subtropical/tropical orchard tree. Moisture stress induces root flushes and flowering but fruit drop occurs if deficit is prolonged.",
        "common_diseases": [
            {
                "name": "Citrus Canker (Xanthomonas axonopodis)",
                "symptoms": "Raised corky lesions on leaves, stems, and fruit surrounded by distinctive oily yellow halos.",
                "ipm_practices": "Windbreak establishment, copper bactericide sprays, leafminer control to avoid entry wounds."
            }
        ]
    },
    "Cucumber": {
        "id": "cucumber",
        "name": "Cucumber",
        "scientific_name": "Cucumis sativus",
        "category": "Vegetable",
        "icon": "🥒",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 40.0,
        "optimal_moisture_range": (60.0, 80.0),
        "rooting_depth_cm": "30 - 60 cm",
        "preferred_soil": ["Sandy Loam", "Rich Loam"],
        "fao_kc": {"seedling": 0.60, "vegetative": 0.75, "flowering": 1.00, "fruiting": 1.00, "mature": 0.75},
        "description": "Fast-growing vine with succulent stems and 95% fruit water content. Shallow roots require frequent, light watering.",
        "common_diseases": [
            {
                "name": "Powdery Mildew (Podosphaera xanthii)",
                "symptoms": "White talcum-powder-like spots on upper and lower surfaces of leaves and petioles.",
                "ipm_practices": "Trellising to keep vines off wet soil, sulfur dusts, potassium bicarbonate sprays."
            }
        ]
    },
    "Onion": {
        "id": "onion",
        "name": "Onion",
        "scientific_name": "Allium cepa",
        "category": "Vegetable",
        "icon": "🧅",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 42.0,
        "optimal_moisture_range": (60.0, 80.0),
        "rooting_depth_cm": "25 - 40 cm",
        "preferred_soil": ["Light Loam", "Sandy Loam"],
        "fao_kc": {"seedling": 0.70, "vegetative": 0.85, "flowering": 1.05, "fruiting": 1.05, "mature": 0.75},
        "description": "Extremely shallow, fibrous root system. Moisture stress during bulb enlargement reduces size and causes splitting.",
        "common_diseases": [
            {
                "name": "Purple Blotch (Alternaria porri)",
                "symptoms": "Water-soaked lesions on leaves turning brown-purple with concentric rings.",
                "ipm_practices": "Well-drained raised beds, avoid dense planting, prophylactic sprays of Mancozeb."
            }
        ]
    },
    "Chickpea": {
        "id": "chickpea",
        "name": "Chickpea",
        "scientific_name": "Cicer arietinum",
        "category": "Pulse",
        "icon": "🫘",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 28.0,
        "optimal_moisture_range": (40.0, 60.0),
        "rooting_depth_cm": "60 - 120 cm",
        "preferred_soil": ["Deep Loam", "Black Soil"],
        "fao_kc": {"seedling": 0.40, "vegetative": 0.65, "flowering": 1.00, "fruiting": 0.80, "mature": 0.35},
        "description": "Drought-hardy rabi pulse. Deep taproots extract subsoil moisture efficiently; excessive irrigation causes collar rot and excessive vegetative growth.",
        "common_diseases": [
            {
                "name": "Ascochyta Blight (Ascochyta rabiei)",
                "symptoms": "Circular spots on leaflets and elongated sunken cankers on stems with dark concentric pycnidia rings.",
                "ipm_practices": "Deep summer plowing, seed treatment with carbendazim, resistant cultivars."
            }
        ]
    },
    "Pigeon Pea": {
        "id": "pigeon_pea",
        "name": "Pigeon Pea",
        "scientific_name": "Cajanus cajan",
        "category": "Pulse",
        "icon": "🌿",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 28.0,
        "optimal_moisture_range": (40.0, 60.0),
        "rooting_depth_cm": "120 - 200 cm",
        "preferred_soil": ["Loamy", "Deep Clay"],
        "fao_kc": {"seedling": 0.35, "vegetative": 0.60, "flowering": 1.00, "fruiting": 0.85, "mature": 0.40},
        "description": "Deep-rooting woody legume (Arhar/Tur). Outstanding drought resilience; benefits from protective irrigation only during pod development.",
        "common_diseases": [
            {
                "name": "Fusarium Wilt (Fusarium udum)",
                "symptoms": "Gradual wilting, purple bands on lower stem, xylem vessel browning inside root tissues.",
                "ipm_practices": "Long crop rotations (3-4 years) with sorghum, bio-agent Trichoderma soil application."
            }
        ]
    },
    "Okra": {
        "id": "okra",
        "name": "Okra",
        "scientific_name": "Abelmoschus esculentus",
        "category": "Vegetable",
        "icon": "🌱",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 35.0,
        "optimal_moisture_range": (50.0, 75.0),
        "rooting_depth_cm": "50 - 90 cm",
        "preferred_soil": ["Friable Loam", "Sandy Loam"],
        "fao_kc": {"seedling": 0.50, "vegetative": 0.75, "flowering": 1.00, "fruiting": 1.00, "mature": 0.80},
        "description": "Warm-season mallow family vegetable (Bhindi). Needs regular watering during continuous pod picking cycles.",
        "common_diseases": [
            {
                "name": "Yellow Vein Mosaic Virus (YVMV)",
                "symptoms": "Homogeneous yellow network of veins against green leaf blade, stunted growth, pale fibrous pods.",
                "ipm_practices": "Whitefly vector suppression via yellow sticky traps and imidacloprid / neem oil, resistant hybrids."
            }
        ]
    },
    "Mustard": {
        "id": "mustard",
        "name": "Mustard",
        "scientific_name": "Brassica juncea",
        "category": "Oilseed",
        "icon": "🌼",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 30.0,
        "optimal_moisture_range": (45.0, 65.0),
        "rooting_depth_cm": "60 - 120 cm",
        "preferred_soil": ["Light Loam", "Sandy Loam"],
        "fao_kc": {"seedling": 0.35, "vegetative": 0.65, "flowering": 1.05, "fruiting": 0.85, "mature": 0.35},
        "description": "Winter season brassica oilseed crop. Two critical irrigation windows: rosette stage (30 DAS) and siliquae formation (60 DAS).",
        "common_diseases": [
            {
                "name": "White Rust (Albugo candida)",
                "symptoms": "Prominent chalky white raised blisters (pustules) on lower leaf surface; staghead floral deformities.",
                "ipm_practices": "Early sowing before mid-October, seed treatment with metalaxyl, destruction of cruciferous weeds."
            }
        ]
    },
    "Sunflower": {
        "id": "sunflower",
        "name": "Sunflower",
        "scientific_name": "Helianthus annuus",
        "category": "Oilseed",
        "icon": "🌻",
        "ai_model_supported": False,
        "ai_classes": [],
        "irrigation_supported": True,
        "base_depletion_threshold": 32.0,
        "optimal_moisture_range": (50.0, 70.0),
        "rooting_depth_cm": "90 - 160 cm",
        "preferred_soil": ["Deep Sandy Loam", "Clay Loam"],
        "fao_kc": {"seedling": 0.35, "vegetative": 0.75, "flowering": 1.15, "fruiting": 0.90, "mature": 0.40},
        "description": "Heliotropic composite oilseed with extensive rooting system. Peak water sensitivity occurs during bud opening and achene filling.",
        "common_diseases": [
            {
                "name": "Alternaria Leaf Blight (Alternaria helianthi)",
                "symptoms": "Dark brown circular spots with target-board rings on leaves, capitulum rot under high humidity.",
                "ipm_practices": "Crop rotation, seed dressing with carbendazim, prophylactic foliar Mancozeb spray at star-bud stage."
            }
        ]
    },
}


def get_all_crop_names() -> List[str]:
    """Retrieve full list of 24 crop display names."""
    return list(CROP_REGISTRY.keys())


def get_ai_supported_crop_names() -> List[str]:
    """Retrieve list of crops with neural image classification support."""
    return [name for name, data in CROP_REGISTRY.items() if data.get("ai_model_supported")]


def get_crop_data(crop_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve structured metadata for a crop by name (case-insensitive)."""
    if not crop_name:
        return None
    c_lower = crop_name.strip().lower()
    for name, data in CROP_REGISTRY.items():
        if name.lower() == c_lower or data.get("id", "").lower() == c_lower:
            return data
    return None
