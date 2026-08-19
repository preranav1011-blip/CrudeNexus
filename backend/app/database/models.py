"""SQLAlchemy ORM models for database tables"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database.db import Base


class GeopoliticalEvent(Base):
    """Geopolitical event table"""
    __tablename__ = "geopolitical_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    event_type = Column(String, nullable=False)  # e.g., geopolitical_tension, port_disruption
    location = Column(String, nullable=False)
    description = Column(Text)
    severity_raw = Column(Float)  # 0-1
    affected_corridor = Column(String)
    india_relevance = Column(Float)  # 0-1
    source = Column(String)  # e.g., GDELT_NEWS
    raw_confidence = Column(Float)  # 0-1
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    risk_assessments = relationship("RiskAssessment", back_populates="event")


class RiskAssessment(Base):
    """Risk assessment for geopolitical events"""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String, unique=True, index=True, nullable=False)
    event_id = Column(String, ForeignKey("geopolitical_events.event_id"))
    corridor_name = Column(String, nullable=False)
    risk_score_ml = Column(Float, nullable=False)  # 0-100, from ML model
    risk_confidence = Column(Float, nullable=False)  # 0-1
    disruption_probability_7d = Column(Float)  # 0-1, P(disruption in 7 days)
    evidence_news_signal = Column(Float)  # 0-1
    evidence_sanctions_signal = Column(Float)  # 0-1
    evidence_historical = Column(Float)  # 0-1
    india_exposure_percentage = Column(Float)  # 0-100
    affected_suppliers = Column(String)  # JSON string of supplier IDs
    created_at = Column(DateTime, default=func.now())
    
    event = relationship("GeopoliticalEvent", back_populates="risk_assessments")
    procurement_strategies = relationship("ProcurementStrategy", back_populates="risk_assessment")


class ProcurementStrategy(Base):
    """Procurement strategy optimization results"""
    __tablename__ = "procurement_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String, unique=True, index=True, nullable=False)
    strategy_type = Column(String, nullable=False)  # e.g., cheapest, balanced, safest
    risk_assessment_id = Column(String, ForeignKey("risk_assessments.assessment_id"))
    total_cost = Column(Float)  # Total procurement cost
    total_crude_supply = Column(Float)  # Million barrels/day
    avg_risk_score = Column(Float)  # 0-100
    avg_transit_time = Column(Float)  # days
    supplier_concentration_ratio = Column(Float)  # 0-1 (Herfindahl index)
    allocation_json = Column(Text)  # JSON with supplier allocations
    explanation = Column(Text)  # Explainable recommendation
    created_at = Column(DateTime, default=func.now())
    
    risk_assessment = relationship("RiskAssessment", back_populates="procurement_strategies")
    supplier_allocations = relationship("SupplierAllocation", back_populates="strategy")


class SupplierAllocation(Base):
    """Supplier allocation within a procurement strategy"""
    __tablename__ = "supplier_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String, ForeignKey("procurement_strategies.strategy_id"))
    supplier_id = Column(String, nullable=False)
    allocation_percentage = Column(Float)  # 0-100
    allocated_volume_mbd = Column(Float)  # Million barrels/day
    allocated_cost = Column(Float)
    
    strategy = relationship("ProcurementStrategy", back_populates="supplier_allocations")
