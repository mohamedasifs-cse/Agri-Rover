"""
AgriRover FastAPI Backend
=========================
AI-powered disease monitoring backend for bitter gourd pandal farms.

Run with:
    uvicorn main:app --reload --port 8000

API Docs:
    http://localhost:8000/docs  (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

import time
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import detections, sensors, farm, chat, predict
from models.schemas import HealthResponse
from services.prediction_service import prediction_service

# ── Startup timestamp ─────────────────────────────────────────────────────────
_start_time = time.time()


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[AgriRover] Backend starting up...")
    print("[AgriRover] Loading mock sensor and detection data...")
    # Load trained EfficientNet-B0 plant disease model once on startup
    try:
        model_loaded = prediction_service.load_model()
        if model_loaded:
            print("[AgriRover] EfficientNet-B0 Plant Disease Model loaded successfully.")
        else:
            print("[AgriRover] Plant disease model weights not found or training in progress.")
    except Exception as e:
        print(f"[AgriRover] Note: Model load deferred or failed: {e}")

    print("[AgriRover] Backend ready at http://localhost:8000")
    yield
    print("[AgriRover] Backend shutting down...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AgriRover API",
    description=(
        "AI-powered disease monitoring API for bitter gourd pandal farms. "
        "Provides disease detection results, IoT sensor data, farm grid status, "
        "and an AI assistant for farmer queries."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS ──────────────────────────────────────────────────────────────────────
_env_origins = os.getenv("ALLOWED_ORIGINS", "")
_allowed_origins = [o.strip() for o in _env_origins.split(",") if o.strip()]
if not _allowed_origins:
    _allowed_origins = [
        "http://localhost:3000",    # Next.js dev (IPv4)
        "http://localhost:3001",
        "http://localhost:8080",
        "http://127.0.0.1:3000",   # explicit IPv4
        "http://127.0.0.1:3001",
        "http://[::1]:3000",        # IPv6 loopback
        "http://[::1]:3001",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(detections.router)
app.include_router(sensors.router)
app.include_router(farm.router)
app.include_router(chat.router)
app.include_router(predict.router)


# ── Root & Health ─────────────────────────────────────────────────────────────
@app.get("/", tags=["root"])
async def root():
    return {
        "app": "AgriRover API",
        "version": "1.0.0",
        "description": "AI disease monitoring for bitter gourd pandal farms",
        "docs": "/docs",
        "phase": "Phase 3 — ML Model & Raspberry Pi Camera Integration",
        "endpoints": {
            "predict": "/api/predict",
            "detections": "/api/detections",
            "sensors": "/api/sensors",
            "farm_grid": "/api/farm/grid",
            "farm_summary": "/api/farm/summary",
            "chat": "/api/chat",
            "disease_info": "/api/farm/disease-info/{disease_class}",
            "trends": "/api/detections/trends",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(time.time() - _start_time, 2),
    )
