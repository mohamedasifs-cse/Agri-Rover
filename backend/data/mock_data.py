"""
Mock data for Phase 1.
Replace with real database queries in Phase 2.
"""

from models.schemas import (
    Detection, RoverLocation, DetectionResultPayload,
    EnvironmentalData, FarmCell
)

# ── Latest Detection ──────────────────────────────────────────────────────────

LATEST_DETECTION = Detection(
    id="det_001",
    timestamp="2026-09-11T14:30:00Z",
    rover_location=RoverLocation(
        row=2,
        section="B",
        distance_from_start_meters=18,
    ),
    detection_result=DetectionResultPayload(
        image_path="/images/detection_001.jpg",
        disease_class="powdery_mildew",
        confidence=0.94,
        severity_class="moderate",
        affected_area_percentage=25.0,
        symptoms_detected=["white_coating", "leaf_curling"],
    ),
    environmental_data=EnvironmentalData(
        temperature_celsius=31.0,
        humidity_percentage=78.0,
        soil_moisture_percentage=62.0,
        light_intensity_lux=720.0,
    ),
)

# ── Historical Detections ─────────────────────────────────────────────────────

HISTORICAL_DETECTIONS: list[Detection] = [
    LATEST_DETECTION,
    Detection(
        id="det_002",
        timestamp="2026-09-10T09:15:00Z",
        rover_location=RoverLocation(row=4, section="A", distance_from_start_meters=34),
        detection_result=DetectionResultPayload(
            image_path="/images/det_002.jpg",
            disease_class="downy_mildew",
            confidence=0.87,
            severity_class="early",
            affected_area_percentage=12.0,
            symptoms_detected=["yellow_spots", "brown_lesions"],
        ),
        environmental_data=EnvironmentalData(
            temperature_celsius=28.0,
            humidity_percentage=85.0,
            soil_moisture_percentage=70.0,
            light_intensity_lux=540.0,
        ),
    ),
    Detection(
        id="det_003",
        timestamp="2026-09-09T11:45:00Z",
        rover_location=RoverLocation(row=1, section="C", distance_from_start_meters=8),
        detection_result=DetectionResultPayload(
            image_path="/images/det_003.jpg",
            disease_class="healthy",
            confidence=0.98,
            severity_class="healthy",
            affected_area_percentage=0.0,
            symptoms_detected=[],
        ),
        environmental_data=EnvironmentalData(
            temperature_celsius=29.0,
            humidity_percentage=72.0,
            soil_moisture_percentage=58.0,
            light_intensity_lux=890.0,
        ),
    ),
    Detection(
        id="det_004",
        timestamp="2026-09-08T15:00:00Z",
        rover_location=RoverLocation(row=3, section="D", distance_from_start_meters=28),
        detection_result=DetectionResultPayload(
            image_path="/images/det_004.jpg",
            disease_class="fungal_leaf_spot",
            confidence=0.91,
            severity_class="severe",
            affected_area_percentage=65.0,
            symptoms_detected=["circular_lesions", "yellow_halo"],
        ),
        environmental_data=EnvironmentalData(
            temperature_celsius=33.0,
            humidity_percentage=82.0,
            soil_moisture_percentage=74.0,
            light_intensity_lux=420.0,
        ),
    ),
    Detection(
        id="det_005",
        timestamp="2026-09-07T10:20:00Z",
        rover_location=RoverLocation(row=5, section="B", distance_from_start_meters=42),
        detection_result=DetectionResultPayload(
            image_path="/images/det_005.jpg",
            disease_class="viral_symptoms",
            confidence=0.79,
            severity_class="moderate",
            affected_area_percentage=38.0,
            symptoms_detected=["mosaic_pattern", "mottle", "leaf_deformation"],
        ),
        environmental_data=EnvironmentalData(
            temperature_celsius=30.0,
            humidity_percentage=76.0,
            soil_moisture_percentage=60.0,
            light_intensity_lux=680.0,
        ),
    ),
    Detection(
        id="det_006",
        timestamp="2026-09-06T08:30:00Z",
        rover_location=RoverLocation(row=6, section="A", distance_from_start_meters=50),
        detection_result=DetectionResultPayload(
            image_path="/images/det_006.jpg",
            disease_class="pest_damage",
            confidence=0.88,
            severity_class="early",
            affected_area_percentage=15.0,
            symptoms_detected=["fruit_fly_marks", "aphid_colonies"],
        ),
        environmental_data=EnvironmentalData(
            temperature_celsius=27.0,
            humidity_percentage=68.0,
            soil_moisture_percentage=52.0,
            light_intensity_lux=950.0,
        ),
    ),
    Detection(
        id="det_007",
        timestamp="2026-09-05T13:10:00Z",
        rover_location=RoverLocation(row=2, section="C", distance_from_start_meters=16),
        detection_result=DetectionResultPayload(
            image_path="/images/det_007.jpg",
            disease_class="powdery_mildew",
            confidence=0.96,
            severity_class="severe",
            affected_area_percentage=72.0,
            symptoms_detected=["white_coating", "leaf_curling", "stunted_growth"],
        ),
        environmental_data=EnvironmentalData(
            temperature_celsius=35.0,
            humidity_percentage=80.0,
            soil_moisture_percentage=65.0,
            light_intensity_lux=600.0,
        ),
    ),
    Detection(
        id="det_008",
        timestamp="2026-09-04T09:00:00Z",
        rover_location=RoverLocation(row=4, section="D", distance_from_start_meters=36),
        detection_result=DetectionResultPayload(
            image_path="/images/det_008.jpg",
            disease_class="healthy",
            confidence=0.99,
            severity_class="healthy",
            affected_area_percentage=0.0,
            symptoms_detected=[],
        ),
        environmental_data=EnvironmentalData(
            temperature_celsius=26.0,
            humidity_percentage=65.0,
            soil_moisture_percentage=55.0,
            light_intensity_lux=1100.0,
        ),
    ),
]

# ── Farm Grid (5 rows × 4 sections) ──────────────────────────────────────────

FARM_GRID: list[FarmCell] = [
    FarmCell(row=1, col=1, section="A", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T09:00:00Z"),
    FarmCell(row=1, col=2, section="B", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T09:10:00Z"),
    FarmCell(row=1, col=3, section="C", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T09:20:00Z", detection_id="det_003"),
    FarmCell(row=1, col=4, section="D", status="attention", disease_class="pest_damage",      severity="early",    last_checked="2026-09-11T09:30:00Z", detection_id="det_006"),
    FarmCell(row=2, col=1, section="A", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T10:00:00Z"),
    FarmCell(row=2, col=2, section="B", status="diseased",  disease_class="powdery_mildew",   severity="moderate", last_checked="2026-09-11T14:30:00Z", detection_id="det_001"),
    FarmCell(row=2, col=3, section="C", status="diseased",  disease_class="powdery_mildew",   severity="severe",   last_checked="2026-09-11T10:20:00Z", detection_id="det_007"),
    FarmCell(row=2, col=4, section="D", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T10:30:00Z"),
    FarmCell(row=3, col=1, section="A", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T11:00:00Z"),
    FarmCell(row=3, col=2, section="B", status="attention", disease_class="downy_mildew",     severity="early",    last_checked="2026-09-11T11:10:00Z"),
    FarmCell(row=3, col=3, section="C", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T11:20:00Z"),
    FarmCell(row=3, col=4, section="D", status="diseased",  disease_class="fungal_leaf_spot", severity="severe",   last_checked="2026-09-11T11:30:00Z", detection_id="det_004"),
    FarmCell(row=4, col=1, section="A", status="attention", disease_class="downy_mildew",     severity="early",    last_checked="2026-09-11T12:00:00Z", detection_id="det_002"),
    FarmCell(row=4, col=2, section="B", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T12:10:00Z"),
    FarmCell(row=4, col=3, section="C", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T12:20:00Z"),
    FarmCell(row=4, col=4, section="D", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T12:30:00Z", detection_id="det_008"),
    FarmCell(row=5, col=1, section="A", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T13:00:00Z"),
    FarmCell(row=5, col=2, section="B", status="diseased",  disease_class="viral_symptoms",   severity="moderate", last_checked="2026-09-11T13:10:00Z", detection_id="det_005"),
    FarmCell(row=5, col=3, section="C", status="healthy",   disease_class="healthy",          severity="healthy",  last_checked="2026-09-11T13:20:00Z"),
    FarmCell(row=5, col=4, section="D", status="attention", disease_class="pest_damage",      severity="early",    last_checked="2026-09-11T13:30:00Z"),
]

# ── Trend Data ────────────────────────────────────────────────────────────────

TREND_DATA = [
    {"date": "Aug 29", "healthy": 18, "attention": 1, "diseased": 1},
    {"date": "Aug 30", "healthy": 17, "attention": 2, "diseased": 1},
    {"date": "Aug 31", "healthy": 16, "attention": 3, "diseased": 1},
    {"date": "Sep 1",  "healthy": 15, "attention": 3, "diseased": 2},
    {"date": "Sep 2",  "healthy": 15, "attention": 2, "diseased": 3},
    {"date": "Sep 3",  "healthy": 14, "attention": 3, "diseased": 3},
    {"date": "Sep 4",  "healthy": 16, "attention": 2, "diseased": 2},
    {"date": "Sep 5",  "healthy": 14, "attention": 3, "diseased": 3},
    {"date": "Sep 6",  "healthy": 15, "attention": 3, "diseased": 2},
    {"date": "Sep 7",  "healthy": 14, "attention": 2, "diseased": 4},
    {"date": "Sep 8",  "healthy": 13, "attention": 3, "diseased": 4},
    {"date": "Sep 9",  "healthy": 14, "attention": 3, "diseased": 3},
    {"date": "Sep 10", "healthy": 13, "attention": 3, "diseased": 4},
    {"date": "Sep 11", "healthy": 12, "attention": 4, "diseased": 4},
]

DISEASE_DISTRIBUTION = [
    {"name": "Powdery Mildew",  "value": 3,  "color": "#F59E0B"},
    {"name": "Downy Mildew",    "value": 2,  "color": "#3B82F6"},
    {"name": "Fungal Leaf Spot","value": 2,  "color": "#8B5CF6"},
    {"name": "Viral Symptoms",  "value": 1,  "color": "#EF4444"},
    {"name": "Pest Damage",     "value": 2,  "color": "#F97316"},
    {"name": "Healthy",         "value": 10, "color": "#22C55E"},
]
