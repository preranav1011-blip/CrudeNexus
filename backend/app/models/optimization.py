"""Pydantic models for optimization results"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class SupplierAllocationModel(BaseModel):
    """Supplier allocation within strategy"""
    supplier_id: str
    allocation_percentage: float  # 0-100
    allocated_volume_mbd: float
    allocated_cost: float


class ProcurementStrategyResponse(BaseModel):
    """Response model for procurement strategy"""
    strategy_id: str
    strategy_type: str  # cheapest, balanced, safest
    total_cost: float
    total_crude_supply: float
    avg_risk_score: float  # 0-100
    avg_transit_time: float  # days
    supplier_concentration_ratio: float  # 0-1
    allocations: List[SupplierAllocationModel]
    explanation: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class OptimizationRequest(BaseModel):
    """Request model for procurement optimization"""
    risk_tolerance: float = 0.5  # 0 = low tolerance, 1 = high tolerance
    event_id: Optional[str] = None  # Link to triggering event
    india_demand_mbd: Optional[float] = None  # Override default demand


class OptimizationResultsResponse(BaseModel):
    """Response with all three strategies"""
    cheapest: ProcurementStrategyResponse
    balanced: ProcurementStrategyResponse
    safest: ProcurementStrategyResponse
    recommended: str  # Strategy ID recommended by system
    recommendation_reason: str
