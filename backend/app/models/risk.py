"""Pydantic models for risk analysis"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RiskSignal(BaseModel):
    """Evidence signal contributing to risk"""
    signal_name: str  # e.g., news_sentiment, sanctions_exposure
    strength: float  # 0-1
    source: str


class RiskAssessmentResponse(BaseModel):
    """Response model for risk assessment"""
    assessment_id: str
    event_id: Optional[str]
    corridor_name: str
    risk_score: float  # 0-100
    risk_confidence: float  # 0-1
    disruption_probability_7d: Optional[float]
    evidence_signals: dict  # news, sanctions, historical
    india_exposure_percentage: float
    affected_suppliers: List[str]
    conflicting_signals: Optional[bool] = False
    conflicting_signals_detail: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
