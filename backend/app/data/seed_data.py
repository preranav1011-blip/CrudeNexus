#!/usr/bin/env python3
"""
Database seeding script for Phase 2
Populates SQLite database with supplier, route, port, corridor, and sample event data
Usage: python -m app.data.seed_data
"""
import logging
import sys
from sqlalchemy.orm import sessionmaker
from app.database.db import engine, Base
from app.database.models import (
    GeopoliticalEvent, 
    RiskAssessment,
    ProcurementStrategy,
    SupplierAllocation
)
from app.data.csv_loaders import (
    SupplierLoader,
    RouteLoader,
    PortLoader,
    CorridorLoader,
    EventLoader,
    seed_geopolitical_events
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database tables"""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def seed_database():
    """Seed all data into database"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Initialize database tables first
        init_database()
        
        # Clear existing data (optional - comment out to preserve)
        # logger.info("Clearing existing data...")
        # db.query(GeopoliticalEvent).delete()
        # db.query(RiskAssessment).delete()
        # db.query(ProcurementStrategy).delete()
        # db.query(SupplierAllocation).delete()
        # db.commit()
        
        # Load and seed data
        logger.info("Loading supplier data...")
        suppliers = SupplierLoader.load_suppliers()
        logger.info(f"Loaded {len(suppliers)} suppliers")
        
        logger.info("Loading route data...")
        routes = RouteLoader.load_routes()
        logger.info(f"Loaded {len(routes)} routes")
        
        logger.info("Loading port data...")
        ports = PortLoader.load_ports()
        logger.info(f"Loaded {len(ports)} ports")
        
        logger.info("Loading corridor data...")
        corridors = CorridorLoader.load_corridors()
        logger.info(f"Loaded {len(corridors)} corridors")
        
        logger.info("Seeding geopolitical events...")
        seed_geopolitical_events(db)
        
        logger.info("=" * 60)
        logger.info("PHASE 2: DATA LAYER SEEDING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"✓ {len(suppliers)} suppliers loaded")
        logger.info(f"✓ {len(routes)} routes loaded")
        logger.info(f"✓ {len(ports)} ports loaded")
        logger.info(f"✓ {len(corridors)} corridors loaded")
        logger.info(f"✓ Sample geopolitical events seeded")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
