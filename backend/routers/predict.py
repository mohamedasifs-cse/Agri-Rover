"""
FastAPI Router for Plant Disease AI Prediction
==============================================
Endpoint: POST /api/predict
Accepts: multipart/form-data with file upload, or raw image bytes.
"""

import base64
import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel

from models.prediction_schemas import PredictionResponse
from services.prediction_service import prediction_service

logger = logging.getLogger("AgriRoverPredictRouter")

router = APIRouter(prefix="/api/predict", tags=["prediction"])


class Base64PredictRequest(BaseModel):
    image_base64: str
    metadata: Optional[dict] = None


@router.post("", response_model=PredictionResponse)
async def predict_image(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
):
    """
    Run EfficientNet-B0 plant disease diagnosis on an uploaded photo
    or webcam snapshot.
    """
    image_bytes = None

    if file is not None:
        try:
            image_bytes = await file.read()
        except Exception as e:
            logger.error(f"Failed reading uploaded file: {e}")
            raise HTTPException(status_code=400, detail="Failed to read uploaded image.")
    elif image_base64:
        try:
            # Strip data URL prefix if present (e.g. data:image/jpeg;base64,...)
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid base64 encoded image string.")
    else:
        raise HTTPException(
            status_code=400,
            detail="No image provided. Please upload a file as 'file' or provide 'image_base64'."
        )

    try:
        result = prediction_service.predict_image(image_bytes)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        logger.exception("Unexpected error during image prediction")
        raise HTTPException(status_code=500, detail="An error occurred while analyzing the image.")


@router.post("/base64", response_model=PredictionResponse)
async def predict_image_json(payload: Base64PredictRequest):
    """Alternative JSON endpoint accepting base64 image data."""
    try:
        raw_b64 = payload.image_base64
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",", 1)[1]
        image_bytes = base64.b64decode(raw_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image string.")

    try:
        result = prediction_service.predict_image(image_bytes)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        logger.exception("Unexpected error during base64 image prediction")
        raise HTTPException(status_code=500, detail="An error occurred while analyzing the image.")
