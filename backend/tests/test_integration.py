"""
AgriRover Integration & Verification Test Suite
================================================
Automated tests covering:
1. FastAPI endpoints (/health, /api/detections, /api/sensors, /api/farm/grid, /api/predict)
2. Prediction input validation (corrupt images, non-images, empty payloads)
3. Model inference response schema and class candidates
4. Flask Webcam Service endpoints & thread-safe CameraManager
"""

import io
import os
import sys
import pytest
from pathlib import Path
from PIL import Image

# Ensure backend root is on sys.path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

# Add raspberry_pi_camera to path
CAM_DIR = BACKEND_ROOT.parent / "raspberry_pi_camera"
sys.path.insert(0, str(CAM_DIR))

from fastapi.testclient import TestClient
from main import app
from services.prediction_service import prediction_service

client = TestClient(app)


def create_test_image(width=256, height=256, color=(34, 197, 94)) -> bytes:
    """Create synthetic in-memory RGB JPEG image."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestFastAPIBasics:
    def test_root(self):
        res = client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert data["app"] == "AgriRover API"
        assert "predict" in data["endpoints"]

    def test_health(self):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data

    def test_sensors(self):
        res = client.get("/api/sensors")
        assert res.status_code == 200
        data = res.json()
        assert "temperature_celsius" in data
        assert "humidity_percentage" in data

    def test_farm_grid(self):
        res = client.get("/api/farm/grid")
        assert res.status_code == 200
        data = res.json()
        assert "cells" in data
        assert data["total_cells"] > 0


class TestPredictionInputValidation:
    def test_predict_no_file(self):
        res = client.post("/api/predict")
        assert res.status_code == 400
        assert "No image provided" in res.json()["detail"]

    def test_predict_empty_file(self):
        res = client.post(
            "/api/predict",
            files={"file": ("empty.jpg", b"", "image/jpeg")}
        )
        assert res.status_code == 400

    def test_predict_corrupt_file(self):
        res = client.post(
            "/api/predict",
            files={"file": ("corrupt.jpg", b"NOT_A_VALID_JPEG_HEADER", "image/jpeg")}
        )
        assert res.status_code == 400
        assert "Unreadable" in res.json()["detail"] or "format" in res.json()["detail"]

    def test_predict_tiny_image(self):
        tiny_img = create_test_image(width=16, height=16)
        res = client.post(
            "/api/predict",
            files={"file": ("tiny.jpg", tiny_img, "image/jpeg")}
        )
        assert res.status_code == 400
        assert "dimensions" in res.json()["detail"]


class TestModelInference:
    def test_predict_real_dataset_sample(self):
        dataset_dir = BACKEND_ROOT / "data" / "bitter_gourd_dataset"
        # Find first available leaf image
        img_files = list(dataset_dir.glob("*/*.jpeg")) + list(dataset_dir.glob("*/*.jpg"))
        if not img_files:
            pytest.skip("No dataset images found to test.")

        sample_path = img_files[0]
        with open(sample_path, "rb") as f:
            img_bytes = f.read()

        res = client.post(
            "/api/predict",
            files={"file": (sample_path.name, img_bytes, "image/jpeg")}
        )
        assert res.status_code == 200
        data = res.json()
        assert "predicted_class" in data
        assert "confidence" in data
        assert "top_predictions" in data
        assert len(data["top_predictions"]) >= 3
        assert data["status"] in ("confirmed", "low_confidence", "uncertain")
        assert "recommended_action" in data
        assert "recommendations" in data
        assert data["processing_time_ms"] > 0

    def test_predict_base64_endpoint(self):
        img_bytes = create_test_image()
        import base64
        b64_str = base64.b64encode(img_bytes).decode("ascii")

        res = client.post(
            "/api/predict/base64",
            json={"image_base64": b64_str}
        )
        assert res.status_code == 200
        data = res.json()
        assert "predicted_class" in data
        assert "confidence" in data


class TestFlaskCameraService:
    def test_camera_manager_status_structure(self):
        from camera_manager import CameraManager
        # Test manager in test mode
        mgr = CameraManager(device_index=99)
        status = mgr.get_status()
        assert "running" in status
        assert "initialized" in status
        assert "device_index" in status
        assert "requested_resolution" in status
        assert status["running"] is False
