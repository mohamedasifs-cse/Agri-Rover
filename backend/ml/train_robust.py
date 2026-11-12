"""
AgriRover Domain-Robust Plant Disease Training Pipeline
=======================================================
Designed specifically for real-world field images and external photos:
1. Retains pretrained ImageNet botanical feature extractors (freezes early backbone layers)
2. Domain-generalization augmentations (RandomGrayscale, ColorJitter, RandomPerspective)
   to eliminate background and camera-sensor shortcut learning
3. High regularization (Dropout 0.4, Weight Decay 1e-3) to prevent feature collapse
4. Preserves full-leaf aspect ratio resizing
"""

import copy
import json
import time
from pathlib import Path
from typing import Dict, List
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.models as models
from torchvision.models import EfficientNet_B0_Weights
from sklearn.metrics import f1_score, accuracy_score

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "plant_disease"
MANIFEST_PATH = MODELS_DIR / "split_manifest.json"
CLASS_MAPPING_PATH = MODELS_DIR / "class_mapping.json"


class RobustPlantDataset(Dataset):
    def __init__(self, samples: List[Dict], transform=None):
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        with Image.open(item["path"]) as img:
            image = img.convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, torch.tensor(item["label"], dtype=torch.long)


def get_robust_transforms():
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]

    # Domain-invariance augmentations: simulate real field lighting, shadows, camera differences
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.6, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=30),
        transforms.RandomPerspective(distortion_scale=0.2, p=0.3),
        # Strong color jitter to prevent the model from using background paper brightness as a shortcut
        transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.08),
        # Random grayscale forces the model to learn structural lesion textures and spot morphology
        transforms.RandomGrayscale(p=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    return train_transform, val_transform


def build_robust_model(num_classes: int) -> nn.Module:
    weights = EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)

    # Freeze low and mid-level feature blocks (layers 0 through 6)
    # This prevents the network from destroying general ImageNet edge/texture features
    for idx, child in enumerate(model.features):
        if idx < 6:
            for param in child.parameters():
                param.requires_grad = False
        else:
            for param in child.parameters():
                param.requires_grad = True

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, num_classes)
    )
    return model


def train_robust(epochs: int = 5, batch_size: int = 32):
    device = torch.device("cpu")
    print(f"Training robust domain-generalized model on {device}...")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
        class_mapping = json.load(f)

    num_classes = class_mapping["num_classes"]
    train_samples = manifest["train"]
    val_samples = manifest["val"]

    train_tf, val_tf = get_robust_transforms()
    train_loader = DataLoader(RobustPlantDataset(train_samples, train_tf), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(RobustPlantDataset(val_samples, val_tf), batch_size=batch_size, shuffle=False)

    # Balanced class weights with moderate smoothing to avoid healthy bias
    counts = [0] * num_classes
    for s in train_samples:
        counts[s["label"]] += 1
    total = sum(counts)
    # Square-root smoothed inverse weights prevent rare classes from dominating or healthy from being over-penalized
    weights = [(total / max(1, c)) ** 0.5 for c in counts]
    weights = [w / sum(weights) * num_classes for w in weights]
    class_weights_t = torch.tensor(weights, dtype=torch.float, device=device)
    print("Class sample counts:", counts)
    print("Smoothed loss weights:", [round(w, 3) for w in weights])

    criterion = nn.CrossEntropyLoss(weight=class_weights_t, label_smoothing=0.1)
    model = build_robust_model(num_classes).to(device)

    # Optimizer: higher lr for classifier head, lower lr for final backbone block
    optimizer = torch.optim.AdamW([
        {"params": [p for p in model.features.parameters() if p.requires_grad], "lr": 1e-4},
        {"params": model.classifier.parameters(), "lr": 1e-3},
    ], weight_decay=1e-3)

    best_val_f1 = -1.0
    best_weights = None

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        model.train()
        running_loss = 0.0
        all_preds, all_labels = [], []

        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * x.size(0)
            preds = torch.argmax(out, dim=1)
            all_preds.extend(preds.numpy())
            all_labels.extend(y.numpy())

        train_loss = running_loss / len(train_samples)
        train_acc = accuracy_score(all_labels, all_preds)

        # Validation
        model.eval()
        v_loss = 0.0
        v_preds, v_labels = [], []
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                loss = criterion(out, y)
                v_loss += loss.item() * x.size(0)
                preds = torch.argmax(out, dim=1)
                v_preds.extend(preds.numpy())
                v_labels.extend(y.numpy())

        val_loss = v_loss / len(val_samples)
        val_acc = accuracy_score(v_labels, v_preds)
        val_f1 = f1_score(v_labels, v_preds, average="macro", zero_division=0)
        elapsed = time.time() - t0

        print(f"Epoch {epoch:02d}/{epochs:02d} ({elapsed:.1f}s) - "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}% Macro-F1: {val_f1:.4f}")

        if val_f1 >= best_val_f1:
            best_val_f1 = val_f1
            best_weights = copy.deepcopy(model.state_dict())

    # Save robust model
    out_path = MODELS_DIR / "best_model.pth"
    torch.save(best_weights, out_path)
    print(f"[SUCCESS] Robust domain-generalized model saved to {out_path}")


if __name__ == "__main__":
    train_robust(epochs=5, batch_size=32)
