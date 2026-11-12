"""
AgriRover AI Prediction Service
===============================
Loads the trained PyTorch EfficientNet-B0 model once on startup and performs
low-latency inference with image validation, calibrated confidence thresholds,
top candidate rankings, and agronomic management guidance.
"""

import io
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models

from services.disease_service import get_disease_info
from services.plant_verifier import verify_plant_presence

logger = logging.getLogger("AgriRoverPredictionService")

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "plant_disease"
MODEL_WEIGHTS_PATH = MODELS_DIR / "best_model.pth"
CLASS_MAPPING_PATH = MODELS_DIR / "class_mapping.json"
MODEL_CONFIG_PATH = MODELS_DIR / "model_config.json"


class PredictionService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[nn.Module] = None
        self.class_mapping: Optional[Dict] = None
        self.model_config: Optional[Dict] = None
        self.idx_to_class: Dict[int, str] = {}
        self.display_names: Dict[str, str] = {}
        self.num_classes: int = 4
        self.confidence_threshold: float = 0.60
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor],  # Will fix syntax
        )

    def load_model(self) -> bool:
        """Load trained model once into memory."""
        if self.model is not None:
            return True

        if not MODEL_WEIGHTS_PATH.exists():
            logger.warning(f"Model weights not found at {MODEL_WEIGHTS_PATH}. Prediction service idle.")
            return False

        try:
            with open(CLASS_MAPPING_PATH, "r", encoding="utf-8") as f:
                self.class_mapping = json.load(f)

            if MODEL_CONFIG_PATH.exists():
                with open(MODEL_CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.model_config = json.load(f)
                    self.confidence_threshold = self.model_config.get("confidence_threshold", 0.60)

            self.num_classes = self.class_mapping.get("num_classes", 4)
            self.idx_to_class = {int(k): v for k, v in self.class_mapping.get("idx_to_class", {}).items()}
            self.display_names = self.class_mapping.get("display_names", {})

            # Build EfficientNet-B0 architecture
            weights = models.EfficientNet_B0_Weights.DEFAULT
            model = models.efficientnet_b0(weights=weights)
            in_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.3, inplace=True),
                nn.Linear(in_features, self.num_classes)
            )

            # Load checkpoint
            state_dict = torch.load(MODEL_WEIGHTS_PATH, map_location=self.device, weights_only=True)
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()

            self.model = model
            logger.info(f"Loaded trained plant disease model successfully ({self.num_classes} classes on {self.device}).")
            return True
        except Exception as e:
            logger.error(f"Failed to load plant disease model: {e}")
            return False

    def predict_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Validate input image bytes, preprocess, and execute inference."""
        t_start = time.perf_counter()

        # 1. Validate image size
        size_kb = len(image_bytes) / 1024.0
        if len(image_bytes) < 100:
            raise ValueError("Uploaded file is too small or empty.")
        if len(image_bytes) > 15 * 1024 * 1024:
            raise ValueError("Uploaded image exceeds the 15 MB size limit.")

        # 2. Validate image readability and format
        try:
            with Image.open(io.BytesIO(image_bytes)) as pil_img:
                img_format = (pil_img.format or "JPEG").upper()
                width, height = pil_img.size
                if width < 32 or height < 32:
                    raise ValueError(f"Image dimensions ({width}x{height}) are too small for diagnosis.")
                rgb_img = pil_img.convert("RGB")
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Unreadable or unsupported image format. Please submit JPEG, PNG, or WEBP. ({e})")

        # 2b. Botanical Plant Guardrail Verification
        # Validates that the uploaded or captured image actually contains plant foliage / bitter gourd leaves
        is_plant, rejection_reason, botanical_metrics = verify_plant_presence(rgb_img)
        if not is_plant:
            elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
            logger.info(f"Non-plant object rejected: {rejection_reason} (metrics={botanical_metrics})")
            return {
                "predicted_class": "no_plant_detected",
                "disease_label": "Plant Not Found",
                "confidence": 0.0,
                "confidence_percentage": 0.0,
                "status": "no_plant",
                "is_healthy": False,
                "top_predictions": [],
                "recommended_action": rejection_reason,
                "recommendations": {
                    "immediate": [
                        "Point the camera directly at plant leaves or vine foliage.",
                        "Ensure adequate sunlight or field lighting — avoid dark shadows.",
                        "Hold the camera 15 to 40 cm from the crop foliage for clear focal clarity."
                    ],
                    "preventive": [
                        "Keep the rover camera lens clean of dust, mud, and water droplets.",
                        "Align the camera angle on the rover to point towards the bitter gourd pandal trellises."
                    ],
                    "disclaimer": "Diagnostic Notice: The vision system did not detect plant or leaf tissue in this frame. Only agricultural plant foliage is analyzed."
                },
                "processing_time_ms": elapsed_ms,
                "image_metadata": {
                    "width": width,
                    "height": height,
                    "format": img_format,
                    "size_kb": round(size_kb, 1),
                    "botanical_metrics": botanical_metrics,
                },
                "model_version": "EfficientNet-B0-Robust-BotanicalGuard",
            }

        # Ensure model is loaded
        if self.model is None:
            loaded = self.load_model()
            if not loaded or self.model is None:
                raise RuntimeError("AI model is currently unavailable or training is in progress.")

        # 3. Multi-Scale & Multi-Crop Preprocessing for Field Robustness
        t_full = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        t_center = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        views = [t_full(rgb_img), t_center(rgb_img)]

        # If image is high-resolution or rectangular, extract quadrant crops to catch edge lesions
        if width > 300 or height > 300:
            w_half, h_half = width // 2, height // 2
            crops = [
                rgb_img.crop((0, 0, w_half + 40, h_half + 40)),
                rgb_img.crop((w_half - 40, 0, width, h_half + 40)),
                rgb_img.crop((0, h_half - 40, w_half + 40, height)),
                rgb_img.crop((w_half - 40, h_half - 40, width, height)),
            ]
            for c in crops:
                views.append(t_full(c))

        batch = torch.stack(views).to(self.device)

        # 4. Multi-View Model Inference
        with torch.no_grad():
            logits = self.model(batch)
            view_probs = torch.softmax(logits, dim=1)

        # Compute average view probabilities and maximum lesion activations
        avg_probs = view_probs.mean(dim=0)
        max_probs = view_probs.max(dim=0).values

        # In plant pathology, if ANY view/crop exhibits strong localized disease symptoms,
        # prioritize the disease lesion over surrounding healthy leaf tissue.
        disease_indices = [idx for idx, name in self.idx_to_class.items() if name != "healthy"]
        best_disease_idx = max(disease_indices, key=lambda i: max_probs[i].item())
        best_disease_prob = max_probs[best_disease_idx].item()

        healthy_idx = None
        for idx, name in self.idx_to_class.items():
            if name == "healthy":
                healthy_idx = idx
                break

        # If any crop shows strong disease indicators (> 0.40), use disease lesion activation
        if best_disease_prob >= 0.40 and (healthy_idx is None or best_disease_prob >= avg_probs[healthy_idx].item() * 0.85):
            # Combined probability vector highlighting detected disease
            final_probs = max_probs.clone()
            final_probs = final_probs / final_probs.sum()
        else:
            final_probs = avg_probs

        # 5. Extract top candidates
        top_k = min(3, self.num_classes)
        top_probs, top_indices = torch.topk(final_probs, k=top_k)

        top_candidates = []
        for p, idx in zip(top_probs, top_indices):
            cls_name = self.idx_to_class.get(idx.item(), f"class_{idx.item()}")
            disp_name = self.display_names.get(cls_name, cls_name.replace("_", " ").title())
            top_candidates.append({
                "disease_class": cls_name,
                "display_name": disp_name,
                "confidence": round(p.item(), 4),
                "confidence_percentage": round(p.item() * 100.0, 1),
            })

        best = top_candidates[0]
        top_class = best["disease_class"]
        top_confidence = best["confidence"]

        # 6. Status and uncertainty calibration
        if top_confidence >= 0.70:
            status = "confirmed"
            display_label = best["display_name"]
            is_healthy = (top_class == "healthy")
            recommended_action = (
                "Healthy bitter gourd vine — continue regular pandal maintenance and nutrition schedule."
                if is_healthy
                else f"Diagnosis confirmed: {best['display_name']}. Review immediate agronomy actions below."
            )
        elif top_confidence >= 0.48:
            status = "low_confidence"
            display_label = f"Likely {best['display_name']} (Moderate Confidence)"
            is_healthy = (top_class == "healthy")
            recommended_action = (
                f"Signs match {best['display_name']} ({best['confidence_percentage']}%), but confidence is moderate. "
                "Inspect the leaf underside for fuzzy growth or crop closely to the diseased spot and re-scan."
            )
        else:
            status = "uncertain"
            display_label = f"Unconfirmed — Possible {best['display_name']}"
            is_healthy = False
            recommended_action = (
                f"Confidence is low ({best['confidence_percentage']}%). The photograph may differ in lighting or camera angle from the pandal dataset. "
                "Please zoom in on the affected yellow/brown leaf spots and re-scan for confirmation."
            )

        # 7. Agronomy recommendations
        target_info_class = top_class if top_class in ("downy_mildew", "viral_symptoms", "bunchy_top", "healthy") else "healthy"
        disease_info = get_disease_info(target_info_class)
        recs = disease_info.get("recommendations", {})

        elapsed_ms = round((time.perf_counter() - t_start) * 1000.0, 2)

        return {
            "predicted_class": top_class,
            "disease_label": display_label,
            "confidence": top_confidence,
            "confidence_percentage": best["confidence_percentage"],
            "status": status,
            "is_healthy": is_healthy,
            "top_predictions": top_candidates,
            "recommended_action": recommended_action,
            "recommendations": {
                "immediate": recs.get("immediate", []),
                "preventive": recs.get("preventive", []),
                "disclaimer": (
                    "Agricultural guidance notice: These management suggestions are based on standard "
                    "cucurbit agronomy practices. For severe or persistent outbreaks, consult your local "
                    "agricultural extension officer or Krishi Vigyan Kendra before chemical application."
                ),
            },
            "processing_time_ms": elapsed_ms,
            "image_metadata": {
                "width": width,
                "height": height,
                "format": img_format,
                "size_kb": round(size_kb, 1),
            },
            "model_version": "EfficientNet-B0-Robust-MultiView",
        }


# Singleton instance
prediction_service = PredictionService()
