"""GET /api/farm — farm grid and health summary."""

from fastapi import APIRouter
from data.mock_data import FARM_GRID
from models.schemas import FarmGridResponse, FarmCell
from services.disease_service import get_disease_info, DISEASE_INFO

router = APIRouter(prefix="/api/farm", tags=["farm"])


def _compute_summary(cells: list[FarmCell]) -> dict:
    total = len(cells)
    healthy = sum(1 for c in cells if c.status == "healthy")
    attention = sum(1 for c in cells if c.status == "attention")
    diseased = sum(1 for c in cells if c.status == "diseased")
    return {
        "total_cells": total,
        "healthy_count": healthy,
        "attention_count": attention,
        "diseased_count": diseased,
        "healthy_pct": round(healthy / total * 100, 1) if total else 0,
        "attention_pct": round(attention / total * 100, 1) if total else 0,
        "diseased_pct": round(diseased / total * 100, 1) if total else 0,
        "rows": max(c.row for c in cells) if cells else 0,
        "sections": sorted(list({c.section for c in cells})),
    }


@router.get("/grid", response_model=FarmGridResponse)
async def get_farm_grid():
    """Return the full farm grid with health status per cell."""
    summary = _compute_summary(FARM_GRID)
    return FarmGridResponse(cells=FARM_GRID, **summary)


@router.get("/grid/{row}/{section}")
async def get_cell(row: int, section: str):
    """Return details for a single farm cell."""
    section_upper = section.upper()
    for cell in FARM_GRID:
        if cell.row == row and cell.section == section_upper:
            disease_info = get_disease_info(cell.disease_class)
            return {
                "cell": cell,
                "disease_info": disease_info,
            }
    return {"error": "Cell not found", "row": row, "section": section_upper}


@router.get("/summary")
async def get_farm_summary():
    """Return health summary statistics for dashboard."""
    summary = _compute_summary(FARM_GRID)
    # Disease breakdown
    disease_counts: dict[str, int] = {}
    for cell in FARM_GRID:
        dc = cell.disease_class
        disease_counts[dc] = disease_counts.get(dc, 0) + 1
    return {**summary, "disease_counts": disease_counts}


@router.get("/disease-info/{disease_class}")
async def get_disease_info_endpoint(disease_class: str):
    """Return detailed disease info including recommendations."""
    if disease_class not in DISEASE_INFO:
        return {"error": "Unknown disease class", "disease_class": disease_class}
    return {
        "disease_class": disease_class,
        **DISEASE_INFO[disease_class],
    }
