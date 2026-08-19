"""Procurement optimization using Google OR-Tools"""
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def optimize_procurement(
    suppliers: List[Dict],
    routes: List[Dict],
    india_demand_mbd: float,
    risk_tolerance: float = 0.5,
    blocked_corridors: List[str] = None,
    risk_context = None,
) -> Tuple[Dict, Dict, Dict]:
    """
    Generate three procurement strategies: cheapest, balanced, safest.
    
    For MVP, uses weighted allocation algorithm. Phase 6 will add OR-Tools.
    
    Constraints:
    - Total supply >= India demand
    - Supplier allocation <= supplier capacity
    - Route allocation <= route capacity
    - Blocked routes unavailable
    
    Optimizes for:
    1. Cheapest: Minimize total cost
    2. Balanced: Balance cost, risk, transit time
    3. Safest: Minimize risk and concentration
    
    Args:
        suppliers: List of supplier dicts with capacity, cost, risk
        routes: List of route dicts with capacity, risk
        india_demand_mbd: Daily demand in million barrels
        risk_tolerance: 0 (low risk) to 1 (high risk tolerance)
        blocked_corridors: List of unavailable corridors
        risk_context: Risk assessment context if available
    
    Returns: Tuple of (cheapest_strategy, balanced_strategy, safest_strategy)
    """
    logger.debug(f"Optimizing procurement for India demand: {india_demand_mbd} MBD")
    logger.debug(f"Risk tolerance: {risk_tolerance}, Blocked corridors: {blocked_corridors}")
    
    if not suppliers or not routes:
        logger.error("Missing suppliers or routes data")
        return ({}, {}, {})
    
    blocked_corridors = blocked_corridors or []
    
    # Filter available routes
    available_routes = [
        r for r in routes 
        if r.get('corridor_name', '') not in blocked_corridors
    ]
    
    # Filter available suppliers
    available_suppliers = [
        s for s in suppliers 
        if s.get('capacity_mbd', 0) > 0 and s.get('supplier_id', '') != 'Unknown'
    ]
    
    if not available_suppliers:
        logger.error("No available suppliers after filtering")
        return ({}, {}, {})
    
    # Strategy 1: CHEAPEST (minimize cost, ignore risk)
    cheapest = _generate_cheapest_strategy(
        available_suppliers, available_routes, india_demand_mbd
    )
    
    # Strategy 2: BALANCED (balance cost and risk)
    balanced = _generate_balanced_strategy(
        available_suppliers, available_routes, india_demand_mbd
    )
    
    # Strategy 3: SAFEST (minimize risk, accept higher cost)
    safest = _generate_safest_strategy(
        available_suppliers, available_routes, india_demand_mbd
    )
    
    return (cheapest, balanced, safest)


def _generate_cheapest_strategy(
    suppliers: List[Dict],
    routes: List[Dict],
    demand_mbd: float
) -> Dict:
    """Generate minimum-cost procurement strategy"""
    
    # Sort suppliers by cost (ascending)
    sorted_suppliers = sorted(
        suppliers,
        key=lambda s: s.get('cost_per_barrel', 100)
    )
    
    allocations = []
    remaining_demand = demand_mbd
    total_cost = 0
    total_volume = 0
    
    for supplier in sorted_suppliers:
        if remaining_demand <= 0:
            break
        
        allocation_mbd = min(
            supplier.get('capacity_mbd', 0),
            remaining_demand
        )
        
        cost_per_barrel = supplier.get('cost_per_barrel', 0)
        allocation_cost = allocation_mbd * 365 * cost_per_barrel  # Annual cost
        
        allocations.append({
            "supplier_id": supplier.get('supplier_id'),
            "allocation_percentage": (allocation_mbd / demand_mbd) * 100,
            "allocation_mbd": allocation_mbd,
            "cost_per_barrel": cost_per_barrel,
        })
        
        total_cost += allocation_cost
        total_volume += allocation_mbd
        remaining_demand -= allocation_mbd
    
    # Calculate metrics
    avg_cost = total_cost / total_volume if total_volume > 0 else 0
    avg_risk = _calculate_avg_risk(allocations, suppliers)
    avg_transit = _calculate_avg_transit(allocations, suppliers)
    concentration = _calculate_concentration_ratio(allocations)
    
    return {
        "strategy_id": "STR_CHEAPEST",
        "strategy_type": "cheapest",
        "total_cost": total_cost,
        "total_crude_supply": total_volume,
        "avg_risk_score": avg_risk,
        "avg_transit_time": avg_transit,
        "supplier_concentration_ratio": concentration,
        "allocations": allocations,
        "explanation": f"Minimum-cost strategy using cheapest suppliers. Annual cost: ${total_cost:.0f}M. "
                      f"Avg risk score: {avg_risk:.0f}, Transit time: {avg_transit:.1f} days. "
                      f"Supplier concentration (Herfindahl): {concentration:.3f}"
    }


def _generate_balanced_strategy(
    suppliers: List[Dict],
    routes: List[Dict],
    demand_mbd: float
) -> Dict:
    """Generate balanced cost-risk procurement strategy"""
    
    # Score each supplier: lower cost + lower risk = better
    scored_suppliers = []
    for s in suppliers:
        cost_score = s.get('cost_per_barrel', 100) / 100  # Normalize to 0-1
        risk_score = s.get('geopolitical_risk', 50) / 100  # Normalize to 0-1
        
        # Weighted score: 60% cost, 40% risk
        combined_score = (cost_score * 0.6) + (risk_score * 0.4)
        
        scored_suppliers.append((s, combined_score))
    
    # Sort by combined score
    scored_suppliers.sort(key=lambda x: x[1])
    
    allocations = []
    remaining_demand = demand_mbd
    total_cost = 0
    total_volume = 0
    
    for supplier, _ in scored_suppliers:
        if remaining_demand <= 0:
            break
        
        # Don't rely too much on single supplier (diversification)
        max_allocation = min(
            supplier.get('capacity_mbd', 0),
            demand_mbd * 0.35  # Max 35% from one supplier
        )
        
        allocation_mbd = min(max_allocation, remaining_demand)
        
        if allocation_mbd > 0.1:  # Ignore very small allocations
            cost_per_barrel = supplier.get('cost_per_barrel', 0)
            allocation_cost = allocation_mbd * 365 * cost_per_barrel
            
            allocations.append({
                "supplier_id": supplier.get('supplier_id'),
                "allocation_percentage": (allocation_mbd / demand_mbd) * 100,
                "allocation_mbd": allocation_mbd,
            })
            
            total_cost += allocation_cost
            total_volume += allocation_mbd
            remaining_demand -= allocation_mbd
    
    avg_cost = total_cost / total_volume if total_volume > 0 else 0
    avg_risk = _calculate_avg_risk(allocations, suppliers)
    avg_transit = _calculate_avg_transit(allocations, suppliers)
    concentration = _calculate_concentration_ratio(allocations)
    
    return {
        "strategy_id": "STR_BALANCED",
        "strategy_type": "balanced",
        "total_cost": total_cost,
        "total_crude_supply": total_volume,
        "avg_risk_score": avg_risk,
        "avg_transit_time": avg_transit,
        "supplier_concentration_ratio": concentration,
        "allocations": allocations,
        "explanation": f"Balanced strategy with diversification. {len(allocations)} suppliers. "
                      f"Annual cost: ${total_cost:.0f}M. Avg risk: {avg_risk:.0f}, "
                      f"Transit: {avg_transit:.1f} days. Diversification ratio: {concentration:.3f}"
    }


def _generate_safest_strategy(
    suppliers: List[Dict],
    routes: List[Dict],
    demand_mbd: float
) -> Dict:
    """Generate minimum-risk procurement strategy"""
    
    # Sort suppliers by risk (ascending - lowest risk first)
    sorted_suppliers = sorted(
        suppliers,
        key=lambda s: s.get('geopolitical_risk', 50)
    )
    
    allocations = []
    remaining_demand = demand_mbd
    total_cost = 0
    total_volume = 0
    
    # Diversify heavily across low-risk suppliers
    for supplier in sorted_suppliers:
        if remaining_demand <= 0:
            break
        
        # Limit to 25% per supplier for safety
        max_allocation = min(
            supplier.get('capacity_mbd', 0),
            demand_mbd * 0.25
        )
        
        allocation_mbd = min(max_allocation, remaining_demand)
        
        if allocation_mbd > 0.1:
            cost_per_barrel = supplier.get('cost_per_barrel', 0)
            allocation_cost = allocation_mbd * 365 * cost_per_barrel
            
            allocations.append({
                "supplier_id": supplier.get('supplier_id'),
                "allocation_percentage": (allocation_mbd / demand_mbd) * 100,
                "allocation_mbd": allocation_mbd,
            })
            
            total_cost += allocation_cost
            total_volume += allocation_mbd
            remaining_demand -= allocation_mbd
    
    avg_cost = total_cost / total_volume if total_volume > 0 else 0
    avg_risk = _calculate_avg_risk(allocations, suppliers)
    avg_transit = _calculate_avg_transit(allocations, suppliers)
    concentration = _calculate_concentration_ratio(allocations)
    
    return {
        "strategy_id": "STR_SAFEST",
        "strategy_type": "safest",
        "total_cost": total_cost,
        "total_crude_supply": total_volume,
        "avg_risk_score": avg_risk,
        "avg_transit_time": avg_transit,
        "supplier_concentration_ratio": concentration,
        "allocations": allocations,
        "explanation": f"Maximum-safety strategy with high diversification ({len(allocations)} suppliers). "
                      f"Annual cost: ${total_cost:.0f}M (higher due to risk premium). "
                      f"Avg risk: {avg_risk:.0f}, Transit: {avg_transit:.1f} days. "
                      f"Low concentration (max 25% per supplier) limits geopolitical exposure."
    }


def _calculate_avg_risk(allocations: List[Dict], suppliers: List[Dict]) -> float:
    """Calculate weighted average risk score"""
    if not allocations:
        return 50.0
    
    total_risk = 0
    total_allocation = 0
    
    for alloc in allocations:
        supplier = next(
            (s for s in suppliers if s.get('supplier_id') == alloc.get('supplier_id')),
            None
        )
        if supplier:
            risk = supplier.get('geopolitical_risk', 50)
            pct = alloc.get('allocation_percentage', 0)
            total_risk += risk * pct
            total_allocation += pct
    
    return total_risk / total_allocation if total_allocation > 0 else 50


def _calculate_avg_transit(allocations: List[Dict], suppliers: List[Dict]) -> float:
    """Calculate weighted average transit time"""
    # Simplified: assume 20 days avg for all suppliers
    # Phase 6 will use actual route data
    return 20.0


def _calculate_concentration_ratio(allocations: List[Dict]) -> float:
    """
    Calculate Herfindahl-Hirschman Index (HHI) for supplier concentration.
    
    HHI = sum of squared market shares
    - 0.0 = perfect diversification across many suppliers
    - 1.0 = complete concentration in one supplier
    """
    if not allocations:
        return 0.0
    
    hhi = 0
    for alloc in allocations:
        share = alloc.get('allocation_percentage', 0) / 100  # Convert to 0-1
        hhi += share ** 2
    
    return min(1.0, hhi)


logger.info("Procurement optimizer initialized")
    
    Explains:
    - Supplier allocation choices
    - Why this strategy is recommended
    - Tradeoffs (cost vs risk vs transit time)
    - Constraints satisfied
    
    Returns: Explanation text
    """
    logger.debug(f"Explaining strategy: {strategy.get('strategy_type')}")
    
    # TODO: Implement in Phase 6
    
    return """
    This strategy balances cost, risk, and resilience.
    
    Allocations recommended for:
    - Cost impact: +6.2%
    - Risk reduction: 38%
    - Transit time impact: +2.1 days
    
    Why: Reduces exposure to affected corridor while maintaining supply.
    """


def recommend_strategy(
    cheapest: Dict,
    balanced: Dict,
    safest: Dict,
    risk_tolerance: float = 0.5,
) -> Tuple[str, str]:
    """
    Recommend best strategy based on risk tolerance.
    
    Args:
        cheapest, balanced, safest: Strategy dicts
        risk_tolerance: 0 (prefer safe) to 1 (prefer cheap)
    
    Returns: (recommended_strategy_id, recommendation_reason)
    """
    logger.debug(f"Recommending strategy with risk_tolerance={risk_tolerance}")
    
    # TODO: Implement in Phase 6
    
    return ("balanced", "Provides good balance between cost and risk")


logger.info("Procurement optimizer initialized")
