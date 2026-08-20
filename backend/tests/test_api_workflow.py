"""Phase 7 integration test: event ingestion through persisted strategy generation."""
import asyncio

from app.agents import geopolitical_risk
from app.database.db import SessionLocal, init_db
from app.database.models import GeopoliticalEvent, ProcurementStrategy, RiskAssessment, SupplierAllocation
from app.models.event import GeopoliticalEventCreate
from app.models.optimization import OptimizationRequest
from app.routes.analysis import analyze_risk
from app.routes.events import create_event, delete_event
from app.routes.optimization import generate_strategies, get_strategy


def test_event_to_risk_to_strategy_workflow(monkeypatch):
    monkeypatch.setitem(geopolitical_risk.LLM_CONFIG, "enabled", False)
    init_db()
    db = SessionLocal()
    event_id = assessment_id = None
    strategy_ids = []
    try:
        event = asyncio.run(create_event(GeopoliticalEventCreate(description="Naval tensions escalate in the Strait of Hormuz, threatening Indian crude tankers."), db))
        event_id = event.event_id
        assessment = asyncio.run(analyze_risk(event_id, db))
        assessment_id = assessment.assessment_id
        assert assessment.risk_score > 0
        result = asyncio.run(generate_strategies(OptimizationRequest(risk_tolerance=.4, risk_assessment_id=assessment_id), db))
        strategy_ids = [result.cheapest.strategy_id, result.balanced.strategy_id, result.safest.strategy_id]
        assert result.recommended == result.balanced.strategy_id
        stored = asyncio.run(get_strategy(result.recommended, db))
        assert stored.allocations
    finally:
        for strategy_id in strategy_ids:
            db.query(SupplierAllocation).filter_by(strategy_id=strategy_id).delete()
            db.query(ProcurementStrategy).filter_by(strategy_id=strategy_id).delete()
        if assessment_id:
            db.query(RiskAssessment).filter_by(assessment_id=assessment_id).delete()
        if event_id:
            db.query(GeopoliticalEvent).filter_by(event_id=event_id).delete()
        db.commit()
        db.close()
