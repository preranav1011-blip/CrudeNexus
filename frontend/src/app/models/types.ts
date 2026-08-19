/**
 * Frontend data types
 */
export interface GeopoliticalEvent {
  event_id: string;
  timestamp: string;
  location: string;
  description: string;
  severity: number;
}

export interface Supplier {
  supplier_id: string;
  supplier_name: string;
  production_capacity_mbd: number;
}

export interface ProcurementStrategy {
  strategy_id: string;
  strategy_type: string;
  total_cost: number;
  avg_risk_score: number;
}
