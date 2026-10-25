"""Unit tests for the IrrigationDecisionEngine."""

from app.services.irrigation_engine import IrrigationDecisionEngine


def test_irrigation_insufficient_data():
    """Verify that omitting both moisture and rainfall yields Insufficient Data."""
    engine = IrrigationDecisionEngine()
    result = engine.assess_irrigation(
        crop="Tomato",
        soil_moisture=None,
        recent_rainfall=None,
    )

    assert result["recommendation"] == "Insufficient data to recommend irrigation."
    assert result["action_urgency"] == "Data Required"
    assert any("RULE_INSUFFICIENT_DATA" in r for r in result["rules_triggered"])


def test_irrigation_moisture_deficit():
    """Verify that soil moisture below threshold triggers irrigation recommendation."""
    engine = IrrigationDecisionEngine()
    result = engine.assess_irrigation(
        crop="Tomato",
        growth_stage="Flowering",
        soil_type="Sandy",
        soil_moisture=25.0,  # Below (35 + 8 + 6 = 49%)
        recent_rainfall=0.0,
    )

    assert result["recommendation"] == "Irrigation may be needed."
    assert result["action_urgency"] == "High"
    assert any("RULE_MOISTURE_DEFICIT" in r for r in result["rules_triggered"])


def test_irrigation_adequate_moisture():
    """Verify that ample soil moisture defers irrigation."""
    engine = IrrigationDecisionEngine()
    result = engine.assess_irrigation(
        crop="Corn",
        growth_stage="Vegetative",
        soil_type="Loamy",
        soil_moisture=55.0,  # Well above 30% baseline
        recent_rainfall=0.0,
    )

    assert result["recommendation"] == "Irrigation may not be needed yet."
    assert result["action_urgency"] == "Adequate Moisture"
    assert any("RULE_SUFFICIENT_MOISTURE" in r for r in result["rules_triggered"])


def test_irrigation_recent_heavy_rainfall_override():
    """Verify that recent precipitation overrides moisture deficit unless severe."""
    engine = IrrigationDecisionEngine()
    result = engine.assess_irrigation(
        crop="Potato",
        growth_stage="Fruiting",
        soil_type="Loamy",
        soil_moisture=42.0,
        recent_rainfall=25.0,  # 25 mm > 12 mm threshold
        rainfall_period_hours=24,
    )

    assert result["recommendation"] == "Irrigation may not be needed yet."
    assert result["action_urgency"] == "Defer Irrigation"
    assert any("RULE_RECENT_RAINFALL_OVERRIDE" in r for r in result["rules_triggered"])


def test_irrigation_buffer_zone_monitoring():
    """Verify that moisture in buffer zone advises reassessment and monitoring."""
    engine = IrrigationDecisionEngine()
    # Tomato baseline MAD is 35%. Moisture at 40% is within the +12% buffer zone.
    result = engine.assess_irrigation(
        crop="Tomato",
        growth_stage="Vegetative",
        soil_type="Loamy",
        soil_moisture=40.0,
        recent_rainfall=0.0,
    )

    assert result["recommendation"] == "Reassess after monitoring soil conditions."
    assert result["action_urgency"] == "Monitor Closely"
    assert any("RULE_BUFFER_ZONE" in r for r in result["rules_triggered"])
