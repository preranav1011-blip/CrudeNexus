import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { GeopoliticalEvent, OptimizationResults, RiskSummary, Route } from '../models/types';

@Injectable({ providedIn: 'root' })
export class DataService {
  readonly events = new BehaviorSubject<GeopoliticalEvent[]>([]);
  readonly risks = new BehaviorSubject<RiskSummary | null>(null);
  readonly routes = new BehaviorSubject<Route[]>([]);
  readonly strategies = new BehaviorSubject<OptimizationResults | null>(null);
}
