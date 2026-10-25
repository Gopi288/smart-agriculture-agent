# Machine Learning & AI Vision Pipeline

## Architecture Overview
The core foliar classifier is built on **MobileNetV2** (Sandler et al., Google Research, 2018), incorporating:
1. **Inverted Residual Blocks:** Expands to high-dimensional feature maps for depthwise convolution before projecting back.
2. **Linear Bottlenecks:** Prevents non-linear activations from collapsing low-dimensional manifold representations.
3. **Transfer Learning:** Pre-trained ImageNet weights are frozen in the feature extraction backbone (`features`), while a custom regularized classification head is fine-tuned.

## Custom Classification Head
```python
nn.Sequential(
    nn.Dropout(p=0.25),
    nn.Linear(model.last_channel, 128),
    nn.ReLU(inplace=True),
    nn.Dropout(p=0.30),
    nn.Linear(128, 8)  # 8 supported classes
)
```

## Training Execution
```powershell
# In PowerShell:
& ".\.venv\Scripts\python.exe" ml/train_model.py --download-data --epochs 6 --batch-size 16
```

## Evaluation Execution
```powershell
# In PowerShell:
& ".\.venv\Scripts\python.exe" ml/evaluate_model.py
```
Outputs classification report, confusion matrix, and latency benchmarks into `experiments/evaluation_metrics.json` and `.csv`.
