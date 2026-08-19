"""Routes for data endpoints (suppliers, routes, corridors)"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.supplier import SupplierResponse, RouteResponse, CorridorResponse
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(
    db: Session = Depends(get_db)
):
    """Get all Indian crude suppliers"""
    # TODO: Load from CSV or cache
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/routes", response_model=List[RouteResponse])
async def get_routes(
    db: Session = Depends(get_db)
):
    """Get all crude import routes to India"""
    # TODO: Load from CSV or cache
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/corridors", response_model=List[CorridorResponse])
async def get_corridors(
    db: Session = Depends(get_db)
):
    """Get all critical chokepoints/corridors"""
    # TODO: Load from CSV or cache
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/ports")
async def get_ports(
    db: Session = Depends(get_db)
):
    """Get port information"""
    # TODO: Load from CSV or cache
    raise HTTPException(status_code=501, detail="Not yet implemented")
