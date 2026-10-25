"""Rule-based disease recommendation engine for Smart Agriculture Agent.

Decouples deep-learning model inference from agronomic decision support.
Applies transparent gating rules for confidence thresholds, crop mismatch detection,
uncertainty handling, and evidence-based IPM advice retrieval.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class DiseaseRecommendationEngine:
    """Agronomic rule engine for disease management decision support."""

    def __init__(self, knowledge_base_path: Path, confidence_threshold: float = 0.70):
        self.knowledge_base_path = knowledge_base_path
        self.confidence_threshold = confidence_threshold
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load structured disease knowledge base from JSON."""
        if not self.knowledge_base_path.exists():
            return {}
        try:
            with open(self.knowledge_base_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("classes", {})
        except Exception:
            return {}

    def evaluate_recommendation(
        self,
        predicted_class: str,
        confidence: float,
        declared_crop: str,
        top_predictions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Evaluate disease classification against agronomic rules.

        Rules applied:
        1. Low Confidence Gating: If confidence < threshold, withhold specific disease
           prescriptions; flag inconclusive and advise physical inspection.
        2. Crop Consistency Rule: Check if predicted crop matches declared crop. If not,
           flag mismatch warning and advise verified crop re-check.
        3. Knowledge Base Presence: Verify whether the class exists in the verified database.
        4. Healthy Status Rule: If predicted healthy, offer preventive baseline guidance.
        5. Pathogen Advisory Rule: If diseased and confident, provide non-chemical IPM,
           sanitation, observable symptoms, and extension contact recommendations.

        Args:
            predicted_class: Class string from classifier (e.g., 'Tomato___Early_blight').
            confidence: Top prediction confidence score (0.0 to 1.0).
            declared_crop: Farmer-selected crop (e.g., 'Tomato').
            top_predictions: Optional list of alternative classes and scores.

        Returns:
            Dictionary containing recommendation details, trigger rules, and warnings.
        """
        confidence_pct = round(confidence * 100.0, 1)
        rules_triggered: List[str] = []
        is_conclusive = True
        crop_matched = True
        warnings: List[str] = []

        # Extract predicted crop from class name (e.g. 'Tomato' from 'Tomato___Early_blight')
        predicted_crop = predicted_class.split("___")[0].replace("Corn_(maize)", "Corn").strip()

        # Rule 1: Confidence Gating
        if confidence < self.confidence_threshold:
            is_conclusive = False
            rules_triggered.append(
                f"RULE_LOW_CONFIDENCE: Model confidence ({confidence_pct}%) is below the validated "
                f"decision threshold ({self.confidence_threshold * 100:.0f}%). Specific disease management guidance "
                f"is withheld to prevent misapplication."
            )
            warnings.append(
                f"Confidence ({confidence_pct}%) is insufficient for a reliable recommendation. "
                "Visual symptoms are ambiguous. Please capture a clearer, well-lit, close-up photograph "
                "of an individual leaf, or consult a local agricultural extension specialist."
            )

        # Rule 2: Crop Consistency Verification
        if declared_crop and declared_crop.lower() != predicted_crop.lower():
            crop_matched = False
            rules_triggered.append(
                f"RULE_CROP_MISMATCH: Declared crop '{declared_crop}' does not match model-predicted "
                f"crop '{predicted_crop}' from image features."
            )
            warnings.append(
                f"Crop Mismatch Warning: You selected '{declared_crop}', but visual analysis indicates foliage "
                f"characteristic of '{predicted_crop}'. Recommendations are deferred until the crop is verified."
            )

        # Retrieve knowledge entry
        knowledge_entry = self.knowledge_base.get(predicted_class)

        # Rule 3: Knowledge Base Availability
        if not knowledge_entry:
            rules_triggered.append(
                f"RULE_KNOWLEDGE_MISSING: Class '{predicted_class}' lacks an authoritative entry "
                f"in the verified knowledge base."
            )
            return {
                "is_conclusive": False,
                "crop_matched": crop_matched,
                "predicted_class": predicted_class,
                "confidence_pct": confidence_pct,
                "common_name": "Unverified Class",
                "pathogen": "Unknown",
                "description": "Authoritative agronomic guidance is not currently available for this detected class.",
                "observable_symptoms": [],
                "preventive_practices": ["Consult local agricultural authorities."],
                "sanitation_guidance": [],
                "crop_management_advice": "No specific guidance available.",
                "recommended_next_step": "Submit a physical sample to a certified plant diagnostic laboratory.",
                "source_name": "N/A",
                "source_url": "",
                "date_reviewed": "",
                "important_limitations": "Unverified entry in database.",
                "rules_triggered": rules_triggered,
                "warnings": warnings,
            }

        # Rule 4 & 5: Conclusive vs Inconclusive Result Assembly
        if not is_conclusive or not crop_matched:
            # Provide general caution rather than full disease-specific treatment
            return {
                "is_conclusive": False,
                "crop_matched": crop_matched,
                "predicted_class": predicted_class,
                "confidence_pct": confidence_pct,
                "common_name": knowledge_entry.get("common_name", predicted_class),
                "pathogen": knowledge_entry.get("pathogen", "N/A"),
                "description": (
                    f"Possible tentative indication: {knowledge_entry.get('common_name', predicted_class)}. "
                    "However, because decision criteria were not met, treat this as unconfirmed preliminary decision support."
                ),
                "observable_symptoms": knowledge_entry.get("observable_symptoms", []),
                "preventive_practices": [
                    "Perform routine field inspection to assess broader canopy health.",
                    "Ensure leaves dry quickly by avoiding overhead watering.",
                    "Isolate suspicious plants until definitive diagnosis is obtained.",
                ],
                "sanitation_guidance": [
                    "Sanitize pruning tools between plants as a universal precaution."
                ],
                "crop_management_advice": "Do not apply chemical pesticides based solely on inconclusive image detection.",
                "recommended_next_step": "Obtain in-person confirmation from an agricultural extension officer.",
                "source_name": knowledge_entry.get("source_name", "Extension Reference"),
                "source_url": knowledge_entry.get("source_url", ""),
                "date_reviewed": knowledge_entry.get("date_reviewed", ""),
                "important_limitations": knowledge_entry.get(
                    "important_limitations", "Visual diagnosis must be verified."
                ),
                "rules_triggered": rules_triggered,
                "warnings": warnings,
            }

        # Conclusive result
        is_healthy = "healthy" in predicted_class.lower()
        if is_healthy:
            rules_triggered.append(
                f"RULE_HEALTHY_STATUS: Model confidence ({confidence_pct}%) meets threshold for healthy foliage. "
                f"Routine preventive cultural practices generated."
            )
        else:
            rules_triggered.append(
                f"RULE_PATHOGEN_IDENTIFIED: High confidence ({confidence_pct}%) identification of {knowledge_entry.get('common_name')}. "
                f"Integrated Pest Management (IPM) guidance retrieved from {knowledge_entry.get('source_name')}."
            )

        return {
            "is_conclusive": True,
            "crop_matched": True,
            "predicted_class": predicted_class,
            "confidence_pct": confidence_pct,
            "common_name": knowledge_entry.get("common_name", predicted_class),
            "pathogen": knowledge_entry.get("pathogen", "N/A"),
            "description": knowledge_entry.get("description", ""),
            "observable_symptoms": knowledge_entry.get("observable_symptoms", []),
            "preventive_practices": knowledge_entry.get("preventive_practices", []),
            "sanitation_guidance": knowledge_entry.get("sanitation_guidance", []),
            "crop_management_advice": knowledge_entry.get("crop_management_advice", ""),
            "recommended_next_step": knowledge_entry.get("recommended_next_step", ""),
            "source_name": knowledge_entry.get("source_name", ""),
            "source_url": knowledge_entry.get("source_url", ""),
            "date_reviewed": knowledge_entry.get("date_reviewed", ""),
            "important_limitations": knowledge_entry.get("important_limitations", ""),
            "rules_triggered": rules_triggered,
            "warnings": warnings,
        }
