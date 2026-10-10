"""
routers/mandi.py - Agmarknet Live Mandi Market Rates Endpoints

Exposes:
- GET /api/mandi/rates (filtered by state and commodity)
- GET /api/mandi/states (list of active states)
- GET /api/mandi/commodities (list of active commodities)
"""

from fastapi import APIRouter, Query
from typing import List, Optional

from app.services.mandi import fetch_mandi_rates, get_available_states, get_available_commodities

router = APIRouter(prefix="/api/mandi", tags=["Mandi Market Rates"])


@router.get("/states")
def list_states() -> List[str]:
    """Returns list of available Indian states with mandi data."""
    return get_available_states()


@router.get("/commodities")
def list_commodities() -> List[str]:
    """Returns list of available commodities."""
    return get_available_commodities()


@router.get("/rates")
def get_mandi_rates(
    state: Optional[str] = Query(None, description="Filter by state (e.g. Haryana, Punjab)"),
    commodity: Optional[str] = Query(None, description="Filter by commodity (e.g. Tomato, Wheat)"),
):
    """
    Fetch daily mandi market rates with comparison vs direct marketplace pricing.
    """
    return fetch_mandi_rates(state=state, commodity=commodity)
