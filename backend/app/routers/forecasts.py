"""
routers/forecasts.py - AI Demand Forecasting Endpoints

This router exposes machine learning demand forecasts and crop analytics.
Available to Farmers, FPOs, and Bulk Buyers to plan production and purchasing.
"""

from fastapi import APIRouter, Query
from typing import Optional, List

from app.services.forecasting import predict_demand, get_available_crops

router = APIRouter(prefix="/api/forecasts", tags=["AI Forecasting"])


@router.get("/crops")
def list_crops() -> List[str]:
    """Returns list of crops supported by the forecasting engine."""
    return get_available_crops()


@router.get("/demand")
def get_demand_forecast(
    crop: str = Query("Tomatoes", description="Name of agricultural produce"),
    months: int = Query(6, ge=1, le=12, description="Months ahead to forecast (1-12)"),
):
    """
    Generate Machine Learning demand and price projection for a selected crop.
    Returns:
    - Historical trend (last 12 months)
    - Future forecasts (next N months)
    - Model metrics (MAE, RMSE, accuracy percentage)
    - Actionable farmer recommendations
    - Clear model limitations disclaimer
    """
    result = predict_demand(crop_name=crop, forecast_months=months)
    return result
