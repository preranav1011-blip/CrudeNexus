"""Routes for data endpoints (suppliers, routes, corridors)"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.supplier import SupplierResponse, RouteResponse, CorridorResponse, PortResponse
from app.data.csv_loaders import (
    SupplierLoader,
    RouteLoader,
    PortLoader,
    CorridorLoader
)
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory caches for CSV data (loaded on first request)
_suppliers_cache = None
_routes_cache = None
_corridors_cache = None
_ports_cache = None


@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(
    db: Session = Depends(get_db)
):
    """Get all Indian crude suppliers"""
    global _suppliers_cache
    
    if _suppliers_cache is None:
        try:
            _suppliers_cache = SupplierLoader.load_suppliers()
            logger.info(f"Loaded {len(_suppliers_cache)} suppliers from CSV")
        except Exception as e:
            logger.error(f"Error loading suppliers: {e}")
            raise HTTPException(status_code=500, detail="Error loading supplier data")
    
    return _suppliers_cache


@router.get("/routes", response_model=List[RouteResponse])
async def get_routes(
    db: Session = Depends(get_db)
):
    """Get all crude import routes to India"""
    global _routes_cache
    
    if _routes_cache is None:
        try:
            _routes_cache = RouteLoader.load_routes()
            logger.info(f"Loaded {len(_routes_cache)} routes from CSV")
        except Exception as e:
            logger.error(f"Error loading routes: {e}")
            raise HTTPException(status_code=500, detail="Error loading route data")
    
    return _routes_cache


@router.get("/corridors", response_model=List[CorridorResponse])
async def get_corridors(
    db: Session = Depends(get_db)
):
    """Get all critical chokepoints/corridors"""
    global _corridors_cache
    
    if _corridors_cache is None:
        try:
            _corridors_cache = CorridorLoader.load_corridors()
            logger.info(f"Loaded {len(_corridors_cache)} corridors from CSV")
        except Exception as e:
            logger.error(f"Error loading corridors: {e}")
            raise HTTPException(status_code=500, detail="Error loading corridor data")
    
    return _corridors_cache


@router.get("/ports", response_model=List[PortResponse])
async def get_ports(
    db: Session = Depends(get_db)
):
    """Get port information"""
    global _ports_cache
    
    if _ports_cache is None:
        try:
            _ports_cache = PortLoader.load_ports()
            logger.info(f"Loaded {len(_ports_cache)} ports from CSV")
        except Exception as e:
            logger.error(f"Error loading ports: {e}")
            raise HTTPException(status_code=500, detail="Error loading port data")
    
    return _ports_cache


@router.get("/refresh-cache")
async def refresh_cache():
    """Refresh all data caches from CSV files"""
    global _suppliers_cache, _routes_cache, _corridors_cache, _ports_cache
    
    try:
        _suppliers_cache = SupplierLoader.load_suppliers()
        _routes_cache = RouteLoader.load_routes()
        _corridors_cache = CorridorLoader.load_corridors()
        _ports_cache = PortLoader.load_ports()
        
        return {
            "status": "success",
            "message": "All data caches refreshed",
            "suppliers": len(_suppliers_cache),
            "routes": len(_routes_cache),
            "corridors": len(_corridors_cache),
            "ports": len(_ports_cache)
        }
    except Exception as e:
        logger.error(f"Error refreshing cache: {e}")
        raise HTTPException(status_code=500, detail="Error refreshing data cache")
