"""Pydantic models for optimization results"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict
from datetime import datetime


class SupplierAllocationModel(BaseModel):
    """Supplier allocation within strategy"""
    supplier_id: str
    allocation_percentage: float  # 0-100
    allocated_volume_mbd: float = 0
    allocated_cost: float = 0


class StrategyResponse(BaseModel):
    """Response model for procurement strategy"""
    strategy_id: str
    strategy_type: str  # cheapest, balanced, safest
    total_cost: float
    total_crude_supply: float
    avg_risk_score: float  # 0-100
    avg_transit_time: float  # days
    supplier_concentration_ratio: float  # 0-1
    allocations: List[SupplierAllocationModel] = Field(default_factory=list)
    explanation: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def unpack_allocations(cls, value):
        if isinstance(value, dict):
            return value
        import json
        data = {field: getattr(value, field, None) for field in cls.model_fields}
        raw = getattr(value, "allocation_json", "[]") or "[]"
        try:
            allocations = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            allocations = []
        data["allocations"] = [
            {
                **allocation,
                "allocated_volume_mbd": allocation.get(
                    "allocated_volume_mbd", allocation.get("allocation_mbd", 0)
                ),
                "allocated_cost": allocation.get("allocated_cost", 0),
            }
            for allocation in allocations
        ]
        return data


ProcurementStrategyResponse = StrategyResponse


class OptimizationRequest(BaseModel):
    """Request model for procurement optimization"""
    risk_tolerance: float = Field(default=0.5, ge=0, le=1)  # 0 = low tolerance, 1 = high tolerance
    event_id: Optional[str] = None  # Link to triggering event
    risk_assessment_id: Optional[str] = None
    india_demand_mbd: Optional[float] = None  # Override default demand
    blocked_corridors: List[str] = Field(default_factory=list)


class OptimizationResultsResponse(BaseModel):
    """Response with all three strategies"""
    cheapest: StrategyResponse
    balanced: StrategyResponse
    safest: StrategyResponse
    recommended: str  # Strategy ID recommended by system
    recommendation_reason: str


class StrategyComparisonResponse(BaseModel):
    strategies: List[StrategyResponse]
    best_by_cost: Optional[StrategyResponse] = None
    best_by_safety: Optional[StrategyResponse] = None
    best_balanced: Optional[StrategyResponse] = None
