"""Pydantic models for risk analysis"""
from pydantic import BaseModel, model_validator
import json
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

    @model_validator(mode="before")
    @classmethod
    def adapt_orm_assessment(cls, value):
        """Translate database column names into the public API contract."""
        if isinstance(value, dict):
            data = dict(value)
        else:
            data = {
                field: getattr(value, field, None)
                for field in cls.model_fields
            }
            data["risk_score"] = getattr(value, "risk_score_ml", None)
            data["evidence_signals"] = {
                "news": getattr(value, "evidence_news_signal", None),
                "sanctions": getattr(value, "evidence_sanctions_signal", None),
                "historical": getattr(value, "evidence_historical", None),
            }
            raw_suppliers = getattr(value, "affected_suppliers", "") or ""
            try:
                data["affected_suppliers"] = json.loads(raw_suppliers)
            except (TypeError, json.JSONDecodeError):
                data["affected_suppliers"] = [item for item in raw_suppliers.split(",") if item]
        signals = data.get("evidence_signals", {})
        values = [value for value in signals.values() if isinstance(value, (int, float))]
        if values and "conflicting_signals" not in data:
            conflict = max(values) - min(values) >= 0.45
            data["conflicting_signals"] = conflict
            if conflict:
                data["conflicting_signals_detail"] = "Risk evidence contains materially divergent signals."
        return data


class RiskAssessmentListResponse(BaseModel):
    """Paginated risk-assessment collection."""
    assessments: List[RiskAssessmentResponse]
    total: int
    limit: int
    offset: int
