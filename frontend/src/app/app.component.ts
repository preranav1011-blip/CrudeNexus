import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { forkJoin } from 'rxjs';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProcurementComponent } from './procurement/procurement.component';
import { SupplyChainComponent } from './supply-chain/supply-chain.component';
import { ApiService } from './services/api.service';
import { DataService } from './services/data.service';

@Component({ selector: 'app-root', standalone: true, imports: [CommonModule, DashboardComponent, ProcurementComponent, SupplyChainComponent], template: `
  <div class="shell"><header><div><small>ENERGY RESILIENCE · INDIA</small><h1>CrudeNexus</h1></div><span [class.offline]="error">{{ error ? 'API attention needed' : 'Decision intelligence online' }}</span></header>
  <nav><button *ngFor="let item of tabs" (click)="view=item" [class.active]="view===item">{{ item }}</button></nav>
  <main><app-dashboard *ngIf="view==='Dashboard'" [events]="state.events.value" [risks]="state.risks.value" [loading]="eventLoading" [error]="eventError" (analyze)="analyze($event)"></app-dashboard>
  <app-procurement *ngIf="view==='Procurement'" [results]="state.strategies.value" [loading]="strategyLoading" [error]="strategyError" (generate)="generate($event)"></app-procurement>
  <app-supply-chain *ngIf="view==='Supply chain'" [routes]="state.routes.value"></app-supply-chain>
  <p class="error" *ngIf="error">{{ error }}</p></main></div>
`, styles: [`:host{display:block;min-height:100vh;background:#071321;color:#eff7ff;font-family:Inter,system-ui,sans-serif}.shell{max-width:1120px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #254260;padding-bottom:18px}small{color:#8fb1ca;letter-spacing:.08em}h1{margin:3px 0 0;font-size:32px}header span{color:#6de5b8;background:#123b39;padding:7px 10px;border-radius:20px;font-size:13px}.offline{color:#ffb19b;background:#4c2829}nav{display:flex;gap:8px;margin:18px 0}nav button{background:transparent;color:#b8d0e7;border:1px solid #254260;padding:8px 12px;border-radius:20px}.active{background:#26b4a6!important;color:#03141b!important;border-color:#26b4a6!important}.error{color:#ff9b83}`] })
export class AppComponent implements OnInit {
  readonly tabs = ['Dashboard', 'Procurement', 'Supply chain']; view = 'Dashboard'; error = ''; eventError = ''; strategyError = ''; eventLoading = false; strategyLoading = false;
  constructor(public readonly state: DataService, private readonly api: ApiService) {}
  ngOnInit(): void { this.refresh(); }
  refresh(): void { forkJoin({ events: this.api.events(), risks: this.api.corridorRisks(), routes: this.api.routes() }).subscribe({ next: data => { this.state.events.next(data.events.events); this.state.risks.next(data.risks); this.state.routes.next(data.routes); }, error: () => this.error = 'Cannot reach the backend. Start it on port 8000 and refresh.' }); }
  analyze(description: string): void { this.eventLoading = true; this.eventError = ''; this.api.createEvent(description).subscribe({ next: event => this.api.analyze(event.event_id).subscribe({ next: () => { this.eventLoading = false; this.refresh(); }, error: () => { this.eventLoading = false; this.eventError = 'The event was saved but risk analysis failed.'; } }), error: () => { this.eventLoading = false; this.eventError = 'Could not save the event.'; } }); }
  generate(riskTolerance: number): void { this.strategyLoading = true; this.strategyError = ''; this.api.strategies(riskTolerance).subscribe({ next: results => { this.state.strategies.next(results); this.strategyLoading = false; }, error: () => { this.strategyLoading = false; this.strategyError = 'Could not generate strategies. Check available route capacity.'; } }); }
}
