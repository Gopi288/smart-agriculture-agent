"""AI Crop Disease Classifier Service for Smart Agriculture Agent.

Performs neural network inference using fine-tuned MobileNetV2 with
softmax probability calibration, multi-class ranking, latency benchmarking,
and explicit uncertainty / ambiguity gating.

Memory optimizations for Render free-tier deployment:
- Lazy model loading: the model weights are only read from disk when the
  first inference request arrives. Workers that only serve auth / irrigation
  routes never load PyTorch weights at all.
- Thread-safe initialization via threading.Lock to avoid duplicate loading
  when concurrent requests first hit an uninitialized worker.
- torch.inference_mode() instead of torch.no_grad() — skips version counter
  tracking, reducing tensor overhead during forward passes.
- Explicit CPU device forcing to avoid any accidental CUDA allocation.
"""

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn.functional as F

from app.services.image_preprocessing import preprocess_image
from ml.dataset_loader import SUPPORTED_CLASSES
from ml.train_model import build_model


class CropDiseaseClassifier:
    """Inference engine managing MobileNetV2 model loading and prediction.

    The model weights are loaded lazily on first call to predict() or
    explicit call to ensure_loaded(), not at __init__ time. This prevents
    every Gunicorn worker from consuming model memory during startup.
    """

    def __init__(
        self,
        model_path: Path,
        class_indices_path: Path,
        confidence_threshold: float = 0.70,
        uncertainty_margin: float = 0.15,
        device: Optional[str] = None,
    ):
        self.model_path = model_path
        self.class_indices_path = class_indices_path
        self.confidence_threshold = confidence_threshold
        self.uncertainty_margin = uncertainty_margin

        # Always force CPU on Render — no CUDA available on free tier.
        # Forcing CPU avoids torch trying to probe for CUDA drivers and
        # allocating CUDA context memory unnecessarily.
        if device:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cpu")

        self.idx_to_class: Dict[int, str] = {}
        self.model: Optional[torch.nn.Module] = None
        self._loaded: bool = False
        self._load_lock = threading.Lock()

        # Class indices can be loaded eagerly — they are tiny JSON files.
        self._load_class_indices()

    # ------------------------------------------------------------------
    # Class Index Loading (lightweight, always eager)
    # ------------------------------------------------------------------

    def _load_class_indices(self) -> None:
        """Load class index to human-readable label mapping."""
        if self.class_indices_path.exists():
            try:
                with open(self.class_indices_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    self.idx_to_class = {int(k): v for k, v in raw_data.items()}
            except Exception:
                self.idx_to_class = {i: c for i, c in enumerate(SUPPORTED_CLASSES)}
        else:
            self.idx_to_class = {i: c for i, c in enumerate(SUPPORTED_CLASSES)}

    # ------------------------------------------------------------------
    # Lazy Model Loading (heavy, deferred until first inference)
    # ------------------------------------------------------------------

    def _load_model(self) -> None:
        """Instantiate MobileNetV2 architecture and load trained weights.

        Must only be called while holding self._load_lock to prevent
        duplicate loading from concurrent first-requests.
        """
        num_classes = len(self.idx_to_class) if self.idx_to_class else len(SUPPORTED_CLASSES)
        model = build_model(num_classes=num_classes, freeze_backbone=False)

        if self.model_path.exists():
            try:
                # map_location=self.device ensures weights land directly on CPU
                # without any intermediate CUDA allocation.
                state_dict = torch.load(
                    str(self.model_path),
                    map_location=self.device,
                    weights_only=True,  # Security: reject pickled callables
                )
                model.load_state_dict(state_dict)
                model = model.to(self.device)
                model.eval()
                self.model = model
                print(f"[*] CropDiseaseClassifier lazy-loaded weights from {self.model_path}")
            except Exception as exc:
                print(f"[Warning] Failed loading weights from {self.model_path}: {exc}")
                self.model = None
        else:
            print(f"[Warning] Model file not found at {self.model_path}. Train model to enable inference.")
            self.model = None

        self._loaded = True

    def ensure_loaded(self) -> None:
        """Thread-safe lazy initialization of model weights.

        Calling this multiple times is safe. The model is loaded at most once.
        """
        if self._loaded:
            return
        with self._load_lock:
            # Double-checked locking: another thread may have loaded
            # while we were waiting for the lock.
            if not self._loaded:
                self._load_model()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_model_ready(self) -> bool:
        """Check whether model weights have been loaded and are ready for inference.

        Note: returns False before the first inference call because the model
        is lazy-loaded. Use ensure_loaded() to force eager loading if needed
        (e.g. after a health check warm-up request).
        """
        return self._loaded and self.model is not None

    def predict(self, image_path: Path) -> Dict[str, Any]:
        """Execute deep learning classification on an uploaded leaf photograph.

        Lazily loads the model on first call. Subsequent calls reuse the same
        model instance without any additional I/O or memory allocation.

        Args:
            image_path: Path to the validated image on disk.

        Returns:
            Dictionary with predicted class, confidence, latency, and uncertainty metrics.
        """
        # Trigger lazy load if not yet done
        self.ensure_loaded()

        if not self.is_model_ready:
            return {
                "success": False,
                "error": "Classification model is not loaded. Please train or configure weights.",
                "predicted_class": "Model_Unavailable",
                "confidence_score": 0.0,
                "confidence_pct": 0.0,
                "is_conclusive": False,
                "uncertainty_warning": "AI inference model is currently offline.",
                "alternatives": [],
                "latency_ms": 0.0,
            }

        try:
            tensor_batch, orig_dimensions = preprocess_image(image_path)
            tensor_batch = tensor_batch.to(self.device)

            t_start = time.perf_counter()
            # torch.inference_mode() is more memory-efficient than torch.no_grad():
            # it disables Autograd tracking AND version counters entirely,
            # reducing per-tensor overhead during the forward pass.
            with torch.inference_mode():
                logits = self.model(tensor_batch)
                probabilities = F.softmax(logits, dim=1).squeeze(0)
            t_end = time.perf_counter()

            latency_ms = round((t_end - t_start) * 1000.0, 2)

            # Sort probabilities descending
            top_probs, top_indices = torch.topk(probabilities, k=min(4, len(self.idx_to_class)))

            top1_prob = float(top_probs[0].item())
            top1_idx = int(top_indices[0].item())
            top1_class = self.idx_to_class.get(top1_idx, "Unknown")

            # Check alternative predictions
            alternatives: List[Dict[str, Any]] = []
            for i in range(1, len(top_probs)):
                alt_idx = int(top_indices[i].item())
                alt_prob = float(top_probs[i].item())
                alt_name = self.idx_to_class.get(alt_idx, f"Class_{alt_idx}")
                alternatives.append({
                    "class_name": alt_name,
                    "confidence_score": round(alt_prob, 4),
                    "confidence_pct": round(alt_prob * 100.0, 1),
                })

            # Uncertainty & Margin Evaluation
            is_conclusive = True
            uncertainty_warnings: List[str] = []

            # Check confidence against calibrated threshold
            if top1_prob < self.confidence_threshold:
                is_conclusive = False
                uncertainty_warnings.append(
                    f"Model confidence ({top1_prob*100:.1f}%) is below the decision threshold "
                    f"({self.confidence_threshold*100:.0f}%). Symptoms appear ambiguous."
                )

            # Check margin between top-1 and top-2 predictions
            if len(alternatives) > 0:
                top2_prob = alternatives[0]["confidence_score"]
                margin = top1_prob - top2_prob
                if margin < self.uncertainty_margin:
                    is_conclusive = False
                    uncertainty_warnings.append(
                        f"Close alternative detected ({alternatives[0]['class_name']} at {top2_prob*100:.1f}%). "
                        f"Confidence margin ({margin*100:.1f}%) is narrow; field confirmation advised."
                    )

            return {
                "success": True,
                "predicted_class": top1_class,
                "confidence_score": round(top1_prob, 4),
                "confidence_pct": round(top1_prob * 100.0, 1),
                "is_conclusive": is_conclusive,
                "uncertainty_warnings": uncertainty_warnings,
                "alternatives": alternatives,
                "latency_ms": latency_ms,
                "image_width": orig_dimensions[0],
                "image_height": orig_dimensions[1],
            }

        except Exception as exc:
            return {
                "success": False,
                "error": f"Inference pipeline failed: {str(exc)}",
                "predicted_class": "Error",
                "confidence_score": 0.0,
                "confidence_pct": 0.0,
                "is_conclusive": False,
                "uncertainty_warnings": ["Exception during image processing."],
                "alternatives": [],
                "latency_ms": 0.0,
            }
