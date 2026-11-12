"""
AgriRover Dataset Preparation & Session-Grouped Stratified Splitter
==================================================================
Splits Bitter Gourd dataset into Train (70%), Val (15%), Test (15%)
while grouping images from the same capture session together to guarantee
zero data leakage.
"""

import os
import json
import random
from pathlib import Path
from collections import defaultdict

SEED = 42
random.seed(SEED)

DATASET_ROOT = Path(__file__).resolve().parent.parent / "data" / "bitter_gourd_dataset"
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "models" / "plant_disease"

# Standard AgriRover slug mapping for the 4 dataset classes
CLASS_SLUG_MAP = {
    "Bunchy top of bitter gourd(96)": "bunchy_top",
    "Downy mildew(944)": "downy_mildew",
    "Healthy leaf(328)": "healthy",
    "Leaf curl (Mosaic virus)(1056)": "viral_symptoms",
}

CLASS_DISPLAY_NAMES = {
    "bunchy_top": "Bunchy Top",
    "downy_mildew": "Downy Mildew",
    "healthy": "Healthy Leaf",
    "viral_symptoms": "Leaf Curl (Mosaic Virus)",
}


def extract_session_id(path: Path) -> str:
    """Group crops/bursts by timestamp prefix: IMG_YYYYMMDD_HHMMSS."""
    parts = path.stem.split("_")
    if len(parts) >= 3 and parts[0] == "IMG":
        return f"{parts[1]}_{parts[2]}"
    return path.stem


def prepare_dataset(
    dataset_dir: Path = DATASET_ROOT,
    output_dir: Path = ARTIFACTS_DIR,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Preparing dataset from: {dataset_dir}")

    # Discover classes
    raw_class_dirs = sorted([d for d in dataset_dir.iterdir() if d.is_dir()])
    if not raw_class_dirs:
        raise ValueError(f"No class subdirectories found in {dataset_dir}")

    class_names = []
    class_to_idx = {}
    idx_to_class = {}

    for idx, cdir in enumerate(raw_class_dirs):
        slug = CLASS_SLUG_MAP.get(cdir.name, cdir.name.lower().replace(" ", "_"))
        class_names.append(slug)
        class_to_idx[slug] = idx
        idx_to_class[idx] = slug

    print(f"Discovered {len(class_names)} classes: {class_names}")

    train_samples = []
    val_samples = []
    test_samples = []

    split_stats = {
        "train": defaultdict(int),
        "val": defaultdict(int),
        "test": defaultdict(int),
    }

    # Group by session per class to prevent data leakage
    for cdir in raw_class_dirs:
        slug = CLASS_SLUG_MAP.get(cdir.name, cdir.name.lower().replace(" ", "_"))
        cls_idx = class_to_idx[slug]

        img_files = sorted([
            f for f in cdir.iterdir()
            if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
        ])

        # Group by session
        sessions = defaultdict(list)
        for f in img_files:
            sid = extract_session_id(f)
            # Store relative path to dataset root or absolute
            sessions[sid].append(str(f.resolve()))

        session_keys = list(sessions.keys())
        random.seed(SEED)
        random.shuffle(session_keys)

        # Distribute sessions across train/val/test according to image counts
        total_class_images = len(img_files)
        target_train = int(total_class_images * train_ratio)
        target_val = int(total_class_images * val_ratio)

        cls_train, cls_val, cls_test = [], [], []
        curr_train_cnt = 0
        curr_val_cnt = 0

        for sid in session_keys:
            img_list = sessions[sid]
            sample_tuples = [{"path": p, "label": cls_idx, "class_name": slug, "session": sid} for p in img_list]

            if curr_train_cnt < target_train:
                cls_train.extend(sample_tuples)
                curr_train_cnt += len(img_list)
            elif curr_val_cnt < target_val:
                cls_val.extend(sample_tuples)
                curr_val_cnt += len(img_list)
            else:
                cls_test.extend(sample_tuples)

        train_samples.extend(cls_train)
        val_samples.extend(cls_val)
        test_samples.extend(cls_test)

        split_stats["train"][slug] = len(cls_train)
        split_stats["val"][slug] = len(cls_val)
        split_stats["test"][slug] = len(cls_test)

    # Save class mapping
    class_mapping = {
        "class_to_idx": class_to_idx,
        "idx_to_class": {str(k): v for k, v in idx_to_class.items()},
        "display_names": CLASS_DISPLAY_NAMES,
        "raw_folder_map": {cdir.name: CLASS_SLUG_MAP.get(cdir.name, cdir.name) for cdir in raw_class_dirs},
        "num_classes": len(class_names),
    }

    class_mapping_file = output_dir / "class_mapping.json"
    with open(class_mapping_file, "w", encoding="utf-8") as f:
        json.dump(class_mapping, f, indent=2)

    # Save split manifest
    manifest = {
        "train": train_samples,
        "val": val_samples,
        "test": test_samples,
        "summary": {
            "total_images": len(train_samples) + len(val_samples) + len(test_samples),
            "train_count": len(train_samples),
            "val_count": len(val_samples),
            "test_count": len(test_samples),
            "train_pct": round(len(train_samples) / (len(train_samples) + len(val_samples) + len(test_samples)) * 100, 1),
            "val_pct": round(len(val_samples) / (len(train_samples) + len(val_samples) + len(test_samples)) * 100, 1),
            "test_pct": round(len(test_samples) / (len(train_samples) + len(val_samples) + len(test_samples)) * 100, 1),
            "per_class_breakdown": {
                "train": dict(split_stats["train"]),
                "val": dict(split_stats["val"]),
                "test": dict(split_stats["test"]),
            }
        }
    }

    manifest_file = output_dir / "split_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nSaved class mapping to: {class_mapping_file}")
    print(f"Saved split manifest to: {manifest_file}")
    print("\n--- Split Summary ---")
    print(f"Train: {manifest['summary']['train_count']} ({manifest['summary']['train_pct']}%)")
    print(f"Val:   {manifest['summary']['val_count']} ({manifest['summary']['val_pct']}%)")
    print(f"Test:  {manifest['summary']['test_count']} ({manifest['summary']['test_pct']}%)")
    print("Per-class breakdown:")
    for slug in class_names:
        print(f"  {slug:16s} -> Train: {split_stats['train'][slug]:4d} | Val: {split_stats['val'][slug]:4d} | Test: {split_stats['test'][slug]:4d}")

    return manifest


if __name__ == "__main__":
    prepare_dataset()
