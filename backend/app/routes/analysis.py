"""Routes for risk analysis endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import GeopoliticalEvent, RiskAssessment
from app.models.risk import RiskAssessmentResponse, RiskAssessmentListResponse
from app.agents.geopolitical_risk import calculate_risk_score
from app.agents.supply_exposure import calculate_supply_exposure
from app.data.csv_loaders import SupplierLoader, RouteLoader, CorridorLoader
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/risk", response_model=RiskAssessmentResponse)
async def analyze_risk(
    event_id: str,
    db: Session = Depends(get_db)
):
    """Analyze geopolitical risk for an event"""
    try:
        # Get event
        event = db.query(GeopoliticalEvent).filter(
            GeopoliticalEvent.event_id == event_id
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        
        # Calculate risk scores
        risk_data = calculate_risk_score(event)
        
        # Create risk assessment record
        assessment_id = f"RSK_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Get affected corridor routes and suppliers
        affected_corridor = event.affected_corridor or "Unknown"
        corridors = CorridorLoader.load_corridors()
        corridor_info = next(
            (c for c in corridors if affected_corridor in {c.get('corridor_id'), c.get('corridor_name')}),
            {},
        )
        corridor_name = corridor_info.get('corridor_name', affected_corridor)
        
        # Calculate supply exposure
        exposure = calculate_supply_exposure(
            corridor=corridor_name,
            risk_score=risk_data.get("risk_score_ml", 50),
            event=event
        )
        
        db_assessment = RiskAssessment(
            assessment_id=assessment_id,
            event_id=event_id,
            corridor_name=corridor_name,
            risk_score_ml=risk_data.get("risk_score_ml", 50),
            risk_confidence=risk_data.get("confidence", 0.7),
            disruption_probability_7d=risk_data.get("disruption_probability", 0.5),
            evidence_news_signal=risk_data.get("news_signal", event.severity_raw),
            evidence_sanctions_signal=risk_data.get("sanctions_signal", 0.0),
            evidence_historical=risk_data.get("historical_signal", 0.3),
            india_exposure_percentage=exposure.get("exposed_percentage", 25),
            affected_suppliers=__import__("json").dumps(exposure.get("affected_suppliers", [])),
        )
        
        db.add(db_assessment)
        db.commit()
        db.refresh(db_assessment)
        
        logger.info(f"Created risk assessment {assessment_id} for event {event_id}")
        return RiskAssessmentResponse.model_validate(db_assessment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing risk for event {event_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/risk/{assessment_id}", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """Get risk assessment details"""
    try:
        assessment = db.query(RiskAssessment).filter(
            RiskAssessment.assessment_id == assessment_id
        ).first()
        
        if not assessment:
            raise HTTPException(status_code=404, detail=f"Assessment {assessment_id} not found")
        
        return RiskAssessmentResponse.model_validate(assessment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assessment {assessment_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving assessment")


@router.get("/corridors/risk")
async def get_all_corridor_risks(
    db: Session = Depends(get_db)
):
    """Get current risk for all major corridors"""
    try:
        corridors = CorridorLoader.load_corridors()
        
        corridor_risks = []
        for corridor in corridors:
            corridor_id = corridor.get('corridor_id', '')
            corridor_name = corridor.get('corridor_name', 'Unknown')
            
            # Get latest assessment for this corridor
            latest_assessment = db.query(RiskAssessment).filter(
                RiskAssessment.corridor_name == corridor_name
            ).order_by(RiskAssessment.created_at.desc()).first()
            
            if latest_assessment:
                corridor_risks.append({
                    "corridor_id": corridor_id,
                    "corridor_name": corridor_name,
                    "location": corridor.get('location', ''),
                    "risk_score": latest_assessment.risk_score_ml,
                    "risk_confidence": latest_assessment.risk_confidence,
                    "disruption_probability": latest_assessment.disruption_probability_7d,
                    "india_exposure_pct": latest_assessment.india_exposure_percentage,
                    "india_annual_traffic_pct": corridor.get('annual_traffic_pct_india', 0),
                    "risk_trigger_events": corridor.get('risk_trigger_events', []),
                })
            else:
                # If no assessment yet, use baseline from corridor data
                corridor_risks.append({
                    "corridor_id": corridor_id,
                    "corridor_name": corridor_name,
                    "location": corridor.get('location', ''),
                    "risk_score": 30,  # Baseline
                    "risk_confidence": 0.5,
                    "disruption_probability": 0.1,
                    "india_exposure_pct": 0,
                    "india_annual_traffic_pct": corridor.get('annual_traffic_pct_india', 0),
                    "risk_trigger_events": corridor.get('risk_trigger_events', []),
                })
        
        return {
            "total_corridors": len(corridor_risks),
            "corridors": sorted(corridor_risks, key=lambda x: x['risk_score'], reverse=True),
            "highest_risk": max((c['risk_score'] for c in corridor_risks), default=0),
            "average_risk": sum(c['risk_score'] for c in corridor_risks) / len(corridor_risks) if corridor_risks else 0,
        }
        
    except Exception as e:
        logger.error(f"Error retrieving corridor risks: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving corridor risks")


@router.get("", response_model=RiskAssessmentListResponse)
async def list_assessments(
    limit: int = Query(20, le=100),
    offset: int = 0,
    corridor: str = None,
    db: Session = Depends(get_db)
):
    """List risk assessments"""
    try:
        query = db.query(RiskAssessment).order_by(RiskAssessment.created_at.desc())
        
        if corridor:
            query = query.filter(RiskAssessment.corridor_name == corridor)
        
        total = query.count()
        assessments = query.offset(offset).limit(limit).all()
        
        return RiskAssessmentListResponse(
            assessments=[RiskAssessmentResponse.model_validate(a) for a in assessments],
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing assessments: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving assessments")
