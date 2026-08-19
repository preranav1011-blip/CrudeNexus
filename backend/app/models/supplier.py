"""Pydantic models for suppliers and routes"""
from pydantic import BaseModel
from typing import Optional


class SupplierBase(BaseModel):
    """Base supplier model"""
    supplier_id: str
    supplier_name: str
    supplier_country: str
    production_capacity_mbd: float
    estimated_cost_per_barrel: float
    geopolitical_baseline_risk_score: float


class SupplierResponse(SupplierBase):
    """Response model for supplier"""
    pass

    class Config:
        from_attributes = True


class RouteBase(BaseModel):
    """Base route model"""
    route_id: str
    route_name: str
    origin_port: str
    destination_port: str
    corridor: str
    distance_km: float
    transit_time_days: float
    capacity_mbd: float
    baseline_risk_score: float
    is_blocked: bool = False


class RouteResponse(RouteBase):
    """Response model for route"""
    pass

    class Config:
        from_attributes = True


class CorridorBase(BaseModel):
    """Base corridor model"""
    corridor_name: str
    location: str
    baseline_risk_score: float
    estimated_current_disruption_probability: float
    affected_routes: str  # Pipe-separated route IDs
    affected_suppliers: str  # Pipe-separated supplier IDs
    india_import_percentage: float


class CorridorResponse(CorridorBase):
    """Response model for corridor"""
    pass

    class Config:
        from_attributes = True
