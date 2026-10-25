"""Unit tests for SQLite database persistence and querying."""

from app.models.database import (
    get_disease_analyses,
    get_disease_analysis_by_id,
    get_irrigation_assessments,
    get_system_counts,
    init_db,
    save_disease_analysis,
    save_irrigation_assessment,
)


def test_database_crud(test_dirs):
    """Verify end-to-end database initialization, insertion, and retrieval."""
    db_file = test_dirs / "crud_test.db"
    init_db(db_file)

    # 1. Insert Disease Analysis
    record_id = save_disease_analysis(
        db_path=db_file,
        crop_declared="Tomato",
        predicted_class="Tomato___Early_blight",
        disease_name="Tomato Early Blight",
        confidence_score=0.88,
        is_conclusive=True,
        crop_matched=True,
        top_alternatives_json='[{"class_name": "Tomato___Late_blight", "confidence_pct": 8.5}]',
        symptoms="Target board concentric rings",
        management_guidance="Prune lower leaves",
        recommendation_source="UC IPM",
        warning_message="",
        image_filename="test_leaf.jpg",
    )
    assert record_id > 0

    # 2. Retrieve Disease Analysis by ID
    rec = get_disease_analysis_by_id(db_file, record_id)
    assert rec is not None
    assert rec["crop_declared"] == "Tomato"
    assert rec["confidence_score"] == 0.88
    assert rec["is_conclusive"] == 1

    # 3. Insert Irrigation Assessment
    irr_id = save_irrigation_assessment(
        db_path=db_file,
        crop="Potato",
        growth_stage="Fruiting",
        soil_type="Clayey",
        soil_moisture=26.5,
        soil_moisture_source="Sensor",
        recent_rainfall=0.0,
        rainfall_period_hours=24,
        rainfall_source="Manual",
        temperature_c=28.0,
        humidity_pct=65.0,
        weather_source="OpenWeather",
        recommendation="Irrigation may be needed.",
        action_urgency="High",
        rationale="Moisture below depletion point",
        missing_data_notes="",
    )
    assert irr_id > 0

    # 4. Verify system counts
    counts = get_system_counts(db_file)
    assert counts["disease_analyses_count"] == 1
    assert counts["irrigation_assessments_count"] == 1

    # 5. Verify querying with crop filter
    tomato_recs = get_disease_analyses(db_file, crop_filter="Tomato")
    assert len(tomato_recs) == 1
    potato_recs = get_disease_analyses(db_file, crop_filter="Potato")
    assert len(potato_recs) == 0
