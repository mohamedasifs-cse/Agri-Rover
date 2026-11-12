import sys
from pathlib import Path
from PIL import Image
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))
from services.plant_verifier import verify_plant_presence

dataset_dir = Path(__file__).resolve().parent.parent / "data" / "bitter_gourd_dataset"

print("========================================")
print("1. EVALUATING REAL BITTER GOURD DATASET")
print("========================================")
passed_leaves = 0
total_leaves = 0
failed_leaves = []

for cls_dir in sorted(dataset_dir.iterdir()):
    if not cls_dir.is_dir():
        continue
    imgs = [f for f in cls_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')][:30]
    cls_passed = 0
    for img_path in imgs:
        total_leaves += 1
        with Image.open(img_path) as im:
            is_plant, reason, metrics = verify_plant_presence(im)
            if is_plant:
                cls_passed += 1
                passed_leaves += 1
            else:
                failed_leaves.append((cls_dir.name, img_path.name, reason, metrics))
    print(f"[{cls_dir.name[:25]}]: {cls_passed}/{len(imgs)} passed ({cls_passed/len(imgs)*100:.1f}%)")

print(f"\nTotal Dataset Leaf Accuracy: {passed_leaves}/{total_leaves} ({passed_leaves/total_leaves*100:.1f}%)")
if failed_leaves:
    print("Failed leaf samples:", failed_leaves[:3])

print("\n========================================")
print("2. EVALUATING NON-PLANT OBJECTS")
print("========================================")
non_plants = [
    ("White wall", Image.new("RGB", (300, 300), (245, 245, 245))),
    ("Human skin / selfie", Image.new("RGB", (300, 300), (218, 168, 138))),
    ("Brown wood / furniture", Image.new("RGB", (300, 300), (133, 74, 39))),
    ("Blue car / metal body", Image.new("RGB", (300, 300), (32, 95, 185))),
    ("Dark room / shadow", Image.new("RGB", (300, 300), (15, 15, 20))),
    ("Gray laptop / asphalt", Image.new("RGB", (300, 300), (128, 128, 130))),
    ("Red fabric / fruit", Image.new("RGB", (300, 300), (220, 35, 40))),
    ("Yellow caution tape / plastic", Image.new("RGB", (300, 300), (240, 220, 20))),
    ("Flat green screen / painted wall", Image.new("RGB", (300, 300), (34, 139, 34))),
    ("Neon green plastic cup", Image.new("RGB", (300, 300), (0, 255, 60))),
]

rejected_non_plants = 0
for name, im in non_plants:
    is_plant, reason, metrics = verify_plant_presence(im)
    if not is_plant:
        rejected_non_plants += 1
        print(f" [REJECTED NON-PLANT] {name}: {reason} (plant_ratio={metrics['plant_ratio']})")
    else:
        print(f" [FAILED TO REJECT] {name}: Classified as plant! Metrics: {metrics}")

print(f"\nNon-Plant Rejection Rate: {rejected_non_plants}/{len(non_plants)} ({rejected_non_plants/len(non_plants)*100:.1f}%)")
