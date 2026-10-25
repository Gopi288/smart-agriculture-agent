"""AI Crop Disease Classifier Service for Smart Agriculture Agent.

Performs neural network inference using fine-tuned MobileNetV2 with
softmax probability calibration, multi-class ranking, latency benchmarking,
and explicit uncertainty / ambiguity gating.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import torch
import torch.nn.functional as F

from app.services.image_preprocessing import preprocess_image
from ml.dataset_loader import SUPPORTED_CLASSES
from ml.train_model import build_model


class CropDiseaseClassifier:
    """Inference engine managing MobileNetV2 model loading and prediction."""

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

        if device:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.idx_to_class: Dict[int, str] = {}
        self.model: Optional[torch.nn.Module] = None
        self._load_class_indices()
        self._load_model()

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

    def _load_model(self) -> None:
        """Instantiate MobileNetV2 architecture and load trained weights."""
        num_classes = len(self.idx_to_class) if self.idx_to_class else len(SUPPORTED_CLASSES)
        self.model = build_model(num_classes=num_classes, freeze_backbone=False)

        if self.model_path.exists():
            try:
                state_dict = torch.load(str(self.model_path), map_location=self.device)
                self.model.load_state_dict(state_dict)
                self.model = self.model.to(self.device)
                self.model.eval()
                print(f"[*] CropDiseaseClassifier loaded weights from {self.model_path}")
            except Exception as exc:
                print(f"[Warning] Failed loading weights from {self.model_path}: {exc}")
                self.model = None
        else:
            print(f"[Warning] Model file not found at {self.model_path}. Train model to enable inference.")
            self.model = None

    @property
    def is_model_ready(self) -> bool:
        """Check whether the model weights are loaded and ready for inference."""
        return self.model is not None

    def predict(self, image_path: Path) -> Dict[str, Any]:
        """Execute deep learning classification on an uploaded leaf photograph.

        Args:
            image_path: Path to the validated image on disk.

        Returns:
            Dictionary with predicted class, confidence, latency, and uncertainty metrics.
        """
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
            with torch.no_grad():
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
