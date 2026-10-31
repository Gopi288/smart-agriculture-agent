"""Image preprocessing pipeline for agricultural disease detection inference.

Safely loads, decodes, resizes, and normalizes leaf images matching
MobileNetV2 ImageNet input specifications.

Memory optimization: Large uploaded images are pre-downsized to a maximum
dimension before Pillow decodes the full pixel buffer, preventing OOM on
Render's constrained free-tier environment.
"""

from pathlib import Path
from typing import Tuple, Union
from PIL import Image
import torch
from torchvision import transforms

# Maximum dimension for pre-downsizing before the primary transform pipeline.
# Uploaded field photos can be 4000×3000 DSLR images (~36MB uncompressed RGB).
# Capping at 512px before the Compose transform saves ~25× peak memory.
_PREDECODE_MAX_DIM = 512

# Preprocessing transforms matching MobileNetV2 training specifications.
# Resize and CenterCrop strategy is equivalent to the original 256→224 crop
# but we accept any reasonable source resolution thanks to pre-downsizing above.
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


def _predecode_resize(img: Image.Image) -> Image.Image:
    """Downsample very large images before full pixel decode.

    Uses Image.thumbnail() which is in-place and never upscales.
    This prevents multi-megabyte RAM spikes on large field photographs.
    """
    if max(img.size) > _PREDECODE_MAX_DIM:
        img.thumbnail((_PREDECODE_MAX_DIM, _PREDECODE_MAX_DIM), Image.BICUBIC)
    return img


def preprocess_image(image_input: Union[Path, str, Image.Image]) -> Tuple[torch.Tensor, Tuple[int, int]]:
    """Decode and transform a leaf photograph for neural network inference.

    Args:
        image_input: File path (Path/str) or already-opened PIL Image.

    Returns:
        Tuple of (preprocessed_tensor: torch.Tensor of shape [1, 3, 224, 224],
                  original_dimensions: (width, height) before any transforms)
    """
    if isinstance(image_input, (str, Path)):
        path = Path(image_input)
        if not path.exists():
            raise FileNotFoundError(f"Image not found at {path}")
        with Image.open(path) as img:
            img = img.convert("RGB")
            orig_size = img.size
            img = _predecode_resize(img)
            tensor = INFERENCE_TRANSFORMS(img)
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
        orig_size = img.size
        img = _predecode_resize(img)
        tensor = INFERENCE_TRANSFORMS(img)
    else:
        raise TypeError("image_input must be a file path or PIL Image object.")

    # Add batch dimension: [3, 224, 224] -> [1, 3, 224, 224]
    batch_tensor = tensor.unsqueeze(0)
    return batch_tensor, orig_size
