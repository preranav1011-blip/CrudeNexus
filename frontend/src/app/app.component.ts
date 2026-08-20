import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { forkJoin } from 'rxjs';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProcurementComponent } from './procurement/procurement.component';
import { SupplyChainComponent } from './supply-chain/supply-chain.component';
import { ApiService } from './services/api.service';
import { DataService } from './services/data.service';

@Component({ selector: 'app-root', standalone: true, imports: [CommonModule, DashboardComponent, ProcurementComponent, SupplyChainComponent], template: `
  <div class="app-shell">

  <aside class="sidebar">

    <div class="brand">
      <div class="brand-mark">CN</div>
      <div>
        <div class="brand-name">CrudeNexus</div>
        <div class="brand-subtitle">ENERGY INTELLIGENCE</div>
      </div>
    </div>

    <div class="nav-section">
      <div class="nav-label">PLATFORM</div>

      <button
        *ngFor="let item of tabs"
        class="nav-item"
        [class.active]="view === item"
        (click)="view = item"
      >
        <span class="nav-dot"></span>
        {{ item === 'Supply chain' ? 'Supply Network' : item }}
      </button>
    </div>

    <div class="sidebar-bottom">
      <div class="nav-label">SYSTEM</div>

      <div class="system-status" [class.offline]="error">
        <span class="status-dot"></span>

        <div>
          <strong>{{ error ? 'API Offline' : 'System Online' }}</strong>
          <small>
            {{ error ? 'Backend unavailable' : 'All systems operational' }}
          </small>
        </div>
      </div>
    </div>

  </aside>


  <div class="main-area">

    <header class="topbar">

      <div>
        <div class="eyebrow">
          ENERGY RESILIENCE · INDIA
        </div>

        <h1>
          {{ view === 'Supply chain' ? 'Supply Network' : view }}
        </h1>
      </div>

      <div class="topbar-status" [class.offline]="error">
        <span class="status-dot"></span>
        {{ error ? 'API Offline' : 'Decision Intelligence Online' }}
      </div>

    </header>


    <main class="content">

      <app-dashboard
        *ngIf="view === 'Dashboard'"
        [events]="state.events.value"
        [risks]="state.risks.value"
        [loading]="eventLoading"
        [error]="eventError"
        (analyze)="analyze($event)"
      ></app-dashboard>


      <app-procurement
        *ngIf="view === 'Procurement'"
        [results]="state.strategies.value"
        [loading]="strategyLoading"
        [error]="strategyError"
        (generate)="generate($event)"
      ></app-procurement>


      <app-supply-chain
        *ngIf="view === 'Supply chain'"
        [routes]="state.routes.value"
      ></app-supply-chain>


      <div class="global-error" *ngIf="error">
        {{ error }}
      </div>

    </main>

  </div>

</div>
`, styles: [`:host {
  display: block;
  min-height: 100vh;
  background: #071321;
  color: #eef6ff;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

* {
  box-sizing: border-box;
}

button {
  font: inherit;
}


/* ─────────────────────────────
   APP LAYOUT
   ───────────────────────────── */

.app-shell {
  min-height: 100vh;
  display: flex;
  background:
    radial-gradient(
      circle at 80% 0%,
      rgba(38, 180, 166, 0.07),
      transparent 35%
    ),
    #071321;
}


/* ─────────────────────────────
   SIDEBAR
   ───────────────────────────── */

.sidebar {
  width: 240px;
  min-height: 100vh;
  padding: 28px 18px;
  display: flex;
  flex-direction: column;

  background: #091827;
  border-right: 1px solid #1b344d;
}


.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 8px 34px;
}


.brand-mark {
  width: 38px;
  height: 38px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 10px;

  background: #26b4a6;
  color: #03141b;

  font-size: 13px;
  font-weight: 800;
  letter-spacing: -0.03em;
}


.brand-name {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.02em;
}


.brand-subtitle {
  margin-top: 3px;

  color: #62839c;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.12em;
}


.nav-section {
  flex: 1;
}


.nav-label {
  margin: 0 8px 10px;

  color: #52718a;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
}


.nav-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 11px;

  margin-bottom: 5px;
  padding: 11px 12px;

  border: 1px solid transparent;
  border-radius: 8px;

  background: transparent;
  color: #8fa9be;

  text-align: left;
  cursor: pointer;

  transition:
    background 0.15s ease,
    color 0.15s ease,
    border-color 0.15s ease;
}


.nav-item:hover {
  background: #10263a;
  color: #d9e8f5;
}


.nav-item.active {
  background: #102f3b;
  border-color: #1c5b61;
  color: #63dfd0;
}


.nav-dot {
  width: 6px;
  height: 6px;

  border-radius: 50%;
  background: #47677f;
}


.nav-item.active .nav-dot {
  background: #26b4a6;
  box-shadow: 0 0 8px rgba(38, 180, 166, 0.6);
}


.sidebar-bottom {
  padding-top: 22px;
  border-top: 1px solid #172f46;
}


.system-status {
  display: flex;
  align-items: center;
  gap: 10px;

  padding: 10px;

  border: 1px solid #183c3a;
  border-radius: 8px;

  background: #0b2428;
}


.system-status strong {
  display: block;

  color: #68d9bd;
  font-size: 12px;
  font-weight: 600;
}


.system-status small {
  display: block;

  margin-top: 3px;

  color: #58778d;
  font-size: 10px;
}


.system-status.offline {
  border-color: #543335;
  background: #24191d;
}


.system-status.offline strong {
  color: #ff9c87;
}


/* ─────────────────────────────
   MAIN AREA
   ───────────────────────────── */

.main-area {
  min-width: 0;
  flex: 1;
}


.topbar {
  height: 92px;

  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 0 38px;

  border-bottom: 1px solid #1b344d;
}


.eyebrow {
  margin-bottom: 5px;

  color: #63859e;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.13em;
}


h1 {
  margin: 0;

  color: #f3f8fc;
  font-size: 24px;
  font-weight: 650;
  letter-spacing: -0.03em;
}


.topbar-status {
  display: flex;
  align-items: center;
  gap: 8px;

  padding: 8px 12px;

  border: 1px solid #19443f;
  border-radius: 20px;

  background: #0b292a;

  color: #69d9bf;
  font-size: 11px;
  font-weight: 600;
}


.topbar-status.offline {
  border-color: #583536;
  background: #281a1e;
  color: #ff9f89;
}


.status-dot {
  width: 7px;
  height: 7px;

  border-radius: 50%;
  background: #31d0ad;

  box-shadow: 0 0 8px rgba(49, 208, 173, 0.6);
}


.offline .status-dot {
  background: #ff765e;
  box-shadow: none;
}


/* ─────────────────────────────
   CONTENT
   ───────────────────────────── */

.content {
  width: 100%;
  max-width: 1400px;

  margin: 0 auto;
  padding: 32px 38px 50px;
}


.global-error {
  margin-top: 20px;

  padding: 12px 15px;

  border: 1px solid #59363a;
  border-radius: 8px;

  background: #24191e;
  color: #ff9e8a;

  font-size: 12px;
}


/* ─────────────────────────────
   RESPONSIVE
   ───────────────────────────── */

@media (max-width: 800px) {

  .sidebar {
    width: 190px;
  }

  .topbar {
    padding: 0 22px;
  }

  .content {
    padding: 24px 22px;
  }

}


@media (max-width: 600px) {

  .sidebar {
    width: 68px;
    padding: 20px 10px;
  }

  .brand {
    justify-content: center;
    padding: 4px 0 30px;
  }

  .brand > div:not(.brand-mark) {
    display: none;
  }

  .nav-label,
  .nav-item {
    font-size: 0;
  }

  .nav-item {
    justify-content: center;
  }

  .nav-dot {
    width: 7px;
    height: 7px;
  }

  .sidebar-bottom {
    display: none;
  }

  .topbar-status {
    display: none;
  }

}`] })
export class AppComponent implements OnInit {
  readonly tabs = ['Dashboard', 'Procurement', 'Supply chain']; view = 'Dashboard'; error = ''; eventError = ''; strategyError = ''; eventLoading = false; strategyLoading = false;
  constructor(public readonly state: DataService, private readonly api: ApiService) {}
  ngOnInit(): void { this.refresh(); }
  refresh(): void { forkJoin({ events: this.api.events(), risks: this.api.corridorRisks(), routes: this.api.routes() }).subscribe({ next: data => { this.state.events.next(data.events.events); this.state.risks.next(data.risks); this.state.routes.next(data.routes); }, error: () => this.error = 'Cannot reach the backend. Start it on port 8000 and refresh.' }); }
  analyze(description: string): void { this.eventLoading = true; this.eventError = ''; this.api.createEvent(description).subscribe({ next: event => this.api.analyze(event.event_id).subscribe({ next: () => { this.eventLoading = false; this.refresh(); }, error: () => { this.eventLoading = false; this.eventError = 'The event was saved but risk analysis failed.'; } }), error: () => { this.eventLoading = false; this.eventError = 'Could not save the event.'; } }); }
  generate(riskTolerance: number): void { this.strategyLoading = true; this.strategyError = ''; this.api.strategies(riskTolerance).subscribe({ next: results => { this.state.strategies.next(results); this.strategyLoading = false; }, error: () => { this.strategyLoading = false; this.strategyError = 'Could not generate strategies. Check available route capacity.'; } }); }
}
