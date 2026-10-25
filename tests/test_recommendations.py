"""Unit tests for the DiseaseRecommendationEngine."""

from app.services.recommendation_engine import DiseaseRecommendationEngine
from config import Config


def test_recommendation_known_disease_high_confidence():
    """Verify recommendation generation for known disease with high confidence."""
    engine = DiseaseRecommendationEngine(
        knowledge_base_path=Config.KNOWLEDGE_BASE_PATH,
        confidence_threshold=0.70,
    )

    result = engine.evaluate_recommendation(
        predicted_class="Tomato___Early_blight",
        confidence=0.88,
        declared_crop="Tomato",
    )

    assert result["is_conclusive"] is True
    assert result["crop_matched"] is True
    assert result["common_name"] == "Tomato Early Blight"
    assert len(result["observable_symptoms"]) > 0
    assert len(result["preventive_practices"]) > 0
    assert len(result["sanitation_guidance"]) > 0
    assert "Alternaria solani" in result["pathogen"]
    assert "UC IPM" in result["source_name"] or "California" in result["source_name"]


def test_recommendation_low_confidence_gating():
    """Verify that low confidence triggers inconclusive warning and withholds treatment."""
    engine = DiseaseRecommendationEngine(
        knowledge_base_path=Config.KNOWLEDGE_BASE_PATH,
        confidence_threshold=0.70,
    )

    result = engine.evaluate_recommendation(
        predicted_class="Tomato___Late_blight",
        confidence=0.52,  # Below 0.70 threshold
        declared_crop="Tomato",
    )

    assert result["is_conclusive"] is False
    assert any("RULE_LOW_CONFIDENCE" in r for r in result["rules_triggered"])
    assert any("insufficient for a reliable recommendation" in w for w in result["warnings"])


def test_recommendation_crop_mismatch_rule():
    """Verify crop mismatch rule triggers when declared crop differs from visual prediction."""
    engine = DiseaseRecommendationEngine(
        knowledge_base_path=Config.KNOWLEDGE_BASE_PATH,
        confidence_threshold=0.70,
    )

    result = engine.evaluate_recommendation(
        predicted_class="Corn_(maize)___Common_rust",
        confidence=0.92,
        declared_crop="Tomato",  # Farmer declared Tomato, but leaf is Corn
    )

    assert result["crop_matched"] is False
    assert result["is_conclusive"] is False
    assert any("RULE_CROP_MISMATCH" in r for r in result["rules_triggered"])
    assert any("Crop Mismatch Warning" in w for w in result["warnings"])


def test_recommendation_healthy_class():
    """Verify recommendation behavior on healthy class."""
    engine = DiseaseRecommendationEngine(
        knowledge_base_path=Config.KNOWLEDGE_BASE_PATH,
        confidence_threshold=0.70,
    )

    result = engine.evaluate_recommendation(
        predicted_class="Potato___healthy",
        confidence=0.95,
        declared_crop="Potato",
    )

    assert result["is_conclusive"] is True
    assert result["pathogen"] == "None detected"
    assert any("RULE_HEALTHY_STATUS" in r for r in result["rules_triggered"])


def test_recommendation_missing_knowledge_class():
    """Verify behavior when a class is not present in the knowledge database."""
    engine = DiseaseRecommendationEngine(
        knowledge_base_path=Config.KNOWLEDGE_BASE_PATH,
        confidence_threshold=0.70,
    )

    result = engine.evaluate_recommendation(
        predicted_class="UnknownCrop___Exotic_pathogen",
        confidence=0.90,
        declared_crop="UnknownCrop",
    )

    assert result["is_conclusive"] is False
    assert any("RULE_KNOWLEDGE_MISSING" in r for r in result["rules_triggered"])
