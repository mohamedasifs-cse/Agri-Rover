from datetime import datetime, timezone
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ── Disease & Severity Enums ──────────────────────────────────────────────────

DiseaseClass = Literal[
    "healthy",
    "powdery_mildew",
    "downy_mildew",
    "fungal_leaf_spot",
    "viral_symptoms",
    "pest_damage",
    "bunchy_top",
]

SeverityClass = Literal["healthy", "early", "moderate", "severe"]


# ── Sub-models ────────────────────────────────────────────────────────────────

class RoverLocation(BaseModel):
    row: int
    section: str
    distance_from_start_meters: float


class DetectionResultPayload(BaseModel):
    image_path: str
    disease_class: DiseaseClass
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity_class: SeverityClass
    affected_area_percentage: float = Field(..., ge=0.0, le=100.0)
    symptoms_detected: List[str]


class EnvironmentalData(BaseModel):
    temperature_celsius: float
    humidity_percentage: float
    soil_moisture_percentage: float
    light_intensity_lux: float


# ── Top-level Detection ───────────────────────────────────────────────────────

class Detection(BaseModel):
    id: str
    timestamp: str
    rover_location: RoverLocation
    detection_result: DetectionResultPayload
    environmental_data: EnvironmentalData


class DetectionsResponse(BaseModel):
    latest: Detection
    history: List[Detection]
    total: int


# ── Sensor Data ───────────────────────────────────────────────────────────────

class SensorResponse(BaseModel):
    temperature_celsius: float
    humidity_percentage: float
    soil_moisture_percentage: float
    light_intensity_lux: float
    updated_at: str


# ── Farm Grid ─────────────────────────────────────────────────────────────────

class FarmCell(BaseModel):
    row: int
    col: int
    section: str
    status: Literal["healthy", "attention", "diseased"]
    disease_class: DiseaseClass
    severity: SeverityClass
    last_checked: str
    detection_id: Optional[str] = None


class FarmGridResponse(BaseModel):
    cells: List[FarmCell]
    total_cells: int
    healthy_count: int
    attention_count: int
    diseased_count: int
    healthy_pct: float
    attention_pct: float
    diseased_pct: float
    rows: int
    sections: List[str]


# ── Disease Info ──────────────────────────────────────────────────────────────

class Recommendations(BaseModel):
    immediate: List[str]
    preventive: List[str]


class DiseaseInfo(BaseModel):
    disease_class: DiseaseClass
    display_name: str
    scientific_name: str
    description: str
    symptoms: List[str]
    causes: List[str]
    recommendations: Recommendations
    farmer_summary: str


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    context_used: str  # e.g. "latest_detection", "weather", "general"


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    uptime_seconds: float


# ── ML Inference (Phase 3) ────────────────────────────────────────────────────

class InferenceRequest(BaseModel):
    """Used when the rover sends an image for disease detection."""
    image_base64: str
    rover_location: RoverLocation
    environmental_data: EnvironmentalData


class InferenceResponse(BaseModel):
    detection: Detection
    processing_time_ms: float
