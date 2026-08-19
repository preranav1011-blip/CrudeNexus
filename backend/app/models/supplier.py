"""Pydantic models for suppliers and routes"""
from pydantic import BaseModel
from typing import Optional, List


class SupplierResponse(BaseModel):
    """Response model for supplier"""
    supplier_id: str
    name: str
    country: str
    capacity_mbd: float
    cost_per_barrel: float
    geopolitical_risk: float

    class Config:
        from_attributes = True


class RouteResponse(BaseModel):
    """Response model for route"""
    route_id: str
    origin: str
    destination: str
    corridor_name: str
    distance_km: float
    transit_days: float
    capacity_mbd: float
    chokepoint: str
    geopolitical_risk_score: float

    class Config:
        from_attributes = True


class PortResponse(BaseModel):
    """Response model for port"""
    port_id: str
    country: str
    port_name: str
    port_type: str
    capacity_mbd: float
    draft_constraints: float
    infrastructure_quality: str
    trade_volume_2023_mbd: float

    class Config:
        from_attributes = True


class CorridorResponse(BaseModel):
    """Response model for corridor"""
    corridor_id: str
    corridor_name: str
    location: str
    transit_countries: List[str]
    chokepoint_type: str
    annual_traffic_pct_india: float
    risk_trigger_events: List[str]
    historical_disruptions: List[str]

    class Config:
        from_attributes = True
