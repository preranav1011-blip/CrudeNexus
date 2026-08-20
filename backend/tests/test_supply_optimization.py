import pytest

from app.agents.procurement_optimizer import optimize_procurement, recommend_strategy
from app.agents.supply_exposure import build_supply_chain_graph, calculate_supply_exposure
from app.data.csv_loaders import RouteLoader, SupplierLoader


def test_supply_graph_contains_route_paths():
    graph = build_supply_chain_graph()
    assert graph.number_of_nodes() >= 20
    assert graph.number_of_edges() >= 18
    assert graph.has_node("india_demand")


def test_exposure_uses_corridor_master_data():
    exposure = calculate_supply_exposure("Strait of Hormuz", risk_score=80)
    assert exposure["exposed_percentage"] == 55
    assert exposure["exposed_volume_mbd"] == pytest.approx(2.475)
    assert set(exposure["affected_routes"]) == {"R001", "R002", "R005", "R006"}


def test_ortools_strategies_respect_blocked_corridor_and_demand():
    suppliers, routes = SupplierLoader.load_suppliers(), RouteLoader.load_routes()
    cheapest, balanced, safest = optimize_procurement(suppliers, routes, 4.5, blocked_corridors=["Hormuz"])
    for strategy in (cheapest, balanced, safest):
        assert strategy["total_crude_supply"] == pytest.approx(4.5)
        assert all(item["corridor"] != "Hormuz" for item in strategy["allocations"])
        assert strategy["allocations"]
    assert balanced["supplier_concentration_ratio"] <= cheapest["supplier_concentration_ratio"]
    recommendation, _ = recommend_strategy(cheapest, balanced, safest, risk_tolerance=.1)
    assert recommendation == safest["strategy_id"]
