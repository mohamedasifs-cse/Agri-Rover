"""
AgriRover Plant Disease Model Evaluation & Calibration Script
============================================================
Evaluates best_model.pth on the untouched TEST set.
Computes:
- Overall accuracy, Balanced accuracy, Macro-F1, Weighted-F1
- Per-class precision, recall, F1-score, and support
- Confusion matrix
- Per-class error analysis
- Model size on disk and single-image inference latency
- Confidence calibration breakdown
- Saves evaluation_report.json
"""

import json
import time
from pathlib import Path
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import torchvision.models as models
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
    f1_score
)

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "plant_disease"
MODEL_WEIGHTS = MODELS_DIR / "best_model.pth"
MANIFEST_PATH = MODELS_DIR / "split_manifest.json"
CLASS_MAPPING_PATH = MODELS_DIR / "class_mapping.json"
REPORT_PATH = MODELS_DIR / "evaluation_report.json"


def run_evaluation(device_str: str = "auto") -> dict:
    if device_str == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)

    print(f"Running evaluation on device: {device}")

    # Load mappings and manifest
    with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
        class_mapping = json.load(f)
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    test_samples = manifest["test"]
    num_classes = class_mapping["num_classes"]
    idx_to_class = {int(k): v for k, v in class_mapping["idx_to_class"].items()}
    class_names = [idx_to_class[i] for i in range(num_classes)]

    # Transform
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Rebuild model structure
    weights = models.EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(in_features, num_classes)
    )

    # Load weights
    print(f"Loading weights from: {MODEL_WEIGHTS}")
    state_dict = torch.load(MODEL_WEIGHTS, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    # Model size
    model_size_mb = round(MODEL_WEIGHTS.stat().st_size / (1024 * 1024), 2)

    all_labels = []
    all_preds = []
    all_confs = []
    latencies = []

    softmax = nn.Softmax(dim=1)

    print(f"Evaluating on {len(test_samples)} untouched test images...")
    with torch.no_grad():
        for item in test_samples:
            img_path = item["path"]
            label = item["label"]

            with Image.open(img_path) as img:
                tensor = val_transform(img.convert("RGB")).unsqueeze(0).to(device)

            t0 = time.perf_counter()
            outputs = model(tensor)
            probs = softmax(outputs)
            lat = (time.perf_counter() - t0) * 1000.0  # ms
            latencies.append(lat)

            conf, pred_idx = torch.max(probs, dim=1)
            all_labels.append(label)
            all_preds.append(pred_idx.item())
            all_confs.append(round(conf.item(), 4))

    # Metrics
    acc = accuracy_score(all_labels, all_preds)
    bal_acc = balanced_accuracy_score(all_labels, all_preds)
    precision, recall, f1, support = precision_recall_fscore_support(
        all_labels, all_preds, labels=list(range(num_classes)), zero_division=0
    )
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    weighted_f1 = f1_score(all_labels, all_preds, average="weighted", zero_division=0)
    cm = confusion_matrix(all_labels, all_preds, labels=list(range(num_classes))).tolist()

    # Per-class summary
    per_class_metrics = {}
    for i, name in enumerate(class_names):
        per_class_metrics[name] = {
            "display_name": class_mapping["display_names"].get(name, name),
            "precision": round(float(precision[i]), 4),
            "recall": round(float(recall[i]), 4),
            "f1_score": round(float(f1[i]), 4),
            "test_support": int(support[i]),
        }

    # Error analysis
    error_analysis = []
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j and cm[i][j] > 0:
                error_analysis.append({
                    "true_class": class_names[i],
                    "predicted_as": class_names[j],
                    "error_count": cm[i][j],
                    "percentage_of_true_class": round((cm[i][j] / max(1, support[i])) * 100, 2)
                })

    # Confidence calibration bins
    conf_bins = {"0.5-0.7": {"count": 0, "correct": 0},
                 "0.7-0.9": {"count": 0, "correct": 0},
                 "0.9-1.0": {"count": 0, "correct": 0}}
    for pred, true, conf in zip(all_preds, all_labels, all_confs):
        correct = (pred == true)
        if conf >= 0.9:
            b = "0.9-1.0"
        elif conf >= 0.7:
            b = "0.7-0.9"
        else:
            b = "0.5-0.7"
        conf_bins[b]["count"] += 1
        if correct:
            conf_bins[b]["correct"] += 1

    calibration_summary = {}
    for b, data in conf_bins.items():
        cnt = data["count"]
        acc_bin = round(data["correct"] / cnt, 4) if cnt > 0 else 0.0
        calibration_summary[b] = {
            "sample_count": cnt,
            "accuracy": acc_bin,
        }

    avg_latency_ms = round(sum(latencies) / len(latencies), 2)
    p95_latency_ms = round(sorted(latencies)[int(0.95 * len(latencies))], 2)

    report = {
        "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_architecture": "EfficientNet-B0",
        "model_size_mb": model_size_mb,
        "device": str(device),
        "test_dataset_size": len(test_samples),
        "total_dataset_size": manifest["summary"]["total_images"],
        "num_classes": num_classes,
        "classes": class_names,
        "summary_metrics": {
            "test_accuracy": round(float(acc), 4),
            "balanced_accuracy": round(float(bal_acc), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4),
            "mean_inference_latency_ms": avg_latency_ms,
            "p95_inference_latency_ms": p95_latency_ms,
        },
        "per_class_metrics": per_class_metrics,
        "confusion_matrix": {
            "classes": class_names,
            "matrix": cm
        },
        "error_analysis": error_analysis,
        "confidence_calibration": calibration_summary,
        "field_image_disclaimer": (
            "Model evaluated on curated Bitter Gourd pandal leaf dataset. "
            "Real-world field images with heavy occlusions, direct sun glare, or non-leaf objects "
            "should be verified with calibrated confidence thresholds."
        )
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 60)
    print(" AgriRover EfficientNet-B0 Test Evaluation Report")
    print("=" * 60)
    print(f"Overall Test Accuracy:    {acc * 100:.2f}%")
    print(f"Balanced Accuracy:        {bal_acc * 100:.2f}%")
    print(f"Macro F1-Score:           {macro_f1:.4f}")
    print(f"Model Disk Size:          {model_size_mb} MB")
    print(f"Avg CPU Inference Latency:{avg_latency_ms} ms / image (P95: {p95_latency_ms} ms)")
    print("\nPer-Class Breakdown:")
    for name, m in per_class_metrics.items():
        print(f"  - {name:16s} Precision: {m['precision']:.3f} | Recall: {m['recall']:.3f} | F1: {m['f1_score']:.3f} | Support: {m['test_support']}")
    print("\nConfusion Matrix:")
    header = "       " + " ".join([f"{c[:6]:>7}" for c in class_names])
    print(header)
    for i, row in enumerate(cm):
        print(f"{class_names[i][:6]:>6}:" + " ".join([f"{val:>7}" for val in row]))

    print(f"\nReport written to: {REPORT_PATH}")
    return report


if __name__ == "__main__":
    run_evaluation()
