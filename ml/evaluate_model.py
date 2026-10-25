"""Evaluation script for Crop Disease Detection model.

Computes accuracy, precision, recall, F1-score (macro and weighted),
per-class classification metrics, confusion matrix, and inference latency on
the held-out test split. Exports results to JSON and CSV.
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.dataset_loader import SUPPORTED_CLASSES, get_dataloaders
from ml.train_model import build_model


def evaluate_test_set(
    model_path: Path,
    splits_dir: Path,
    class_indices_path: Path,
    output_json_path: Path,
    output_csv_path: Path,
) -> Dict[str, Any]:
    """Evaluate model on held-out test partition and export rigorous metrics."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Running test evaluation on device: {device}")

    # Load class mappings
    with open(class_indices_path, "r", encoding="utf-8") as f:
        raw_map = json.load(f)
        idx_to_class = {int(k): v for k, v in raw_map.items()}

    _, _, test_loader, _, _ = get_dataloaders(splits_dir, batch_size=1)

    # Load model
    model = build_model(num_classes=len(SUPPORTED_CLASSES), freeze_backbone=False)
    if not model_path.exists():
        raise FileNotFoundError(f"Trained model not found at {model_path}. Train model first.")

    model.load_state_dict(torch.load(str(model_path), map_location=device))
    model = model.to(device)
    model.eval()

    y_true: List[int] = []
    y_pred: List[int] = []
    latencies_ms: List[float] = []

    print(f"[*] Evaluating {len(test_loader)} held-out test images...")

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            t0 = time.perf_counter()
            outputs = model(images)
            probabilities = F.softmax(outputs, dim=1)
            t1 = time.perf_counter()

            latencies_ms.append((t1 - t0) * 1000.0)

            _, preds = torch.max(probabilities, 1)

            y_true.extend(labels.cpu().numpy().tolist())
            y_pred.extend(preds.cpu().numpy().tolist())

    y_true_np = np.array(y_true)
    y_pred_np = np.array(y_pred)

    acc = float(accuracy_score(y_true_np, y_pred_np))
    prec_macro = float(precision_score(y_true_np, y_pred_np, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_true_np, y_pred_np, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_true_np, y_pred_np, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_true_np, y_pred_np, average="weighted", zero_division=0))

    cm = confusion_matrix(y_true_np, y_pred_np, labels=list(range(len(SUPPORTED_CLASSES)))).tolist()
    avg_latency = float(np.mean(latencies_ms))
    p95_latency = float(np.percentile(latencies_ms, 95))

    target_names = [idx_to_class[i] for i in range(len(SUPPORTED_CLASSES))]
    report_dict = classification_report(
        y_true_np,
        y_pred_np,
        labels=list(range(len(SUPPORTED_CLASSES))),
        target_names=target_names,
        output_dict=True,
        zero_division=0,
    )

    results: Dict[str, Any] = {
        "dataset_name": "PlantVillage (Hughes & Salathé, 2015)",
        "test_sample_size": len(y_true),
        "number_of_classes": len(SUPPORTED_CLASSES),
        "overall_metrics": {
            "accuracy": round(acc, 4),
            "precision_macro": round(prec_macro, 4),
            "recall_macro": round(rec_macro, 4),
            "f1_macro": round(f1_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
        },
        "latency_benchmarks_ms": {
            "mean_inference_time_ms": round(avg_latency, 2),
            "p95_inference_time_ms": round(p95_latency, 2),
            "device": str(device),
        },
        "per_class_metrics": {
            k: {
                "precision": round(v.get("precision", 0.0), 4),
                "recall": round(v.get("recall", 0.0), 4),
                "f1_score": round(v.get("f1-score", 0.0), 4),
                "support": int(v.get("support", 0)),
            }
            for k, v in report_dict.items()
            if isinstance(v, dict) and k in target_names
        },
        "confusion_matrix": {
            "labels": target_names,
            "matrix": cm,
        },
        "eval_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # Save to JSON
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Save to CSV
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Class Name", "Precision", "Recall", "F1-Score", "Support"])
        for cname in target_names:
            cdata = results["per_class_metrics"].get(cname, {})
            writer.writerow([
                cname,
                cdata.get("precision", 0.0),
                cdata.get("recall", 0.0),
                cdata.get("f1_score", 0.0),
                cdata.get("support", 0),
            ])
        writer.writerow([])
        writer.writerow(["Overall Accuracy", round(acc, 4)])
        writer.writerow(["Macro F1-Score", round(f1_macro, 4)])
        writer.writerow(["Weighted F1-Score", round(f1_weighted, 4)])
        writer.writerow(["Mean Latency (ms)", round(avg_latency, 2)])

    print("\n================== HELD-OUT TEST RESULTS ==================")
    print(f"Accuracy:         {acc*100:.2f}%")
    print(f"Macro F1-Score:   {f1_macro:.4f}")
    print(f"Mean Latency:     {avg_latency:.2f} ms / image on {device}")
    print(f"Metrics saved:    {output_json_path} & {output_csv_path}")
    print("===========================================================\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Crop Disease Classification Model")
    parser.add_argument("--model-path", type=str, default="ml/models/mobilenetv2_crop_disease.pth")
    args = parser.parse_args()

    model_path = PROJECT_ROOT / args.model_path
    splits_dir = PROJECT_ROOT / "data" / "splits"
    class_indices_path = PROJECT_ROOT / "ml" / "models" / "class_indices.json"
    output_json_path = PROJECT_ROOT / "experiments" / "evaluation_metrics.json"
    output_csv_path = PROJECT_ROOT / "experiments" / "evaluation_metrics.csv"

    evaluate_test_set(
        model_path, splits_dir, class_indices_path, output_json_path, output_csv_path
    )
