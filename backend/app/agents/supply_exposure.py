"""Data-driven supply-chain graph and corridor exposure analysis."""
from __future__ import annotations

import logging
from typing import Any, Dict

import networkx as nx

from app.data.csv_loaders import CorridorLoader, PortLoader, RouteLoader, SupplierLoader
from app.data.mock_sources import get_mock_india_crude_demand

logger = logging.getLogger(__name__)
_ALIASES = {"strait of hormuz": "Hormuz", "suez canal": "Suez", "red sea route": "Red Sea"}


def _canonical_corridor(name: str) -> str:
    return _ALIASES.get(name.strip().lower(), name.strip())


def calculate_supply_exposure(corridor: str, risk_score: float = 50, event=None) -> Dict:
    """Measure exposed import share and viable alternatives using corridor master data."""
    name = _canonical_corridor(corridor)
    details = next((item for item in CorridorLoader.load_corridors() if item["corridor_name"].lower() == name.lower()), None)
    if not details:
        return {"exposed_percentage": 0, "affected_suppliers": [], "affected_routes": [], "exposed_volume_mbd": 0,
                "additional_cost": 0, "additional_transit_time": 0, "alternative_capacity": 0}
    routes = RouteLoader.load_routes()
    affected_routes = details["affected_routes"] or [route["route_id"] for route in routes if route["corridor_name"].lower() == name.lower()]
    alternatives = [route for route in routes if route["route_id"] not in affected_routes and not route["is_blocked"]]
    exposure_pct = float(details["india_import_percentage"])
    demand = get_mock_india_crude_demand()
    base_transit = [route["transit_days"] for route in routes if route["route_id"] in affected_routes]
    alternative_transit = [route["transit_days"] for route in alternatives]
    return {"exposed_percentage": exposure_pct, "affected_suppliers": details["affected_suppliers"], "affected_routes": affected_routes,
            "exposed_volume_mbd": demand * exposure_pct / 100, "additional_cost": max(0, min(1, risk_score / 100)) * 5,
            "additional_transit_time": max(0, (sum(alternative_transit) / len(alternative_transit) if alternative_transit else 0) - (sum(base_transit) / len(base_transit) if base_transit else 0)),
            "alternative_capacity": sum(route["capacity_mbd"] for route in alternatives)}


def build_supply_chain_graph() -> nx.MultiDiGraph:
    """Build supplier → origin port → import port → India graph with route attributes."""
    graph = nx.MultiDiGraph()
    suppliers, ports, routes = SupplierLoader.load_suppliers(), PortLoader.load_ports(), RouteLoader.load_routes()
    for supplier in suppliers:
        graph.add_node(f"supplier_{supplier['supplier_id']}", type="supplier", **supplier)
    for port in ports:
        graph.add_node(f"port_{port['port_id']}", type="port", **port)
    graph.add_node("india_demand", type="demand", capacity_mbd=get_mock_india_crude_demand())
    ports_by_name = {port["port_name"]: port for port in ports}
    for route in routes:
        origin, destination = ports_by_name.get(route["origin"]), ports_by_name.get(route["destination"])
        supplier = next((item for item in suppliers if origin and item["country"] == origin["country"]), None)
        if not (origin and destination and supplier):
            continue
        attributes = {key: value for key, value in route.items() if key != "route_id"}
        graph.add_edge(f"supplier_{supplier['supplier_id']}", f"port_{origin['port_id']}", key=f"supply_{route['route_id']}", route_id=route["route_id"], **attributes)
        graph.add_edge(f"port_{origin['port_id']}", f"port_{destination['port_id']}", key=route["route_id"], route_id=route["route_id"], **attributes)
        graph.add_edge(f"port_{destination['port_id']}", "india_demand", key=f"import_{route['route_id']}", route_id=route["route_id"], capacity_mbd=route["capacity_mbd"])
    logger.info("Built supply graph with %d nodes and %d edges", graph.number_of_nodes(), graph.number_of_edges())
    return graph
