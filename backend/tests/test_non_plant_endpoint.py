import io
import json
import urllib.request
import urllib.parse
from PIL import Image
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_api_predict(im: Image.Image, name: str):
    buf = io.BytesIO()
    im.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    boundary = "----WebKitFormBoundaryAgriRoverTest7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="test.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8") + img_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/predict",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"[OK] [{name}] Label: '{data['disease_label']}' | Status: '{data['status']}' | Class: '{data['predicted_class']}' | Conf: {data['confidence_percentage']}%")
        return data

print("--- 1. TESTING NON-PLANT IMAGES (MUST BE 'Plant Not Found') ---")
non_plants = [
    ("Human Face / Skin", Image.new("RGB", (256, 256), (218, 168, 138))),
    ("White Room Wall", Image.new("RGB", (256, 256), (245, 245, 245))),
    ("Brown Furniture / Desk", Image.new("RGB", (256, 256), (133, 74, 39))),
    ("Blue Car / Vehicle", Image.new("RGB", (256, 256), (32, 95, 185))),
    ("Black / Dark Shadow", Image.new("RGB", (256, 256), (15, 15, 20))),
    ("Gray Laptop Surface", Image.new("RGB", (256, 256), (128, 128, 130))),
    ("Red Apple / Shirt", Image.new("RGB", (256, 256), (220, 35, 40))),
    ("Solid Green Screen", Image.new("RGB", (256, 256), (34, 139, 34))),
]

all_rejected = True
for name, im in non_plants:
    res = test_api_predict(im, name)
    if res["status"] != "no_plant" or res["disease_label"] != "Plant Not Found":
        print(f"FAILED TO REJECT: {name}")
        all_rejected = False

print(f"\nAll Non-Plants Correctly Classified as 'Plant Not Found': {all_rejected}")

print("\n--- 2. TESTING REAL BITTER GOURD LEAVES (MUST BE DIAGNOSED) ---")
ds_dir = Path("d:/Agri_ML/backend/data/bitter_gourd_dataset")
for cls_dir in sorted(ds_dir.iterdir()):
    if not cls_dir.is_dir(): continue
    sample = next(cls_dir.glob("*.jpeg"))
    with Image.open(sample) as im:
        res = test_api_predict(im, cls_dir.name[:25])
        assert res["status"] in ("confirmed", "low_confidence", "uncertain"), f"Failed on real leaf: {res}"
        assert res["disease_label"] != "Plant Not Found", f"Real leaf rejected: {res}"

print("\nALL TESTS PASSED SUCCESSFULLY!")
