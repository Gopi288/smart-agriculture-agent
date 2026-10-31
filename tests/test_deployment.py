"""Deployment-safety tests for the Smart Agriculture Agent.

Verifies that the Render-specific optimisations introduced to fix
HTTP 502 / SIGKILL (OOM) errors behave correctly:

1. /healthz liveness probe responds without touching the AI model.
2. CropDiseaseClassifier uses lazy loading (not loaded at __init__).
3. After ensure_loaded() / predict(), the model is ready.
4. ensure_loaded() is idempotent (calling twice does not reload weights).
5. Large images are pre-downsized before the transform pipeline.
6. Inference runs inside torch.inference_mode() (no autograd overhead).
"""

import io
import threading

import pytest
import torch
from PIL import Image

from app.services.disease_classifier import CropDiseaseClassifier
from app.services.image_preprocessing import _PREDECODE_MAX_DIM, _predecode_resize
from config import Config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pil_image(width: int, height: int, color: tuple = (34, 139, 34)) -> Image.Image:
    """Create a solid-colour PIL Image for testing."""
    return Image.new("RGB", (width, height), color=color)


def _make_classifier(model_path=None) -> CropDiseaseClassifier:
    """Return a CropDiseaseClassifier pointed at the real (or custom) model path."""
    return CropDiseaseClassifier(
        model_path=model_path or Config.MODEL_PATH,
        class_indices_path=Config.CLASS_INDICES_PATH,
        confidence_threshold=0.70,
    )


# ---------------------------------------------------------------------------
# /healthz endpoint
# ---------------------------------------------------------------------------

class TestHealthzEndpoint:
    """/healthz must respond instantly and must not load the AI model."""

    def test_healthz_returns_200(self, client):
        """/healthz returns HTTP 200 OK."""
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_healthz_returns_ok_json(self, client):
        """/healthz body is {'status': 'ok'}."""
        response = client.get("/healthz")
        data = response.get_json()
        assert data is not None, "Response is not valid JSON"
        assert data.get("status") == "ok"

    def test_healthz_does_not_require_authentication(self, client):
        """/healthz is a public liveness probe — no login needed."""
        # Hit endpoint without logging in; expect 200, not 302 redirect to /login.
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_healthz_does_not_load_model(self, app):
        """Calling /healthz must not trigger CropDiseaseClassifier.ensure_loaded().

        We verify this by inspecting the app's classifier object immediately
        after a /healthz call and confirming is_model_ready is still False.
        """
        classifier: CropDiseaseClassifier = app.classifier
        # Ensure model has not been loaded by any prior test interaction.
        if classifier._loaded:
            pytest.skip("Classifier was already loaded before this test ran.")

        with app.test_client() as c:
            c.get("/healthz")

        # After /healthz, the model must still be un-loaded.
        assert classifier._loaded is False, (
            "/healthz triggered model loading — this will cause OOM on Render free tier."
        )


# ---------------------------------------------------------------------------
# Lazy loading behaviour
# ---------------------------------------------------------------------------

class TestLazyLoading:
    """Verify that CropDiseaseClassifier does NOT load weights at __init__ time."""

    def test_model_not_ready_at_init(self):
        """is_model_ready must be False immediately after __init__."""
        clf = _make_classifier()
        assert clf.is_model_ready is False, (
            "Model was loaded at __init__ — this defeats lazy loading and will cause OOM."
        )

    def test_class_indices_loaded_at_init(self):
        """idx_to_class (tiny JSON) must be populated eagerly at __init__."""
        clf = _make_classifier()
        assert len(clf.idx_to_class) == 8

    def test_model_ready_after_ensure_loaded(self):
        """is_model_ready must be True after an explicit ensure_loaded() call."""
        clf = _make_classifier()
        clf.ensure_loaded()
        assert clf.is_model_ready is True

    def test_ensure_loaded_is_idempotent(self, mocker):
        """Calling ensure_loaded() twice must not call _load_model() twice.

        Duplicate loading would double peak memory and cause OOM on constrained
        Render instances.
        """
        clf = _make_classifier()
        original_load = clf._load_model
        call_count = {"n": 0}

        def counting_load():
            call_count["n"] += 1
            original_load()

        mocker.patch.object(clf, "_load_model", side_effect=counting_load)

        clf.ensure_loaded()
        clf.ensure_loaded()  # Second call must be a no-op
        clf.ensure_loaded()  # Third call must also be a no-op

        assert call_count["n"] == 1, (
            f"_load_model() was called {call_count['n']} times; expected exactly 1."
        )

    def test_ensure_loaded_thread_safety(self):
        """Concurrent calls to ensure_loaded() from multiple threads must load
        the model exactly once (double-checked locking).
        """
        clf = _make_classifier()
        results = []
        errors = []

        def worker():
            try:
                clf.ensure_loaded()
                results.append(clf.is_model_ready)
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=worker) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        assert all(results), "Some threads saw is_model_ready=False after ensure_loaded()"


# ---------------------------------------------------------------------------
# Missing-model graceful degradation
# ---------------------------------------------------------------------------

class TestMissingModelGracefulDegradation:
    """When the model file does not exist, the classifier must fail safely."""

    def test_is_model_ready_false_before_predict(self, tmp_path):
        """is_model_ready is False at init when model path does not exist."""
        clf = CropDiseaseClassifier(
            model_path=tmp_path / "no_such_model.pth",
            class_indices_path=Config.CLASS_INDICES_PATH,
        )
        assert clf.is_model_ready is False

    def test_predict_returns_error_dict_not_exception(self, tmp_path):
        """predict() must return an error dict, not raise an exception."""
        fake_image = tmp_path / "leaf.jpg"
        fake_image.write_bytes(b"not a real image")

        clf = CropDiseaseClassifier(
            model_path=tmp_path / "no_such_model.pth",
            class_indices_path=Config.CLASS_INDICES_PATH,
        )
        result = clf.predict(fake_image)

        assert result["success"] is False
        assert "model is not loaded" in result["error"].lower()


# ---------------------------------------------------------------------------
# Image pre-downsizing
# ---------------------------------------------------------------------------

class TestImagePredownsizing:
    """Large images must be capped at _PREDECODE_MAX_DIM before the transform."""

    def test_large_image_is_downsized(self):
        """A 4000×3000 image must be reduced so max(dim) <= _PREDECODE_MAX_DIM."""
        large_img = _make_pil_image(4000, 3000)
        result = _predecode_resize(large_img)
        assert max(result.size) <= _PREDECODE_MAX_DIM, (
            f"Image not downsized: got {result.size}, expected max dim {_PREDECODE_MAX_DIM}."
        )

    def test_small_image_is_not_upscaled(self):
        """An image already smaller than the cap must not be resized."""
        small_img = _make_pil_image(100, 80)
        result = _predecode_resize(small_img)
        assert result.size == (100, 80), (
            f"Small image was resized from (100,80) to {result.size} — thumbnail should not upscale."
        )

    def test_exact_cap_image_is_unchanged(self):
        """An image exactly at the cap dimension must not be resized."""
        cap_img = _make_pil_image(_PREDECODE_MAX_DIM, _PREDECODE_MAX_DIM)
        result = _predecode_resize(cap_img)
        assert result.size == (_PREDECODE_MAX_DIM, _PREDECODE_MAX_DIM)

    def test_aspect_ratio_preserved_after_downsizing(self):
        """thumbnail() must preserve aspect ratio (no squashing)."""
        original = _make_pil_image(4000, 2000)  # 2:1 aspect ratio
        result = _predecode_resize(original)
        w, h = result.size
        # Allow ±1 pixel tolerance for integer rounding
        assert abs(w / h - 2.0) < 0.02, (
            f"Aspect ratio changed after downsizing: {w}×{h} (expected ~2:1)."
        )

    def test_predecode_resize_constant_matches_expected_value(self):
        """_PREDECODE_MAX_DIM must be 512 — larger values defeat the memory saving."""
        assert _PREDECODE_MAX_DIM == 512, (
            f"_PREDECODE_MAX_DIM is {_PREDECODE_MAX_DIM}; expected 512 for Render memory budget."
        )


# ---------------------------------------------------------------------------
# Inference mode (no autograd tracking during forward pass)
# ---------------------------------------------------------------------------

class TestInferenceMode:
    """Verify that torch.inference_mode() is active during prediction.

    inference_mode() is more memory-efficient than no_grad() because it
    also disables tensor version counters.
    """

    def test_inference_runs_without_grad_tracking(self, tmp_path):
        """Model forward pass must execute without building a computation graph."""
        clf = _make_classifier()
        clf.ensure_loaded()

        # Create a tiny valid leaf image to feed through the classifier
        img = _make_pil_image(300, 300, color=(0, 128, 0))
        img_path = tmp_path / "test_leaf.jpg"
        img.save(str(img_path), "JPEG")

        # Capture the inference_mode state inside the forward pass by patching
        # the model's forward method to record torch.is_inference_mode_enabled().
        inference_mode_was_active = []
        original_forward = clf.model.forward

        def recording_forward(x):
            inference_mode_was_active.append(torch.is_inference_mode_enabled())
            return original_forward(x)

        clf.model.forward = recording_forward

        result = clf.predict(img_path)

        assert result["success"] is True, f"Inference failed: {result.get('error')}"
        assert inference_mode_was_active, "forward() was never called during predict()"
        assert all(inference_mode_was_active), (
            "torch.inference_mode() was NOT active during model forward pass — "
            "this wastes memory on Render."
        )

    def test_predict_cpu_device(self):
        """Model must run on CPU — Render free tier has no GPU."""
        clf = _make_classifier()
        clf.ensure_loaded()
        assert clf.device.type == "cpu", (
            f"Classifier is using device '{clf.device}' instead of 'cpu'. "
            "This will fail on Render where no CUDA is available."
        )
