"""
Pydantic Schemas for Plant Disease AI Prediction API
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class CandidatePrediction(BaseModel):
    disease_class: str
    display_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_percentage: float


class PredictionRecommendations(BaseModel):
    immediate: List[str]
    preventive: List[str]
    disclaimer: str = (
        "Agricultural guidance notice: These management suggestions are based on standard "
        "cucurbit agronomy practices. For severe or persistent outbreaks, consult your local "
        "agricultural extension officer or Krishi Vigyan Kendra before chemical application."
    )


class PredictionResponse(BaseModel):
    predicted_class: str
    disease_label: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_percentage: float
    status: Literal["confirmed", "low_confidence", "uncertain", "no_plant"]
    is_healthy: bool
    top_predictions: List[CandidatePrediction]
    recommended_action: str
    recommendations: Optional[PredictionRecommendations] = None
    processing_time_ms: float
    image_metadata: Dict[str, Any]
    model_version: str = "EfficientNet-B0-Transfer"
