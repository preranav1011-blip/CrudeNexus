export interface GeopoliticalEvent {
  event_id: string; timestamp: string; event_type: string; location: string;
  description?: string; severity_raw?: number; affected_corridor?: string;
  india_relevance?: number; raw_confidence?: number;
}
export interface CorridorRisk { corridor_id: string; corridor_name: string; location: string; risk_score: number; risk_confidence: number; disruption_probability: number; india_exposure_pct: number; }
export interface RiskSummary { total_corridors: number; corridors: CorridorRisk[]; highest_risk: number; average_risk: number; }
export interface Allocation { supplier_id: string; route_id?: string; allocation_percentage: number; allocated_volume_mbd: number; allocated_cost: number; }
export interface ProcurementStrategy { strategy_id: string; strategy_type: string; total_cost: number; total_crude_supply: number; avg_risk_score: number; avg_transit_time: number; supplier_concentration_ratio: number; allocations: Allocation[]; explanation?: string; }
export interface OptimizationResults { cheapest: ProcurementStrategy; balanced: ProcurementStrategy; safest: ProcurementStrategy; recommended: string; recommendation_reason: string; }
export interface Route { route_id: string; origin: string; destination: string; corridor_name: string; transit_days: number; capacity_mbd: number; geopolitical_risk_score: number; }
