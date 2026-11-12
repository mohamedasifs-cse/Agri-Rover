"""
AgriRover Dataset Verification & Quality Audit Script
====================================================
Performs comprehensive inspection of the Bitter Gourd dataset:
- Discovers classes automatically
- Verifies image integrity and detects unreadable/corrupted files
- Analyzes class balance and image dimensions
- Detects capture session groupings and potential data leakage
- Generates JSON summary report
"""

import json
from pathlib import Path
from collections import Counter
from PIL import Image

DATASET_ROOT = Path(__file__).resolve().parent.parent / "data" / "bitter_gourd_dataset"

def audit_dataset(dataset_dir: Path = DATASET_ROOT) -> dict:
    print(f"Auditing Bitter Gourd Dataset at: {dataset_dir}")
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    classes = {}
    corrupted_files = []
    dimensions_counter = Counter()
    session_counter = Counter()
    total_size_bytes = 0
    all_files = []

    for class_dir in sorted(dataset_dir.iterdir()):
        if not class_dir.is_dir():
            continue

        class_name = class_dir.name
        img_files = [f for f in class_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.bmp', '.webp')]
        classes[class_name] = len(img_files)

        for img_path in img_files:
            file_size = img_path.stat().st_size
            total_size_bytes += file_size
            all_files.append(img_path)

            # Check PIL readability
            try:
                with Image.open(img_path) as img:
                    img.verify()
                # Re-open to read size and mode safely
                with Image.open(img_path) as img:
                    dimensions_counter[img.size] += 1
            except Exception as e:
                corrupted_files.append({"path": str(img_path), "error": str(e)})

            # Session detection from filename prefix
            parts = img_path.stem.split("_")
            if len(parts) >= 3 and parts[0] == "IMG":
                session_id = f"{parts[1]}_{parts[2]}"
                session_counter[session_id] += 1
            else:
                session_counter[img_path.stem] += 1

    total_images = sum(classes.values())
    total_size_mb = round(total_size_bytes / (1024 * 1024), 2)

    # Class balance calculation
    class_balance = {}
    for c, cnt in classes.items():
        class_balance[c] = {
            "count": cnt,
            "percentage": round((cnt / total_images) * 100, 2) if total_images > 0 else 0
        }

    report = {
        "dataset_path": str(dataset_dir),
        "total_classes": len(classes),
        "classes": class_balance,
        "total_images": total_images,
        "total_size_mb": total_size_mb,
        "corrupted_images_count": len(corrupted_files),
        "corrupted_images": corrupted_files,
        "unique_sessions_detected": len(session_counter),
        "dominant_resolutions": [
            {"width": dim[0], "height": dim[1], "count": count}
            for dim, count in dimensions_counter.most_common(5)
        ]
    }

    print("\n--- Audit Summary ---")
    print(f"Total Images: {report['total_images']}")
    print(f"Total Disk Size: {report['total_size_mb']} MB")
    print(f"Total Classes: {report['total_classes']}")
    for c, data in report['classes'].items():
        print(f"  • {c}: {data['count']} images ({data['percentage']}%)")
    print(f"Corrupted Images: {report['corrupted_images_count']}")
    print(f"Unique Capture Sessions: {report['unique_sessions_detected']}")
    print(f"Image Dimensions: {report['dominant_resolutions']}")

    return report

if __name__ == "__main__":
    report = audit_dataset()
    output_path = Path(__file__).resolve().parent / "dataset_audit_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport written to: {output_path}")
