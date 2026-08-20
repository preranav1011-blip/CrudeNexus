"""Route-feasible multi-strategy procurement optimization using OR-Tools."""
from __future__ import annotations

import logging
from typing import Dict, List, Tuple

from ortools.linear_solver import pywraplp

logger = logging.getLogger(__name__)


def _supplier_for_route(route: Dict, suppliers: List[Dict]) -> Dict | None:
    """Resolve a route origin port to a supplier country from prototype data."""
    origin = route.get("origin", "").strip().lower()
    ports = {"ras tanura": "saudi arabia", "novorossiysk": "russia", "kharg island": "iran",
             "abu dhabi": "uae", "houston": "usa", "baku": "azerbaijan"}
    country = ports.get(origin)
    return next((supplier for supplier in suppliers if supplier.get("country", "").lower() == country), None)


def _available_options(suppliers: List[Dict], routes: List[Dict], blocked_corridors: List[str], risk_context) -> List[Dict]:
    blocked = {item.lower().strip() for item in blocked_corridors}
    context_corridor = getattr(risk_context, "corridor_name", "").lower() if risk_context else ""
    context_risk = float(getattr(risk_context, "risk_score_ml", 0) or 0) if risk_context else 0
    options = []
    for route in routes:
        corridor = route.get("corridor_name", "").lower()
        if route.get("is_blocked") or corridor in blocked:
            continue
        supplier = _supplier_for_route(route, suppliers)
        if not supplier or supplier.get("capacity_mbd", 0) <= 0 or route.get("capacity_mbd", 0) <= 0:
            continue
        route_risk = float(route.get("geopolitical_risk_score", 50))
        if corridor == context_corridor:
            route_risk = min(100, route_risk + context_risk * .5)
        options.append({"route": route, "supplier": supplier, "capacity": min(float(route["capacity_mbd"]), float(supplier["capacity_mbd"])),
                        "risk": (float(supplier.get("geopolitical_risk", 50)) + route_risk) / 2})
    return options


def _solve(strategy_type: str, options: List[Dict], demand: float, risk_tolerance: float) -> Dict:
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        raise RuntimeError("OR-Tools SCIP solver is unavailable")
    volumes = [solver.NumVar(0, option["capacity"], f"volume_{index}") for index, option in enumerate(options)]
    solver.Add(solver.Sum(volumes) == demand)
    suppliers = {option["supplier"]["supplier_id"] for option in options}
    diversification_cap = demand * (.40 if strategy_type == "balanced" else .30)
    use_diversification_cap = strategy_type in {"balanced", "safest"} and diversification_cap * len(suppliers) >= demand
    for supplier_id in suppliers:
        indices = [index for index, option in enumerate(options) if option["supplier"]["supplier_id"] == supplier_id]
        capacity = min(option["supplier"]["capacity_mbd"] for option in (options[i] for i in indices))
        solver.Add(solver.Sum(volumes[i] for i in indices) <= capacity)
        if use_diversification_cap:
            solver.Add(solver.Sum(volumes[i] for i in indices) <= diversification_cap)

    objective = solver.Objective()
    for variable, option in zip(volumes, options):
        cost = float(option["supplier"]["cost_per_barrel"])
        risk, transit = option["risk"], float(option["route"]["transit_days"])
        if strategy_type == "cheapest":
            coefficient = cost
        elif strategy_type == "balanced":
            coefficient = cost * (.55 + .20 * risk_tolerance) + risk * (1 - risk_tolerance) * .65 + transit * .12
        else:
            coefficient = risk * 1.5 + transit * .16 + cost * .08
        objective.SetCoefficient(variable, coefficient)
    objective.SetMinimization()
    if solver.Solve() not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        raise ValueError(f"No feasible {strategy_type} strategy for {demand} MBD after route constraints")

    allocations = []
    for variable, option in zip(volumes, options):
        volume = variable.solution_value()
        if volume < .0001:
            continue
        supplier, route = option["supplier"], option["route"]
        allocations.append({"supplier_id": supplier["supplier_id"], "route_id": route["route_id"], "corridor": route["corridor_name"],
                            "allocation_percentage": volume / demand * 100, "allocation_mbd": volume,
                            "allocated_volume_mbd": volume, "cost_per_barrel": supplier["cost_per_barrel"],
                            "allocated_cost": volume * 365 * supplier["cost_per_barrel"], "risk_score": option["risk"],
                            "transit_days": route["transit_days"]})
    total_cost = sum(item["allocated_cost"] for item in allocations)
    total_volume = sum(item["allocation_mbd"] for item in allocations)
    avg_risk = sum(item["allocation_mbd"] * item["risk_score"] for item in allocations) / total_volume
    avg_transit = sum(item["allocation_mbd"] * item["transit_days"] for item in allocations) / total_volume
    by_supplier = {}
    for item in allocations:
        by_supplier[item["supplier_id"]] = by_supplier.get(item["supplier_id"], 0) + item["allocation_mbd"] / demand
    concentration = sum(share ** 2 for share in by_supplier.values())
    return {"strategy_id": f"STR_{strategy_type.upper()}", "strategy_type": strategy_type, "total_cost": total_cost,
            "total_crude_supply": total_volume, "avg_risk_score": avg_risk, "avg_transit_time": avg_transit,
            "supplier_concentration_ratio": concentration, "allocations": allocations,
            "explanation": f"{strategy_type.title()} OR-Tools strategy meets {demand:.2f} MBD through {len(allocations)} route allocations. "
                           f"Annual cost ${total_cost:,.0f}; risk {avg_risk:.1f}/100; concentration {concentration:.3f}."}


def optimize_procurement(suppliers: List[Dict], routes: List[Dict], india_demand_mbd: float,
                         risk_tolerance: float = .5, blocked_corridors: List[str] | None = None,
                         risk_context=None) -> Tuple[Dict, Dict, Dict]:
    """Generate cheapest, balanced, and safest strategies under supply/route constraints."""
    if india_demand_mbd <= 0:
        raise ValueError("india_demand_mbd must be positive")
    options = _available_options(suppliers, routes, blocked_corridors or [], risk_context)
    if not options:
        raise ValueError("No usable supplier-route options remain")
    if sum(item["capacity"] for item in options) < india_demand_mbd:
        raise ValueError("Available route capacity cannot meet India demand")
    return tuple(_solve(name, options, india_demand_mbd, risk_tolerance) for name in ("cheapest", "balanced", "safest"))


def explain_strategy(strategy: Dict) -> str:
    return strategy.get("explanation", "No explanation available.")


def recommend_strategy(cheapest: Dict, balanced: Dict, safest: Dict, risk_tolerance: float = .5) -> Tuple[str, str]:
    selected = cheapest if risk_tolerance >= .75 else safest if risk_tolerance <= .25 else balanced
    return selected["strategy_id"], f"Selected {selected['strategy_type']} for risk tolerance {risk_tolerance:.2f}."
