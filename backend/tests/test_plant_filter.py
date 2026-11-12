import cv2
import numpy as np
from pathlib import Path
from PIL import Image

def analyze_plant_features(pil_img: Image.Image):
    rgb = np.array(pil_img.convert("RGB"))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    
    r = rgb[:, :, 0].astype(np.float32)
    g = rgb[:, :, 1].astype(np.float32)
    b = rgb[:, :, 2].astype(np.float32)
    
    # 1. Excess Green Index: ExG = 2G - R - B
    exg = 2.0 * g - r - b
    
    # 2. Plant foliage masks
    # Chlorophyll green hue in HSV (H: 25..88, S >= 28, V >= 25)
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]
    
    # Healthy & green vine foliage
    green_mask = (h >= 25) & (h <= 88) & (s >= 30) & (v >= 25) & (exg > 5)
    
    # Yellow/chlorotic/necrotic leaf disease spots (H: 14..25, S >= 40, V >= 35) with plant tone
    # For leaf lesions, G is typically > B and R is high, but not skin-toned
    chlorotic_mask = (h >= 14) & (h < 25) & (s >= 40) & (v >= 35) & (g > b * 1.1)
    
    # Total plant pixels
    plant_mask = green_mask | chlorotic_mask
    plant_ratio = np.mean(plant_mask)
    
    # Texture of the candidate plant region:
    # A flat color background has low Laplacian variance
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    return {
        "plant_ratio": float(plant_ratio),
        "green_ratio": float(np.mean(green_mask)),
        "chlorotic_ratio": float(np.mean(chlorotic_mask)),
        "laplacian_var": float(laplacian_var),
        "mean_exg": float(np.mean(exg)),
    }

# Test on 20 bitter gourd dataset images
dataset_dir = Path(__file__).resolve().parent.parent / "data" / "bitter_gourd_dataset"
print("--- TESTING DATASET IMAGES (PLANTS) ---")
for cls_dir in dataset_dir.iterdir():
    if cls_dir.is_dir():
        imgs = [f for f in cls_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')]
        for img_path in imgs[:3]:
            with Image.open(img_path) as im:
                res = analyze_plant_features(im)
                print(f"[{cls_dir.name}] {img_path.name[:20]}: plant_ratio={res['plant_ratio']:.3f}, green_ratio={res['green_ratio']:.3f}, exg={res['mean_exg']:.1f}, lap={res['laplacian_var']:.1f}")

print("\n--- TESTING SYNTHETIC NON-PLANT IMAGES ---")
# 1. Blank white
w = Image.new("RGB", (256, 256), (255, 255, 255))
print("White wall:", analyze_plant_features(w))

# 2. Skin tone (face / person)
skin = Image.new("RGB", (256, 256), (210, 160, 130))
print("Skin tone:", analyze_plant_features(skin))

# 3. Wooden table / brown furniture
wood = Image.new("RGB", (256, 256), (139, 69, 19))
print("Wood furniture:", analyze_plant_features(wood))

# 4. Blue sky / car
blue = Image.new("RGB", (256, 256), (30, 100, 200))
print("Blue car / sky:", analyze_plant_features(blue))

# 5. Black screen / dark room
dark = Image.new("RGB", (256, 256), (20, 20, 20))
print("Dark room:", analyze_plant_features(dark))

# 6. Gray concrete / laptop / electronics
gray = Image.new("RGB", (256, 256), (120, 120, 120))
print("Gray laptop / concrete:", analyze_plant_features(gray))

# 7. Red object / apple / shirt
red = Image.new("RGB", (256, 256), (200, 30, 30))
print("Red shirt / car:", analyze_plant_features(red))
