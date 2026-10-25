"""Training script for Crop Disease Detection using Transfer Learning with MobileNetV2.

Fine-tunes a pretrained MobileNetV2 backbone on agricultural leaf images,
tracks validation accuracy, saves best model weights, and exports training metrics.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
import torch
import torch.nn as nn
from torch.optim import Adam
from torchvision import models
from torchvision.models import MobileNet_V2_Weights

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.dataset_loader import (
    SUPPORTED_CLASSES,
    create_splits,
    download_plantvillage_subset,
    get_dataloaders,
)


def build_model(num_classes: int = 8, freeze_backbone: bool = True) -> nn.Module:
    """Construct MobileNetV2 model with custom classification head for crop diseases.

    Args:
        num_classes: Number of target agricultural disease classes (default: 8).
        freeze_backbone: Whether to freeze feature extractor layers for transfer learning.

    Returns:
        PyTorch nn.Module ready for training.
    """
    weights = MobileNet_V2_Weights.DEFAULT
    model = models.mobilenet_v2(weights=weights)

    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False

    # Replace classifier head with a 2-stage dense head with dropout regularization
    last_channel = model.last_channel
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.25),
        nn.Linear(last_channel, 128),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.3),
        nn.Linear(128, num_classes),
    )

    return model


def train_model(
    data_dir: Path,
    splits_dir: Path,
    model_save_path: Path,
    class_indices_path: Path,
    metrics_save_path: Path,
    epochs: int = 8,
    batch_size: int = 16,
    learning_rate: float = 0.001,
) -> Dict[str, Any]:
    """Train MobileNetV2 on dataset splits and persist best model."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training on device: {device}")

    # Prepare loaders
    train_loader, val_loader, test_loader, class_to_idx, idx_to_class = get_dataloaders(
        splits_dir, batch_size=batch_size
    )

    # Save class indices mapping
    class_indices_path.parent.mkdir(parents=True, exist_ok=True)
    with open(class_indices_path, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in idx_to_class.items()}, f, indent=2)
    print(f"[*] Saved class indices mapping to {class_indices_path}")

    model = build_model(num_classes=len(SUPPORTED_CLASSES), freeze_backbone=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(
        [p for p in model.parameters() if p.requires_grad], lr=learning_rate
    )

    best_val_acc = 0.0
    history: List[Dict[str, float]] = []
    start_time = time.time()

    print(f"[*] Beginning transfer learning training ({epochs} epochs)...")

    for epoch in range(1, epochs + 1):
        # -----------------
        # Training Phase
        # -----------------
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += (preds == labels).sum().item()
            total_train += labels.size(0)

        train_loss = running_loss / max(total_train, 1)
        train_acc = correct_train / max(total_train, 1)

        # -----------------
        # Validation Phase
        # -----------------
        model.eval()
        val_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                correct_val += (preds == labels).sum().item()
                total_val += labels.size(0)

        epoch_val_loss = val_loss / max(total_val, 1)
        epoch_val_acc = correct_val / max(total_val, 1)

        epoch_record = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(epoch_val_loss, 4),
            "val_acc": round(epoch_val_acc, 4),
        }
        history.append(epoch_record)

        print(
            f"Epoch {epoch:02d}/{epochs:02d} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.1f}% | "
            f"Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc*100:.1f}%"
        )

        # Save best model based on validation accuracy
        if epoch_val_acc >= best_val_acc:
            best_val_acc = epoch_val_acc
            model_save_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), str(model_save_path))
            print(f"  -> Checkpoint saved with Val Acc: {epoch_val_acc*100:.1f}%")

    elapsed_time = round(time.time() - start_time, 2)
    print(f"[*] Training complete in {elapsed_time}s. Best Val Acc: {best_val_acc*100:.1f}%")

    # Export metrics
    metrics_save_path.parent.mkdir(parents=True, exist_ok=True)
    summary_data = {
        "model_architecture": "MobileNetV2",
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "elapsed_training_seconds": elapsed_time,
        "best_val_acc": round(best_val_acc, 4),
        "history": history,
    }
    with open(metrics_save_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    return summary_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MobileNetV2 for Crop Disease Classification")
    parser.add_argument("--epochs", type=int, default=6, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--download-data", action="store_true", help="Download PlantVillage images")
    parser.add_argument("--num-per-class", type=int, default=25, help="Number of images per class to download")
    args = parser.parse_args()

    data_dir = PROJECT_ROOT / "data" / "plantvillage_raw"
    splits_dir = PROJECT_ROOT / "data" / "splits"
    sample_images_dir = PROJECT_ROOT / "static" / "sample_images"
    model_save_path = PROJECT_ROOT / "ml" / "models" / "mobilenetv2_crop_disease.pth"
    class_indices_path = PROJECT_ROOT / "ml" / "models" / "class_indices.json"
    metrics_save_path = PROJECT_ROOT / "experiments" / "training_history.json"

    if args.download_data or not data_dir.exists():
        print("[*] Downloading authentic PlantVillage sample subset...")
        counts = download_plantvillage_subset(
            data_dir, num_per_class=args.num_per_class, sample_images_dir=sample_images_dir
        )
        print("[*] Creating stratified train/val/test splits...")
        create_splits(data_dir, splits_dir)

    train_model(
        data_dir,
        splits_dir,
        model_save_path,
        class_indices_path,
        metrics_save_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )
