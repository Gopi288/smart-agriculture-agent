"""Unit and integration tests for UI/UX upgrades, 3-mode theme system, 24-crop registry, and dedicated views."""

import json
from pathlib import Path
from app.utils.crop_registry import (
    CROP_REGISTRY,
    get_all_crop_names,
    get_ai_supported_crop_names,
    get_crop_data,
)
from app.services.assistant_service import AgriculturalAssistant


def test_crop_registry_contains_24_crops():
    """Verify registry contains all 24 expected agronomic crops."""
    expected_crops = [
        "Tomato", "Potato", "Pepper", "Rice", "Wheat", "Corn",
        "Cotton", "Chilli", "Brinjal", "Groundnut", "Soybean", "Sugarcane",
        "Banana", "Mango", "Grapes", "Apple", "Citrus", "Cucumber",
        "Onion", "Chickpea", "Pigeon Pea", "Okra", "Mustard", "Sunflower"
    ]
    all_crops = get_all_crop_names()
    assert len(all_crops) == 24
    for exp in expected_crops:
        assert exp in all_crops, f"Crop {exp} missing from registry"


def test_crop_registry_capabilities_and_metadata():
    """Verify AI foliar model flags are strictly limited to verified classes."""
    ai_crops = get_ai_supported_crop_names()
    assert set(ai_crops) == {"Tomato", "Potato", "Corn"}

    # Non-AI crops must have irrigation and knowledge base support
    rice = get_crop_data("Rice")
    assert rice is not None
    assert rice["ai_model_supported"] is False
    assert rice["irrigation_supported"] is True
    assert rice["base_depletion_threshold"] == 50.0
    assert rice["scientific_name"] == "Oryza sativa"
    assert len(rice["common_diseases"]) > 0

    banana = get_crop_data("Banana")
    assert banana is not None
    assert banana["ai_model_supported"] is False
    assert banana["irrigation_supported"] is True
    assert "Musa" in banana["scientific_name"]


def test_crops_explorer_view(auth_client):
    """Verify /crops route renders and lists 24 crops."""
    res = auth_client.get("/crops")
    assert res.status_code == 200
    assert b"Supported Crops Explorer" in res.data
    assert b"Tomato" in res.data
    assert b"Rice" in res.data
    assert b"Wheat" in res.data
    assert b"Banana" in res.data
    assert b"24 Registered Crops" in res.data


def test_agricultural_assistant_service():
    """Verify assistant correctly retrieves agronomic and IPM guidance."""
    asst = AgriculturalAssistant()

    # FAO-56 inquiry
    kc_resp = asst.answer_query("Explain FAO-56 crop coefficient Kc")
    assert "FAO-56" in kc_resp["title"]
    assert "ETc = Kc" in kc_resp["body"]

    # Early Blight inquiry
    eb_resp = asst.answer_query("How to manage Early Blight on Tomato?")
    assert "Early Blight" in eb_resp["title"]
    assert "Alternaria solani" in eb_resp["title"]
    assert len(eb_resp["actionable_tips"]) > 0

    # Specific crop lookup
    wheat_resp = asst.answer_query("Tell me about wheat irrigation")
    assert "Wheat" in wheat_resp["title"]


def test_assistant_view_routes(auth_client):
    """Verify /assistant GET and POST queries render appropriate answers."""
    # GET view
    res_get = auth_client.get("/assistant")
    assert res_get.status_code == 200
    assert b"Agricultural Decision Assistant" in res_get.data
    assert b"Suggested Inquiries" in res_get.data

    # POST query
    res_post = auth_client.post("/assistant", data={"query": "What is Kc?"})
    assert res_post.status_code == 200
    assert b"FAO-56 Crop Coefficient" in res_post.data


def test_model_performance_view(auth_client):
    """Verify /performance loads evaluation metrics correctly."""
    res = auth_client.get("/performance")
    assert res.status_code == 200
    assert b"Model Performance" in res.data
    assert b"MobileNetV2" in res.data
    assert b"PlantVillage" in res.data
    # 85.19% overall accuracy from evaluation_metrics.json
    assert b"85.19" in res.data


def test_settings_view(auth_client):
    """Verify /settings renders system telemetry and 3-mode theme controls."""
    res = auth_client.get("/settings")
    assert res.status_code == 200
    assert b"System Settings" in res.data
    assert b"Light Mode" in res.data
    assert b"Dark Mode" in res.data
    assert b"Glassmorphism" in res.data
    assert b"Decision Parameters" in res.data


def test_navigation_sidebar_and_themes_in_base_template(auth_client):
    """Verify base template renders the left sidebar with 10 navigation views and anti-FOUC script."""
    res = auth_client.get("/")
    assert res.status_code == 200

    # Anti-FOUC script check
    assert b"localStorage.getItem(\"saa_theme\")" in res.data

    # 3-mode theme buttons check
    assert b"data-theme-val=\"light\"" in res.data
    assert b"data-theme-val=\"dark\"" in res.data
    assert b"data-theme-val=\"glass\"" in res.data

    # 10 Sidebar Navigation Items
    assert b"Dashboard" in res.data
    assert b"Crop Disease Detection" in res.data
    assert b"Irrigation Advisor" in res.data
    assert b"Agri Assistant" in res.data
    assert b"Audit History" in res.data
    assert b"Model Performance" in res.data
    assert b"Supported Crops" in res.data
    assert b"About Project" in res.data
    assert b"Settings" in res.data
    assert b"Sign Out" in res.data


def test_irrigation_engine_with_expanded_crops(app):
    """Verify IrrigationDecisionEngine functions accurately with new crops like Rice and Wheat."""
    engine = app.irrigation_engine

    # Rice assessment: Semi-aquatic crop with 50% base threshold
    rice_res = engine.assess_irrigation(
        crop="Rice",
        growth_stage="Flowering",
        soil_type="Clayey",
        soil_moisture=42.0,  # Below threshold
    )
    assert rice_res["recommendation"] == "Irrigation may be needed."
    assert rice_res["data_summary"]["crop"] == "Rice"

    # Wheat assessment: 35% threshold, soil moisture 60% (adequate)
    wheat_res = engine.assess_irrigation(
        crop="Wheat",
        growth_stage="Vegetative",
        soil_type="Loamy",
        soil_moisture=60.0,
    )
    assert wheat_res["recommendation"] == "Irrigation may not be needed yet."
