import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { GeopoliticalEvent, OptimizationResults, RiskSummary, Route } from '../models/types';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = '/api';
  constructor(private readonly http: HttpClient) {}
  events(): Observable<{ events: GeopoliticalEvent[]; total: number }> { return this.http.get<{ events: GeopoliticalEvent[]; total: number }>(`${this.baseUrl}/events`); }
  createEvent(description: string): Observable<GeopoliticalEvent> { return this.http.post<GeopoliticalEvent>(`${this.baseUrl}/events`, { description, source: 'DASHBOARD' }); }
  analyze(eventId: string): Observable<unknown> { return this.http.post(`${this.baseUrl}/analysis/risk`, null, { params: { event_id: eventId } }); }
  corridorRisks(): Observable<RiskSummary> { return this.http.get<RiskSummary>(`${this.baseUrl}/analysis/corridors/risk`); }
  routes(): Observable<Route[]> { return this.http.get<Route[]>(`${this.baseUrl}/data/routes`); }
  strategies(riskTolerance: number, blockedCorridors: string[] = []): Observable<OptimizationResults> {
    return this.http.post<OptimizationResults>(`${this.baseUrl}/optimization/strategies`, { risk_tolerance: riskTolerance, blocked_corridors: blockedCorridors });
  }
}
