"""
AgriRover PyTorch EfficientNet-B0 Transfer Learning Training Pipeline
===================================================================
Features:
- Pretrained EfficientNet-B0 from torchvision
- Inverse class frequency weighted CrossEntropyLoss
- Two-stage training: classifier warm-up + backbone fine-tuning
- Realistic agricultural data augmentations
- Early stopping & model checkpointing based on Validation Macro-F1
- Saves best checkpoint, class mapping, model configuration, and training history
"""

import os
import sys
import json
import time
import copy
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.models as models
from torchvision.models import EfficientNet_B0_Weights
from sklearn.metrics import f1_score, accuracy_score

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "plant_disease"
MANIFEST_PATH = MODELS_DIR / "split_manifest.json"
CLASS_MAPPING_PATH = MODELS_DIR / "class_mapping.json"


class PlantDiseaseDataset(Dataset):
    """Dataset loading images directly from split manifest dictionary."""

    def __init__(self, samples: List[Dict], transform=None):
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        img_path = item["path"]
        label = item["label"]
        with Image.open(img_path) as img:
            image = img.convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, torch.tensor(label, dtype=torch.long)


def get_transforms():
    """Return agricultural augmentation pipeline and validation pipeline."""
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]

    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    return train_transform, val_transform


def build_model(num_classes: int) -> nn.Module:
    """Instantiate EfficientNet-B0 with custom classifier."""
    print("Loading pretrained EfficientNet-B0 weights...")
    weights = EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, num_classes)
    )
    return model


def compute_class_weights(train_samples: List[Dict], num_classes: int, device: torch.device) -> torch.Tensor:
    """Compute inverse-frequency class weights for balanced cross-entropy."""
    counts = [0] * num_classes
    for s in train_samples:
        counts[s["label"]] += 1
    total = sum(counts)
    weights = [total / (num_classes * max(1, c)) for c in counts]
    print(f"Train sample counts per class: {counts}")
    print(f"Computed loss class weights: {[round(w, 3) for w in weights]}")
    return torch.tensor(weights, dtype=torch.float, device=device)


def train_model(
    batch_size: int = 32,
    head_epochs: int = 3,
    finetune_epochs: int = 6,
    device_str: str = "auto",
):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Select compute device
    if device_str == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)
    print(f"Training on device: {device}")

    # Load manifest and mappings
    if not MANIFEST_PATH.exists() or not CLASS_MAPPING_PATH.exists():
        print("Manifest not found. Running prepare_dataset.py first...")
        from prepare_dataset import prepare_dataset
        prepare_dataset()

    with open
    (MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
        class_mapping = json.load(f)

    num_classes = class_mapping["num_classes"]
    train_samples = manifest["train"]
    val_samples = manifest["val"]

    train_transform, val_transform = get_transforms()
    train_dataset = PlantDiseaseDataset(train_samples, transform=train_transform)
    val_dataset = PlantDiseaseDataset(val_samples, transform=val_transform)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=(device.type == "cuda")
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=(device.type == "cuda")
    )

    # Loss function with class weights
    class_weights = compute_class_weights(train_samples, num_classes, device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # Build model
    model = build_model(num_classes).to(device)

    best_val_f1 = -1.0
    best_model_wts = copy.deepcopy(model.state_dict())
    history = {
        "epochs": [],
        "train_loss": [],
        "val_loss": [],
        "train_acc": [],
        "val_acc": [],
        "val_macro_f1": []
    }

    # ── STAGE 1: Train Classifier Head Only ──────────────────────────────────────
    print("\n" + "=" * 60)
    print("STAGE 1: Training Classifier Head (Backbone Frozen)")
    print("=" * 60)

    for param in model.features.parameters():
        param.requires_grad = False
    for param in model.classifier.parameters():
        param.requires_grad = True

    optimizer_head = torch.optim.AdamW(model.classifier.parameters(), lr=1e-3, weight_decay=1e-4)

    for epoch in range(1, head_epochs + 1):
        t0 = time.time()
        model.train()
        running_loss = 0.0
        all_preds, all_labels = [], []

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer_head.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer_head.step()

            running_loss += loss.item() * inputs.size(0)
            preds = torch.argmax(outputs, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

        train_loss = running_loss / len(train_dataset)
        train_acc = accuracy_score(all_labels, all_preds)

        # Validation
        val_loss, val_acc, val_f1 = evaluate_split(model, val_loader, criterion, device)
        elapsed = time.time() - t0

        print(f"Epoch {epoch:02d}/{head_epochs:02d} [Head] ({elapsed:.1f}s) - "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}% Macro-F1: {val_f1:.4f}")

        history["epochs"].append(f"head_{epoch}")
        history["train_loss"].append(round(train_loss, 4))
        history["val_loss"].append(round(val_loss, 4))
        history["train_acc"].append(round(train_acc, 4))
        history["val_acc"].append(round(val_acc, 4))
        history["val_macro_f1"].append(round(val_f1, 4))

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_model_wts = copy.deepcopy(model.state_dict())

    # ── STAGE 2: Fine-Tuning Backbone + Classifier ──────────────────────────────
    print("\n" + "=" * 60)
    print("STAGE 2: Fine-Tuning Backbone & Classifier")
    print("=" * 60)

    # Unfreeze entire network with lower learning rate
    for param in model.parameters():
        param.requires_grad = True

    optimizer_ft = torch.optim.AdamW([
        {"params": model.features.parameters(), "lr": 1e-4},
        {"params": model.classifier.parameters(), "lr": 5e-4},
    ], weight_decay=1e-4)

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer_ft, T_max=finetune_epochs, eta_min=1e-6)

    early_stopping_patience = 4
    no_improve_epochs = 0

    for epoch in range(1, finetune_epochs + 1):
        t0 = time.time()
        model.train()
        running_loss = 0.0
        all_preds, all_labels = [], []

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer_ft.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer_ft.step()

            running_loss += loss.item() * inputs.size(0)
            preds = torch.argmax(outputs, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

        scheduler.step()
        train_loss = running_loss / len(train_dataset)
        train_acc = accuracy_score(all_labels, all_preds)

        # Validation
        val_loss, val_acc, val_f1 = evaluate_split(model, val_loader, criterion, device)
        elapsed = time.time() - t0

        print(f"Epoch {epoch:02d}/{finetune_epochs:02d} [Fine-tune] ({elapsed:.1f}s) - "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}% Macro-F1: {val_f1:.4f}")

        history["epochs"].append(f"ft_{epoch}")
        history["train_loss"].append(round(train_loss, 4))
        history["val_loss"].append(round(val_loss, 4))
        history["train_acc"].append(round(train_acc, 4))
        history["val_acc"].append(round(val_acc, 4))
        history["val_macro_f1"].append(round(val_f1, 4))

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_model_wts = copy.deepcopy(model.state_dict())
            no_improve_epochs = 0
            print(f"  --> Saved new best checkpoint (Val Macro-F1: {val_f1:.4f})")
        else:
            no_improve_epochs += 1
            if no_improve_epochs >= early_stopping_patience:
                print(f"Early stopping triggered after {no_improve_epochs} epochs without improvement.")
                break

    # Save best checkpoint
    best_model_path = MODELS_DIR / "best_model.pth"
    torch.save(best_model_wts, best_model_path)
    print(f"\n[SUCCESS] Best model checkpoint saved to: {best_model_path}")

    # Save model configuration metadata
    model_config = {
        "architecture": "efficientnet_b0",
        "num_classes": num_classes,
        "input_resolution": [224, 224],
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225],
        },
        "best_val_macro_f1": round(best_val_f1, 4),
        "trained_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "classes": class_mapping["class_to_idx"],
        "confidence_threshold": 0.60,
    }
    with open(MODELS_DIR / "model_config.json", "w", encoding="utf-8") as f:
        json.dump(model_config, f, indent=2)

    # Save history
    with open(MODELS_DIR / "training_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    return model_config, history


def evaluate_split(model, dataloader, criterion, device):
    """Compute loss, accuracy, and macro-F1 on a split."""
    model.eval()
    running_loss = 0.0
    all_preds, all_labels = [], []

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * inputs.size(0)
            preds = torch.argmax(outputs, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    total_loss = running_loss / len(dataloader.dataset)
    acc = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    return total_loss, acc, f1


if __name__ == "__main__":
    train_model(batch_size=32, head_epochs=3, finetune_epochs=6)
