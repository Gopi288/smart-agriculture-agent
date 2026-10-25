"""Dataset preparation and loader for PlantVillage agricultural image classification.

Handles dataset acquisition, integrity verification, stratified train/val/test
splitting, data augmentation pipelines, and PyTorch DataLoader generation.
Dataset Source: PlantVillage (David Hughes & Marcel Salathe, CC BY-SA 4.0).
"""

import json
import os
import random
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import requests
from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

# Supported 8 classes
SUPPORTED_CLASSES = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Corn_(maize)___Common_rust",
    "Corn_(maize)___healthy",
]

# GitHub repository tree endpoint for raw images
GITHUB_API_BASE = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color"

# Standard ImageNet normalization parameters for MobileNetV2
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_transforms() -> Tuple[transforms.Compose, transforms.Compose]:
    """Return PyTorch transform pipelines for training and validation/testing.

    Training pipeline includes domain-appropriate data augmentation (flips, slight rotations,
    affine shifts) to simulate field variability without distorting diagnostic lesions.
    """
    train_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.3),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )

    eval_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )

    return train_transform, eval_transform


class PlantDiseaseDataset(Dataset):
    """PyTorch Dataset loading agricultural leaf images from an organized folder."""

    def __init__(self, file_paths: List[Path], class_to_idx: Dict[str, int], transform=None):
        self.file_paths = file_paths
        self.class_to_idx = class_to_idx
        self.transform = transform

    def __len__(self) -> int:
        return len(self.file_paths)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path = self.file_paths[idx]
        class_name = img_path.parent.name
        label = self.class_to_idx[class_name]

        with Image.open(img_path) as img:
            img = img.convert("RGB")
            if self.transform:
                tensor = self.transform(img)
            else:
                tensor = transforms.ToTensor()(img)

        return tensor, label


def download_plantvillage_subset(
    output_dir: Path,
    num_per_class: int = 25,
    sample_images_dir: Path = None,
) -> Dict[str, int]:
    """Download authentic PlantVillage sample images for the 8 supported classes.

    Downloads legitimate image files directly from the public PlantVillage repository
    with image integrity checks. Also saves copies into sample_images_dir for UI demonstration.

    Args:
        output_dir: Root directory to save the raw dataset.
        num_per_class: Number of representative images per class (default: 25).
        sample_images_dir: Optional path to save demo images for the web interface.

    Returns:
        Dictionary mapping class names to counts of successfully acquired images.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    if sample_images_dir:
        sample_images_dir.mkdir(parents=True, exist_ok=True)

    counts: Dict[str, int] = {}
    headers = {"User-Agent": "SmartAgricultureAgent-MiniCapstone/1.0"}

    # Map class name to GitHub folder name (PlantVillage has a trailing underscore on Common_rust_)
    github_folder_map = {
        "Corn_(maize)___Common_rust": "Corn_(maize)___Common_rust_",
    }

    for class_name in SUPPORTED_CLASSES:
        class_folder = output_dir / class_name
        class_folder.mkdir(parents=True, exist_ok=True)

        remote_folder_name = github_folder_map.get(class_name, class_name)
        api_url = f"{GITHUB_API_BASE}/{remote_folder_name}"
        try:
            r = requests.get(api_url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"[Warning] Failed to list {class_name} from GitHub API (HTTP {r.status_code})")
                continue

            items = [item for item in r.json() if item["type"] == "file" and item["name"].lower().endswith((".jpg", ".jpeg", ".png"))]
            selected_items = items[:num_per_class]

            success_count = 0
            for idx, item in enumerate(selected_items):
                target_path = class_folder / item["name"]
                if target_path.exists() and target_path.stat().st_size > 0:
                    success_count += 1
                    continue

                dl_r = requests.get(item["download_url"], headers=headers, timeout=15)
                if dl_r.status_code == 200:
                    with open(target_path, "wb") as f:
                        f.write(dl_r.content)

                    # Verify image validity
                    try:
                        with Image.open(target_path) as test_img:
                            test_img.verify()
                        success_count += 1

                        # Save one or two sample images for UI demonstration
                        if sample_images_dir and idx < 2:
                            demo_dest = sample_images_dir / f"sample_{class_name}_{idx+1}.jpg"
                            shutil.copy2(target_path, demo_dest)

                    except Exception:
                        if target_path.exists():
                            os.remove(target_path)

            counts[class_name] = success_count
            print(f"[{class_name}] Downloaded and verified {success_count} images.")

        except Exception as exc:
            print(f"[Error] Failed processing class {class_name}: {exc}")
            counts[class_name] = 0

    return counts


def create_splits(
    dataset_dir: Path,
    splits_dir: Path,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> Dict[str, int]:
    """Perform stratified split of dataset images into train, val, and test sets.

    Ensures zero leakage between training, validation, and held-out test sets.
    """
    random.seed(seed)
    train_dir = splits_dir / "train"
    val_dir = splits_dir / "val"
    test_dir = splits_dir / "test"

    for d in [train_dir, val_dir, test_dir]:
        d.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, int] = {"train": 0, "val": 0, "test": 0}

    for class_name in SUPPORTED_CLASSES:
        src_folder = dataset_dir / class_name
        if not src_folder.exists():
            continue

        images = [f for f in src_folder.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        random.shuffle(images)

        n_total = len(images)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)

        train_imgs = images[:n_train]
        val_imgs = images[n_train : n_train + n_val]
        test_imgs = images[n_train + n_val :]

        for split_name, split_imgs, target_base in [
            ("train", train_imgs, train_dir),
            ("val", val_imgs, val_dir),
            ("test", test_imgs, test_dir),
        ]:
            class_target = target_base / class_name
            class_target.mkdir(parents=True, exist_ok=True)
            for img in split_imgs:
                dest = class_target / img.name
                shutil.copy2(img, dest)
                summary[split_name] += 1

    return summary


def get_dataloaders(
    splits_dir: Path, batch_size: int = 16
) -> Tuple[DataLoader, DataLoader, DataLoader, Dict[str, int], Dict[int, str]]:
    """Construct PyTorch DataLoaders for train, val, and test partitions."""
    train_transform, eval_transform = get_transforms()

    train_dir = splits_dir / "train"
    val_dir = splits_dir / "val"
    test_dir = splits_dir / "test"

    # Build class to index mapping
    class_to_idx = {name: i for i, name in enumerate(SUPPORTED_CLASSES)}
    idx_to_class = {i: name for name, i in class_to_idx.items()}

    def collect_files(base_dir: Path) -> List[Path]:
        files: List[Path] = []
        for class_name in SUPPORTED_CLASSES:
            cf = base_dir / class_name
            if cf.exists():
                files.extend([f for f in cf.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"}])
        return files

    train_files = collect_files(train_dir)
    val_files = collect_files(val_dir)
    test_files = collect_files(test_dir)

    train_ds = PlantDiseaseDataset(train_files, class_to_idx, transform=train_transform)
    val_ds = PlantDiseaseDataset(val_files, class_to_idx, transform=eval_transform)
    test_ds = PlantDiseaseDataset(test_files, class_to_idx, transform=eval_transform)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, test_loader, class_to_idx, idx_to_class
