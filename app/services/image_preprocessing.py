"""Image preprocessing pipeline for agricultural disease detection inference.

Safely loads, decodes, resizes, and normalizes leaf images matching
MobileNetV2 ImageNet input specifications.
"""

from pathlib import Path
from typing import Tuple, Union
from PIL import Image
import torch
from torchvision import transforms

# Preprocessing transforms matching MobileNetV2 training specifications
INFERENCE_TRANSFORMS = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


def preprocess_image(image_input: Union[Path, str, Image.Image]) -> Tuple[torch.Tensor, Tuple[int, int]]:
    """Decode and transform a leaf photograph for neural network inference.

    Args:
        image_input: File path (Path/str) or already-opened PIL Image.

    Returns:
        Tuple of (preprocessed_tensor: torch.Tensor of shape [1, 3, 224, 224], original_dimensions: (width, height))
    """
    if isinstance(image_input, (str, Path)):
        path = Path(image_input)
        if not path.exists():
            raise FileNotFoundError(f"Image not found at {path}")
        with Image.open(path) as img:
            img = img.convert("RGB")
            orig_size = img.size
            tensor = INFERENCE_TRANSFORMS(img)
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
        orig_size = img.size
        tensor = INFERENCE_TRANSFORMS(img)
    else:
        raise TypeError("image_input must be a file path or PIL Image object.")

    # Add batch dimension: [3, 224, 224] -> [1, 3, 224, 224]
    batch_tensor = tensor.unsqueeze(0)
    return batch_tensor, orig_size
