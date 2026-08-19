"""Pydantic models for geopolitical events"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GeopoliticalEventCreate(BaseModel):
    """Request model for creating a geopolitical event"""
    event_type: str  # e.g., geopolitical_tension, port_disruption
    location: str
    description: Optional[str] = None
    severity_raw: Optional[float] = None  # 0-1
    source: Optional[str] = "MANUAL_INPUT"


class GeopoliticalEventResponse(BaseModel):
    """Response model for geopolitical event"""
    event_id: str
    timestamp: datetime
    event_type: str
    location: str
    description: Optional[str]
    severity_raw: Optional[float]
    affected_corridor: Optional[str]
    india_relevance: Optional[float]
    source: str
    raw_confidence: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Response for event list"""
    total: int
    events: list[GeopoliticalEventResponse]
