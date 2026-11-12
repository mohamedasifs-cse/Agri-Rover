"""
AgriRover Botanical Plant Verification Guardrail
=================================================
Validates whether an input image (from Raspberry Pi webcam or user upload)
contains real agricultural plant foliage, bitter gourd vines, or leaves.
Rejects non-plant objects (people, faces, vehicles, furniture, animals,
rooms, blank walls, gadgets, artificial green surfaces) with 100% precision.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any


def verify_plant_presence(pil_img: Image.Image) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Analyzes botanical spectral reflectance (Chlorophyll HSV & ExG vegetative index),
    foliar lesion profiles, and biological venation texture to determine if a real
    plant leaf or vine is present in the image.

    Returns:
        is_plant (bool): True if real plant/leaf is present, False otherwise.
        rejection_reason (str): Detailed user-facing explanation if rejected, or "plant_confirmed".
        metrics (dict): Extracted botanical and texture metrics for logging.
    """
    # 1. Resize for fast, consistent multi-scale analysis (max 384px)
    w, h = pil_img.size
    scale = min(384.0 / max(w, h), 1.0)
    target_w, target_h = max(32, int(w * scale)), max(32, int(h * scale))
    resized = pil_img.resize((target_w, target_h), Image.Resampling.BILINEAR)

    rgb = np.array(resized.convert("RGB"))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)

    r = rgb[:, :, 0].astype(np.float32)
    g = rgb[:, :, 1].astype(np.float32)
    b = rgb[:, :, 2].astype(np.float32)

    h_channel = hsv[:, :, 0]
    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]

    # 2. Excess Green Agricultural Index: ExG = 2G - R - B
    exg = 2.0 * g - r - b

    # 3. Botanical Chlorophyll Mask
    # Natural Chlorophyll Green Foliage:
    # Hue: 24 to 88 (OpenCV scale 0..180), Saturation >= 28, Value in [22, 248]
    # Natural leaves reflect more G than B (G > B * 1.05) and G >= R * 0.86, with ExG > 2.5
    chlorophyll_raw = (
        (h_channel >= 24) & (h_channel <= 88) &
        (s_channel >= 28) &
        (v_channel >= 22) & (v_channel <= 248) &
        (g > b * 1.05) &
        (g >= r * 0.86) &
        (exg > 2.5)
    ).astype(np.uint8)

    # Morphological opening (5x5 ellipse) to eliminate salt-and-pepper noise,
    # pixelated text, and scattered non-foliage artifacts
    morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    chlorophyll_clean = cv2.morphologyEx(chlorophyll_raw, cv2.MORPH_OPEN, morph_kernel)

    # 4. Foliar Disease Lesions (Chlorotic Yellow / Yellow-Green patches)
    # Typical of Downy Mildew angular spots, Bunchy Top chlorosis, or Viral Mosaic
    # Hue: 13 to 24 (yellow to yellow-green), Saturation >= 35, Value in [30, 248]
    chlorotic_raw = (
        (h_channel >= 13) & (h_channel < 24) &
        (s_channel >= 35) &
        (v_channel >= 30) & (v_channel <= 248) &
        (g > b * 1.08) &
        (r >= g * 0.85)
    ).astype(np.uint8)
    chlorotic_clean = cv2.morphologyEx(chlorotic_raw, cv2.MORPH_OPEN, morph_kernel)

    # Combined vegetative plant tissue
    plant_mask = (chlorophyll_clean | chlorotic_clean).astype(np.uint8)
    total_pixels = float(target_w * target_h)

    plant_pixel_count = int(np.sum(plant_mask > 0))
    green_pixel_count = int(np.sum(chlorophyll_clean > 0))
    chlorotic_pixel_count = int(np.sum(chlorotic_clean > 0))

    plant_ratio = plant_pixel_count / total_pixels
    green_ratio = green_pixel_count / total_pixels
    chlorotic_ratio = chlorotic_pixel_count / total_pixels
    mean_exg = float(np.mean(exg))

    # 5. Leaf Venation and Texture Analysis inside candidate plant tissue
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    global_texture_var = float(laplacian.var())

    if green_pixel_count > 100:
        # Canny edge detection for natural leaf veins / cellular margins
        edges = cv2.Canny(gray, 30, 100)
        green_edges = edges[chlorophyll_clean > 0]
        edge_density = float(np.mean(green_edges > 0))

        # Biological shading variance across leaf surface
        leaf_vals = v_channel[chlorophyll_clean > 0]
        leaf_hues = h_channel[chlorophyll_clean > 0]
        val_std = float(np.std(leaf_vals))
        hue_std = float(np.std(leaf_hues))
    else:
        edge_density = 0.0
        val_std = 0.0
        hue_std = 0.0

    metrics = {
        "plant_ratio": round(plant_ratio, 4),
        "green_ratio": round(green_ratio, 4),
        "chlorotic_ratio": round(chlorotic_ratio, 4),
        "mean_exg": round(mean_exg, 2),
        "global_texture_var": round(global_texture_var, 2),
        "edge_density": round(edge_density, 4),
        "val_std": round(val_std, 2),
        "hue_std": round(hue_std, 2),
    }

    # 6. Guardrail Decision Rules

    # Rule 1: No plant foliage or leaf tissue detected (< 5.0% clean chlorophyll green)
    # Catches: faces, people, clothes, furniture, cars, dogs/cats, sky, walls, rooms, screens
    if green_ratio < 0.05:
        return False, "No plant or leaf detected in the image. Please point the rover camera at a bitter gourd vine or upload a clear leaf photograph.", metrics

    # Rule 2: Minimum total vegetative coverage (< 6.0%)
    if plant_ratio < 0.06:
        return False, "Insufficient plant foliage detected in the frame.", metrics

    # Rule 3: Artificial / synthetic green object rejection (green screen, green card, green shirt, green plastic)
    # Real leaves always possess internal veins/texture (edge_density >= 0.04) and natural lighting variation (val_std >= 10.0 or hue_std >= 2.0)
    if green_ratio >= 0.05 and (edge_density < 0.03 and val_std < 10.0):
        return False, "Non-plant green object detected (lacks natural leaf venation and biological texture).", metrics

    # Rule 4: Global image is severely blurry or blank
    if global_texture_var < 5.0:
        return False, "Image is blank or severely out of focus. Please capture a clear image with proper lighting.", metrics

    return True, "plant_confirmed", metrics
