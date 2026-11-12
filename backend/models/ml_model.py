"""
Stub for Phase 3 ML model integration.
Replace this file with TensorFlow Lite or ONNX Runtime inference.
"""

# ── Phase 3 Implementation Guide ──────────────────────────────────────────────
#
# 1. TensorFlow Lite:
#    pip install tflite-runtime
#
#    import tflite_runtime.interpreter as tflite
#    import numpy as np
#    from PIL import Image
#
#    def load_model(model_path: str):
#        interpreter = tflite.Interpreter(model_path=model_path)
#        interpreter.allocate_tensors()
#        return interpreter
#
#    def predict(interpreter, image_bytes: bytes) -> dict:
#        img = Image.open(io.BytesIO(image_bytes)).resize((224, 224))
#        input_data = np.expand_dims(np.array(img, dtype=np.float32) / 255.0, axis=0)
#        interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_data)
#        interpreter.invoke()
#        output = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])
#        class_idx = np.argmax(output[0])
#        confidence = float(output[0][class_idx])
#        return {"class_idx": class_idx, "confidence": confidence}
#
# 2. ONNX Runtime:
#    pip install onnxruntime
#
#    import onnxruntime as ort
#    session = ort.InferenceSession("weights/disease_model.onnx")
#    ...
#
# 3. Disease class mapping (output_idx → disease_class):
#    DISEASE_CLASSES = [
#        "healthy", "powdery_mildew", "downy_mildew",
#        "fungal_leaf_spot", "viral_symptoms", "pest_damage"
#    ]

DISEASE_CLASSES = [
    "healthy",
    "powdery_mildew",
    "downy_mildew",
    "fungal_leaf_spot",
    "viral_symptoms",
    "pest_damage",
]

SEVERITY_THRESHOLDS = {
    "healthy": (0, 0),
    "early": (1, 20),
    "moderate": (21, 60),
    "severe": (61, 100),
}


def classify_severity(affected_area_percentage: float) -> str:
    """Classify severity from affected area percentage."""
    if affected_area_percentage == 0:
        return "healthy"
    elif affected_area_percentage <= 20:
        return "early"
    elif affected_area_percentage <= 60:
        return "moderate"
    else:
        return "severe"


# Placeholder — will call actual model in Phase 3
async def run_inference(image_bytes: bytes) -> dict:
    """
    Phase 3: Run disease detection model on image bytes.
    Returns detection result dict matching DetectionResultPayload schema.
    """
    raise NotImplementedError(
        "ML model inference not yet integrated. "
        "See Phase 3 implementation guide in this file."
    )
