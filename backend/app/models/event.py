"""Pydantic models for geopolitical events"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class GeopoliticalEventCreate(BaseModel):
    """Request model for creating a geopolitical event"""
    event_type: Optional[str] = None  # e.g., geopolitical_tension, port_disruption
    location: Optional[str] = None
    description: str = Field(min_length=1)
    timestamp: Optional[datetime] = None
    severity_raw: Optional[float] = Field(default=None, ge=0, le=1)
    affected_corridor: Optional[str] = None
    india_relevance: Optional[float] = Field(default=None, ge=0, le=1)
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
    limit: int
    offset: int
