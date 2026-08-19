"""Supply chain exposure analysis"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def calculate_supply_exposure(
    corridor: str,
    risk_score: float = 50,
    event = None,
) -> Dict:
    """
    Calculate how much of India's crude procurement is exposed to a disruption.
    
    Returns:
    {
        "exposed_percentage": 0-100,
        "affected_suppliers": ["S001", "S002", ...],
        "affected_routes": ["R001", "R002", ...],
        "exposed_volume_mbd": float,
        "additional_cost": float,
        "additional_transit_time": float,
        "alternative_capacity": float
    }
    """
    logger.debug(f"Calculating supply exposure for corridor: {corridor}")
    
    # Map corridors to affected suppliers and routes
    corridor_mapping = {
        "Strait of Hormuz": {
            "affected_suppliers": ["S003", "S004", "S005"],  # Iran, UAE, Kuwait
            "affected_routes": ["R004", "R005", "R006", "R007"],
            "exposed_pct": 45.0,
            "exposed_volume": 2.0,
        },
        "Suez Canal": {
            "affected_suppliers": ["S001"],  # Saudi Arabia
            "affected_routes": ["R001", "R002"],
            "exposed_pct": 30.0,
            "exposed_volume": 1.35,
        },
        "Red Sea Route": {
            "affected_suppliers": ["S001"],  # Saudi Arabia
            "affected_routes": ["R001", "R002"],
            "exposed_pct": 20.0,
            "exposed_volume": 0.9,
        },
        "Cape of Good Hope": {
            "affected_suppliers": ["S002"],  # Russia
            "affected_routes": ["R003"],
            "exposed_pct": 5.0,
            "exposed_volume": 0.28,
        },
        "Malacca Strait": {
            "affected_suppliers": [],
            "affected_routes": [],
            "exposed_pct": 0.0,
            "exposed_volume": 0.0,
        },
    }
    
    mapping = corridor_mapping.get(corridor, {
        "affected_suppliers": [],
        "affected_routes": [],
        "exposed_pct": 0,
        "exposed_volume": 0,
    })
    
    # Calculate alternative sources cost premium
    # Higher risk score = longer search time = higher cost
    additional_cost_per_barrel = (risk_score / 100) * 5.0  # Up to $5/barrel premium
    
    # Calculate additional transit time
    alternative_transit_days = 30 + (risk_score / 100) * 10  # 30-40 days
    
    return {
        "exposed_percentage": mapping.get("exposed_pct", 0),
        "affected_suppliers": mapping.get("affected_suppliers", []),
        "affected_routes": mapping.get("affected_routes", []),
        "exposed_volume_mbd": mapping.get("exposed_volume", 0),
        "additional_cost": additional_cost_per_barrel,
        "additional_transit_time": alternative_transit_days - 20,  # Delta vs normal
        "alternative_capacity": 5.0,  # Placeholder: assume 5 MBD alternative capacity
    }


def build_supply_chain_graph():
    """
    Build NetworkX graph representation of India's crude supply network.
    
    Nodes: Suppliers, Ports, Routes, India demand
    Edges: Supply paths with capacity/risk attributes
    
    Returns: NetworkX DiGraph
    """
    logger.debug("Building supply chain graph")
    
    try:
        import networkx as nx
        from app.data.csv_loaders import SupplierLoader, RouteLoader, PortLoader, CorridorLoader
        
        G = nx.DiGraph()
        
        # Load data
        suppliers = SupplierLoader.load_suppliers()
        routes = RouteLoader.load_routes()
        ports = PortLoader.load_ports()
        corridors = CorridorLoader.load_corridors()
        
        # Add supplier nodes
        for supplier in suppliers:
            G.add_node(
                f"supplier_{supplier.get('supplier_id')}",
                type="supplier",
                name=supplier.get('name', ''),
                country=supplier.get('country', ''),
                capacity=supplier.get('capacity_mbd', 0),
                cost=supplier.get('cost_per_barrel', 0),
                risk=supplier.get('geopolitical_risk', 50)
            )
        
        # Add port nodes
        for port in ports:
            G.add_node(
                f"port_{port.get('port_id')}",
                type="port",
                name=port.get('port_name', ''),
                country=port.get('country', ''),
                capacity=port.get('capacity_mbd', 0)
            )
        
        # Add India demand node
        G.add_node("india_demand", type="demand", capacity=4.5)
        
        # Add route edges (supplier -> port -> india)
        for route in routes:
            origin = route.get('origin', '')
            destination = route.get('destination', '')
            route_id = route.get('route_id', '')
            
            # Find matching supplier and port
            supplier = next((s for s in suppliers if s.get('country') == origin), None)
            port = next((p for p in ports if p.get('port_name') == destination), None)
            
            if supplier and port:
                supplier_node = f"supplier_{supplier.get('supplier_id')}"
                port_node = f"port_{port.get('port_id')}"
                
                G.add_edge(
                    supplier_node, port_node,
                    route_id=route_id,
                    distance=route.get('distance_km', 0),
                    transit_days=route.get('transit_days', 0),
                    capacity=route.get('capacity_mbd', 0),
                    corridor=route.get('corridor_name', ''),
                    risk=route.get('geopolitical_risk_score', 50)
                )
                
                # Add edge from port to India demand
                G.add_edge(
                    port_node, "india_demand",
                    capacity=port.get('capacity_mbd', 0)
                )
        
        logger.info(f"Built supply chain graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        return G
        
    except Exception as e:
        logger.error(f"Error building supply chain graph: {e}")
        return None


logger.info("Supply exposure analysis agent initialized")
