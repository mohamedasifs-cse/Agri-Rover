"""GET /api/detections — returns latest and historical detection data."""

from fastapi import APIRouter
from data.mock_data import LATEST_DETECTION, HISTORICAL_DETECTIONS, TREND_DATA, DISEASE_DISTRIBUTION
from models.schemas import DetectionsResponse

router = APIRouter(prefix="/api/detections", tags=["detections"])


@router.get("", response_model=DetectionsResponse)
async def get_detections():
    """Return the latest detection and full historical list."""
    return DetectionsResponse(
        latest=LATEST_DETECTION,
        history=HISTORICAL_DETECTIONS,
        total=len(HISTORICAL_DETECTIONS),
    )


@router.get("/latest")
async def get_latest_detection():
    """Return only the most recent detection."""
    return LATEST_DETECTION


@router.get("/trends")
async def get_trends():
    """Return 14-day trend data for charts."""
    return {
        "trend_data": TREND_DATA,
        "disease_distribution": DISEASE_DISTRIBUTION,
    }


@router.get("/{detection_id}")
async def get_detection_by_id(detection_id: str):
    """Return a single detection by ID."""
    for det in HISTORICAL_DETECTIONS:
        if det.id == detection_id:
            return det
    return {"error": "Detection not found", "id": detection_id}
