"""Unit tests for the CropDiseaseClassifier service."""

from pathlib import Path
from app.services.disease_classifier import CropDiseaseClassifier
from app.services.image_preprocessing import preprocess_image
from config import Config


def test_image_preprocessing(valid_test_image):
    """Verify preprocessing outputs proper batch tensor shape and normalization."""
    tensor_batch, orig_size = preprocess_image(valid_test_image)
    assert tensor_batch.shape == (1, 3, 224, 224)
    assert orig_size == (224, 224)


def test_classifier_initialization():
    """Verify class indices load at init and model loads lazily on ensure_loaded()."""
    classifier = CropDiseaseClassifier(
        model_path=Config.MODEL_PATH,
        class_indices_path=Config.CLASS_INDICES_PATH,
        confidence_threshold=0.70,
    )
    # Model weights are lazy-loaded — not yet loaded at __init__ time.
    assert classifier.is_model_ready is False
    # Class indices (tiny JSON) are loaded eagerly at __init__ time.
    assert len(classifier.idx_to_class) == 8

    # After explicit ensure_loaded(), the model should be ready.
    classifier.ensure_loaded()
    assert classifier.is_model_ready is True


def test_classifier_inference_on_sample():
    """Verify real inference produces structured confidence, alternatives, and latency."""
    classifier = CropDiseaseClassifier(
        model_path=Config.MODEL_PATH,
        class_indices_path=Config.CLASS_INDICES_PATH,
        confidence_threshold=0.70,
    )

    sample_image = Config.BASE_DIR / "static" / "sample_images" / "sample_Tomato___Early_blight_1.jpg"
    if sample_image.exists():
        res = classifier.predict(sample_image)
        assert res["success"] is True
        assert res["predicted_class"] in classifier.idx_to_class.values()
        assert 0.0 <= res["confidence_score"] <= 1.0
        assert res["latency_ms"] > 0.0
        assert len(res["alternatives"]) > 0


def test_classifier_missing_model_behavior():
    """Verify graceful error reporting when model path does not exist."""
    fake_path = Path("non_existent_model.pth")
    classifier = CropDiseaseClassifier(
        model_path=fake_path,
        class_indices_path=Config.CLASS_INDICES_PATH,
    )
    assert classifier.is_model_ready is False

    res = classifier.predict(fake_path)
    assert res["success"] is False
    assert "model is not loaded" in res["error"].lower()
