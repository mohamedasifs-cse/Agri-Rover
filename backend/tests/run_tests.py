"""
AgriRover Standalone Automated Test Runner (Python unittest)
===========================================================
"""

import sys
import unittest
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))
CAM_DIR = BACKEND_ROOT.parent / "raspberry_pi_camera"
sys.path.insert(0, str(CAM_DIR))

from fastapi.testclient import TestClient
from main import app
from services.prediction_service import prediction_service
from camera_manager import CameraManager
from PIL import Image
import io

client = TestClient(app)


class TestAgriRoverIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        prediction_service.load_model()

    def test_01_root_endpoint(self):
        res = client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["app"], "AgriRover API")
        self.assertIn("predict", data["endpoints"])

    def test_02_health_endpoint(self):
        res = client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")

    def test_03_sensors_endpoint(self):
        res = client.get("/api/sensors")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("temperature_celsius", data)

    def test_04_farm_grid_endpoint(self):
        res = client.get("/api/farm/grid")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_cells"], 0)

    def test_05_predict_missing_file_rejected(self):
        res = client.post("/api/predict")
        self.assertEqual(res.status_code, 400)
        self.assertIn("No image provided", res.json()["detail"])

    def test_06_predict_corrupt_file_rejected(self):
        res = client.post(
            "/api/predict",
            files={"file": ("corrupt.jpg", b"INVALID_HEADER_" * 20, "image/jpeg")},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unreadable", res.json()["detail"])

    def test_07_predict_tiny_image_rejected(self):
        img = Image.new("RGB", (16, 16), color=(0, 255, 0))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        res = client.post(
            "/api/predict",
            files={"file": ("tiny.jpg", buf.getvalue(), "image/jpeg")},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("dimensions", res.json()["detail"])

    def test_08_predict_real_dataset_sample(self):
        dataset_dir = BACKEND_ROOT / "data" / "bitter_gourd_dataset"
        samples = list(dataset_dir.glob("*/*.jpeg"))
        self.assertTrue(len(samples) > 0, "No dataset sample found")

        with open(samples[0], "rb") as f:
            img_bytes = f.read()

        res = client.post(
            "/api/predict",
            files={"file": (samples[0].name, img_bytes, "image/jpeg")},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("predicted_class", data)
        self.assertIn(data["predicted_class"], ["bunchy_top", "downy_mildew", "healthy", "viral_symptoms"])
        self.assertGreaterEqual(data["confidence"], 0.0)
        self.assertLessEqual(data["confidence"], 1.0)
        self.assertEqual(len(data["top_predictions"]), 3)
        self.assertIn("recommended_action", data)
        self.assertIn("recommendations", data)
        self.assertGreater(data["processing_time_ms"], 0)
        print(f"\n[TEST PASS] Predicted: {data['disease_label']} ({data['confidence_percentage']}%) in {data['processing_time_ms']}ms")

    def test_09_predict_base64_endpoint(self):
        dataset_dir = BACKEND_ROOT / "data" / "bitter_gourd_dataset"
        samples = list(dataset_dir.glob("*/*.jpeg"))
        self.assertTrue(len(samples) > 0)
        with open(samples[0], "rb") as f:
            raw_bytes = f.read()
        import base64
        b64 = base64.b64encode(raw_bytes).decode("ascii")

        res = client.post("/api/predict/base64", json={"image_base64": b64})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("predicted_class", data)
        self.assertIn(data["status"], ["confirmed", "low_confidence", "uncertain"])

    def test_10_flask_camera_manager_lifecycle(self):
        mgr = CameraManager(device_index=99)
        status = mgr.get_status()
        self.assertFalse(status["running"])
        self.assertFalse(status["initialized"])
        self.assertEqual(status["device_index"], 99)

    def test_11_non_plant_objects_result_in_plant_not_found(self):
        non_plants = [
            ("white_wall", Image.new("RGB", (256, 256), (250, 250, 250))),
            ("skin_tone", Image.new("RGB", (256, 256), (218, 168, 138))),
            ("blue_car", Image.new("RGB", (256, 256), (30, 90, 180))),
            ("wood_desk", Image.new("RGB", (256, 256), (133, 74, 39))),
            ("flat_green_screen", Image.new("RGB", (256, 256), (34, 139, 34))),
        ]
        for name, im in non_plants:
            buf = io.BytesIO()
            im.save(buf, format="JPEG")
            res = client.post(
                "/api/predict",
                files={"file": (f"{name}.jpg", buf.getvalue(), "image/jpeg")},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "no_plant", f"Failed for {name}")
            self.assertEqual(data["disease_label"], "Plant Not Found", f"Failed for {name}")
            self.assertEqual(data["predicted_class"], "no_plant_detected", f"Failed for {name}")
            self.assertEqual(data["confidence"], 0.0)
            combined_text = (data["recommended_action"] + " " + data["recommendations"]["disclaimer"]).lower()
            self.assertTrue("plant" in combined_text or "leaf" in combined_text)


if __name__ == "__main__":
    unittest.main()
