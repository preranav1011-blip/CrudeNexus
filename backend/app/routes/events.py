"""Routes for event management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.db import get_db
from app.database.models import GeopoliticalEvent
from app.models.event import GeopoliticalEventCreate, GeopoliticalEventResponse, EventListResponse
from app.agents.geopolitical_risk import extract_event_from_text
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=GeopoliticalEventResponse)
async def create_event(
    event: GeopoliticalEventCreate,
    db: Session = Depends(get_db)
):
    """Create a new geopolitical event"""
    try:
        # Extract structured event data from description using LLM/heuristic
        extracted = extract_event_from_text(event.description)
        
        # Create database record
        db_event = GeopoliticalEvent(
            event_id=f"EVT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
            timestamp=event.timestamp or datetime.utcnow(),
            event_type=extracted.get("event_type", event.event_type or "geopolitical_event"),
            location=extracted.get("location", event.location or "Unknown"),
            description=event.description,
            severity_raw=extracted.get("severity", 0.5),
            affected_corridor=extracted.get("affected_corridor", event.affected_corridor),
            india_relevance=extracted.get("india_relevance", 0.5),
            source=event.source or "USER_INPUT",
            raw_confidence=extracted.get("confidence", 0.7),
        )
        
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        logger.info(f"Created event {db_event.event_id}")
        return GeopoliticalEventResponse.from_orm(db_event)
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=EventListResponse)
async def list_events(
    limit: int = 20,
    offset: int = 0,
    event_type: str = None,
    db: Session = Depends(get_db)
):
    """List recent geopolitical events"""
    try:
        query = db.query(GeopoliticalEvent).order_by(desc(GeopoliticalEvent.timestamp))
        
        # Filter by event type if specified
        if event_type:
            query = query.filter(GeopoliticalEvent.event_type == event_type)
        
        # Count total
        total = query.count()
        
        # Apply limit and offset
        events = query.offset(offset).limit(limit).all()
        
        return EventListResponse(
            events=[GeopoliticalEventResponse.from_orm(e) for e in events],
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving events")


@router.get("/{event_id}", response_model=GeopoliticalEventResponse)
async def get_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    """Get event details"""
    try:
        event = db.query(GeopoliticalEvent).filter(
            GeopoliticalEvent.event_id == event_id
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        
        return GeopoliticalEventResponse.from_orm(event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving event")


@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    """Delete an event"""
    try:
        event = db.query(GeopoliticalEvent).filter(
            GeopoliticalEvent.event_id == event_id
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        
        db.delete(event)
        db.commit()
        
        logger.info(f"Deleted event {event_id}")
        return {"status": "success", "message": f"Event {event_id} deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting event")


@router.get("/recent/{hours}", response_model=EventListResponse)
async def get_recent_events(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get events from last N hours"""
    try:
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        events = db.query(GeopoliticalEvent).filter(
            GeopoliticalEvent.timestamp >= cutoff_time
        ).order_by(desc(GeopoliticalEvent.timestamp)).all()
        
        return EventListResponse(
            events=[GeopoliticalEventResponse.from_orm(e) for e in events],
            total=len(events),
            limit=len(events),
            offset=0
        )
        
    except Exception as e:
        logger.error(f"Error retrieving recent events: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving events")
