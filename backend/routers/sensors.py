"""GET /api/sensors — current environmental IoT sensor readings."""

from datetime import datetime, timezone
from fastapi import APIRouter
from data.mock_data import LATEST_DETECTION
from models.schemas import SensorResponse

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


@router.get("", response_model=SensorResponse)
async def get_sensor_data():
    """Return current IoT sensor readings."""
    env = LATEST_DETECTION.environmental_data
    return SensorResponse(
        temperature_celsius=env.temperature_celsius,
        humidity_percentage=env.humidity_percentage,
        soil_moisture_percentage=env.soil_moisture_percentage,
        light_intensity_lux=env.light_intensity_lux,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
