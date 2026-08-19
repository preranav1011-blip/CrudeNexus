"""CSV data loader for suppliers, routes, ports, and corridors"""
import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from app.database.db import SessionLocal
from app.database.models import GeopoliticalEvent
from datetime import datetime

logger = logging.getLogger(__name__)

# Get the data directory path
DATA_DIR = Path(__file__).parent.parent.parent / "data"


class SupplierLoader:
    """Load supplier data from CSV"""
    
    @staticmethod
    def load_suppliers() -> List[Dict[str, Any]]:
        """Load suppliers from CSV file"""
        suppliers = []
        csv_path = DATA_DIR / "suppliers.csv"
        
        if not csv_path.exists():
            logger.warning(f"Suppliers CSV not found at {csv_path}")
            return suppliers
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Normalize column names
                    supplier = {
                        'supplier_id': row.get('supplier_id') or row.get('supplier_id'),
                        'name': row.get('supplier_name', 'Unknown'),
                        'country': row.get('supplier_country', ''),
                        'capacity_mbd': float(row.get('production_capacity_mbd', 0)),
                        'cost_per_barrel': float(row.get('estimated_cost_per_barrel', 0)),
                        'geopolitical_risk': float(row.get('geopolitical_baseline_risk_score', 50)),
                    }
                    suppliers.append(supplier)
            logger.info(f"Loaded {len(suppliers)} suppliers from CSV")
        except Exception as e:
            logger.error(f"Error loading suppliers CSV: {e}")
        
        return suppliers


class RouteLoader:
    """Load route data from CSV"""
    
    @staticmethod
    def load_routes() -> List[Dict[str, Any]]:
        """Load routes from CSV file"""
        routes = []
        csv_path = DATA_DIR / "routes.csv"
        
        if not csv_path.exists():
            logger.warning(f"Routes CSV not found at {csv_path}")
            return routes
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    route = {
                        'route_id': row.get('route_id', ''),
                        'route_name': row.get('route_name', ''),
                        'origin': row.get('origin_port') or row.get('origin', ''),
                        'destination': row.get('destination_port') or row.get('destination', ''),
                        'corridor_name': row.get('corridor') or row.get('corridor_name', ''),
                        'distance_km': float(row.get('distance_km', 0)),
                        'transit_days': float(row.get('transit_time_days') or row.get('transit_days', 0)),
                        'capacity_mbd': float(row.get('capacity_mbd', 0)),
                        'chokepoint': row.get('corridor') or row.get('chokepoint', ''),
                        'geopolitical_risk_score': float(
                            row.get('baseline_risk_score') or row.get('geopolitical_risk_score', 50)
                        ),
                        'is_blocked': (row.get('is_blocked', '0').strip().lower() in {'1', 'true', 'yes'}),
                    }
                    routes.append(route)
            logger.info(f"Loaded {len(routes)} routes from CSV")
        except Exception as e:
            logger.error(f"Error loading routes CSV: {e}")
        
        return routes


class PortLoader:
    """Load port data from CSV"""
    
    @staticmethod
    def load_ports() -> List[Dict[str, Any]]:
        """Load ports from CSV file"""
        ports = []
        csv_path = DATA_DIR / "ports.csv"
        
        if not csv_path.exists():
            logger.warning(f"Ports CSV not found at {csv_path}")
            return ports
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    port = {
                        'port_id': row.get('port_id', ''),
                        'country': row.get('country', ''),
                        'port_name': row.get('port_name', ''),
                        'port_type': row.get('port_type', ''),
                        'capacity_mbd': float(row.get('capacity_mbd', 0)),
                        'draft_constraints': float(row.get('draft_constraints', 12)),
                        'infrastructure_quality': row.get('infrastructure_quality', 'fair'),
                        'trade_volume_2023_mbd': float(row.get('trade_volume_2023_mbd', 0)),
                    }
                    ports.append(port)
            logger.info(f"Loaded {len(ports)} ports from CSV")
        except Exception as e:
            logger.error(f"Error loading ports CSV: {e}")
        
        return ports


class CorridorLoader:
    """Load corridor data from CSV"""
    
    @staticmethod
    def load_corridors() -> List[Dict[str, Any]]:
        """Load corridors from CSV file"""
        corridors = []
        csv_path = DATA_DIR / "corridors.csv"
        
        if not csv_path.exists():
            logger.warning(f"Corridors CSV not found at {csv_path}")
            return corridors
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    corridor = {
                        'corridor_id': row.get('corridor_id') or row.get('corridor_name', ''),
                        'corridor_name': row.get('corridor_name', ''),
                        'location': row.get('location', ''),
                        'transit_countries': row.get('transit_countries', '').split(';'),
                        'chokepoint_type': row.get('chokepoint_type', ''),
                        'annual_traffic_pct_india': float(row.get('annual_traffic_pct_india', 0)),
                        'risk_trigger_events': row.get('risk_trigger_events', '').split(';'),
                        'historical_disruptions': row.get('historical_disruptions', '').split(';'),
                    }
                    corridors.append(corridor)
            logger.info(f"Loaded {len(corridors)} corridors from CSV")
        except Exception as e:
            logger.error(f"Error loading corridors CSV: {e}")
        
        return corridors


class EventLoader:
    """Load event data from JSON"""
    
    @staticmethod
    def load_sample_events() -> List[Dict[str, Any]]:
        """Load sample geopolitical events from JSON file"""
        events = []
        json_path = DATA_DIR / "sample_events.json"
        
        if not json_path.exists():
            logger.warning(f"Sample events JSON not found at {json_path}")
            return events
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    events = data
                else:
                    events = [data]
            logger.info(f"Loaded {len(events)} sample events from JSON")
        except Exception as e:
            logger.error(f"Error loading sample events JSON: {e}")
        
        return events


def seed_geopolitical_events(db_session):
    """Seed sample geopolitical events into database"""
    try:
        events_data = EventLoader.load_sample_events()
        
        for event_data in events_data:
            # Check if event already exists
            existing = db_session.query(GeopoliticalEvent).filter_by(
                event_id=event_data.get('event_id')
            ).first()
            
            if not existing:
                event = GeopoliticalEvent(
                    event_id=event_data.get('event_id'),
                    timestamp=datetime.fromisoformat(event_data.get('timestamp', '').replace('Z', '+00:00')),
                    event_type=event_data.get('event_type', ''),
                    location=event_data.get('location', ''),
                    description=event_data.get('description', ''),
                    severity_raw=float(event_data.get('severity_raw', 0.5)),
                    affected_corridor=event_data.get('affected_corridor', ''),
                    india_relevance=float(event_data.get('india_relevance', 0.5)),
                    source=event_data.get('source', 'SAMPLE_DATA'),
                    raw_confidence=float(event_data.get('raw_confidence', 0.7)),
                )
                db_session.add(event)
        
        db_session.commit()
        logger.info("Seeded geopolitical events successfully")
    except Exception as e:
        logger.error(f"Error seeding events: {e}")
        db_session.rollback()
        raise


logger.info("CSV loaders initialized")
