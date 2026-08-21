import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { forkJoin } from 'rxjs';

import { DashboardComponent } from './dashboard/dashboard.component';
import { ProcurementComponent } from './procurement/procurement.component';
import { SupplyChainComponent } from './supply-chain/supply-chain.component';
import { ApiService } from './services/api.service';
import { DataService } from './services/data.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    DashboardComponent,
    ProcurementComponent,
    SupplyChainComponent
  ],
  template: `
    <div class="app-shell">

      <!-- SIDEBAR -->
      <aside class="sidebar">

        <div class="brand">
          <div class="brand-mark">
            <svg
              viewBox="0 0 40 40"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M10 28 L20 11 L31 28"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />

              <path
                d="M10 28 L31 28"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
              />

              <circle cx="20" cy="11" r="4" fill="currentColor"/>
              <circle cx="10" cy="28" r="4" fill="currentColor"/>
              <circle cx="31" cy="28" r="4" fill="currentColor"/>
            </svg>
          </div>

          <div>
            <div class="brand-name">CrudeNexus</div>
            <div class="brand-subtitle">ENERGY INTELLIGENCE</div>
          </div>
        </div>

        <div class="nav-section">

          <div class="nav-label">
            COMMAND CENTER
          </div>

          <button
            *ngFor="let item of tabs"
            class="nav-item"
            [class.active]="view === item"
            (click)="view = item"
          >

            <span class="nav-icon">
              <span *ngIf="item === 'Dashboard'">◇</span>
              <span *ngIf="item === 'Procurement'">◇</span>
              <span *ngIf="item === 'Supply chain'">◎</span>
            </span>

            <div class="nav-text">
              <strong>
                {{ item === 'Supply chain' ? 'Supply Network' : item }}
              </strong>

              <small>
                {{
                  item === 'Dashboard'
                    ? 'Risk overview'
                    : item === 'Procurement'
                      ? 'Optimize supply'
                      : 'Monitor corridors'
                }}
              </small>
            </div>

            <span
              class="active-indicator"
              *ngIf="view === item"
            ></span>

          </button>

        </div>

        <!-- SIDEBAR BOTTOM -->
        <div class="sidebar-bottom">

          <div class="nav-label">
            SYSTEM STATUS
          </div>

          <div
            class="system-status"
            [class.offline]="error"
          >

            <span class="status-dot"></span>

            <div>
              <strong>
                {{ error ? 'API OFFLINE' : 'SYSTEM ONLINE' }}
              </strong>

              <small>
                {{
                  error
                    ? 'Backend unavailable'
                    : 'All systems operational'
                }}
              </small>
            </div>

          </div>

          <div class="sidebar-footer">
            <span>INDIA</span>
            <span>UTC+05:30</span>
            <span>VERSION 1.0</span>
          </div>

        </div>

      </aside>


      <!-- MAIN AREA -->
      <div class="main-area">

        <!-- HEADER -->
        <header class="topbar">

          <div class="header-left">

            <div class="eyebrow">
              <span class="eyebrow-dot"></span>
              INDIA ENERGY RESILIENCE
              <span class="slash">/</span>
              DECISION INTELLIGENCE
            </div>

            <h1>
              {{ view === 'Supply chain' ? 'Supply Network' : view }}
            </h1>

            <p class="header-description">
              {{
                view === 'Dashboard'
                  ? 'Monitor crude supply risk, geopolitical events and critical energy corridors.'
                  : view === 'Procurement'
                    ? 'Optimize procurement decisions against cost, risk and supplier concentration.'
                    : 'Monitor critical crude supply corridors and route exposure.'
              }}
            </p>

          </div>

          <div
            class="connection-card"
            [class.offline]="error"
          >

            <div class="connection-title">
              <span class="connection-dot"></span>

              {{
                error
                  ? 'CONNECTION LOST'
                  : 'SYSTEM CONNECTED'
              }}
            </div>

            <strong>
              {{ error ? 'OFFLINE' : 'ONLINE' }}
            </strong>

            <small>
              {{
                error
                  ? 'API · 8000 UNREACHABLE'
                  : 'ALL SERVICES OPERATIONAL'
              }}
            </small>

          </div>

        </header>


        <!-- STATUS STRIP -->
        <div class="status-strip">

          <div>
            <span>MODE</span>
            MONITORING
          </div>

          <div>
            <span>REGION</span>
            INDIA
          </div>

          <div>
            <span>ENGINE</span>
            RISK + OPTIMIZATION
          </div>

          <div class="strip-line"></div>

          <div class="system-ready">
            SYSTEM READY
            <span></span>
          </div>

        </div>


        <!-- CONTENT -->
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


          <div
            class="global-error"
            *ngIf="error"
          >
            <span class="error-icon">!</span>

            <div>
              <strong>BACKEND CONNECTION UNAVAILABLE</strong>
              <small>
                Start the API on port 8000 and refresh the application.
              </small>
            </div>
          </div>

        </main>

      </div>

    </div>
  `,

  styles: [`

    :host {
      display: block;
      min-height: 100vh;

      background: #071321;
      color: #eef6ff;

      font-family:
        Inter,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
    }

    * {
      box-sizing: border-box;
    }

    button {
      font: inherit;
    }


    /* =========================
       APP LAYOUT
       ========================= */

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


    /* =========================
       SIDEBAR
       ========================= */

    .sidebar {
      width: 265px;
      min-height: 100vh;

      padding: 28px 16px 18px;

      display: flex;
      flex-direction: column;

      background: #091827;

      border-right: 1px solid #1b344d;
    }


    /* BRAND */

    .brand {
      display: flex;
      align-items: center;

      gap: 13px;

      padding: 0 8px 30px;

      border-bottom: 1px solid #183149;
    }

    .brand-mark {
      width: 46px;
      height: 46px;

      flex-shrink: 0;

      display: flex;
      align-items: center;
      justify-content: center;

      border: 1px solid #3bd1c0;
      border-radius: 12px;

      background:
        linear-gradient(
          145deg,
          #27bbae,
          #167f7a
        );

      color: #04151c;

      box-shadow:
        0 8px 24px
        rgba(38, 180, 166, 0.14);
    }

    .brand-mark svg {
      width: 27px;
      height: 27px;
    }

    .brand-name {
      color: #f1f7fb;

      font-size: 18px;
      font-weight: 750;

      letter-spacing: -0.02em;
    }

    .brand-subtitle {
      margin-top: 5px;

      color: #7093aa;

      font-size: 11px;
      font-weight: 650;

      letter-spacing: 0.12em;
    }


    /* NAV */

    .nav-section {
      flex: 1;

      padding-top: 28px;
    }

    .nav-label {
      margin: 0 8px 13px;

      color: #60839a;

      font-size: 11px;
      font-weight: 750;

      letter-spacing: 0.13em;
    }

    .nav-item {
      position: relative;

      width: 100%;

      display: flex;
      align-items: center;

      gap: 11px;

      margin-bottom: 6px;

      padding: 11px 12px;

      border: 1px solid transparent;
      border-radius: 9px;

      background: transparent;

      color: #91aabd;

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

    .nav-icon {
      width: 38px;
      height: 38px;

      flex-shrink: 0;

      display: flex;
      align-items: center;
      justify-content: center;

      border-radius: 8px;

      background: #102b40;

      color: #6e91a9;

      font-size: 18px;
    }

    .nav-item.active .nav-icon {
      background: #16434b;
      color: #63dfd0;
    }

    .nav-text {
      min-width: 0;
    }

    .nav-text strong {
      display: block;

      color: inherit;

      font-size: 14px;
      font-weight: 650;
    }

    .nav-text small {
      display: block;

      margin-top: 4px;

      color: #64849a;

      font-size: 11px;
      line-height: 1.35;
    }

    .active-indicator {
      width: 6px;
      height: 6px;

      margin-left: auto;

      flex-shrink: 0;

      border-radius: 50%;

      background: #42d7c3;

      box-shadow:
        0 0 8px
        rgba(66, 215, 195, 0.65);
    }


    /* SIDEBAR BOTTOM */

    .sidebar-bottom {
      padding-top: 22px;

      border-top: 1px solid #172f46;
    }

    .system-status {
      display: flex;
      align-items: center;

      gap: 11px;

      padding: 12px;

      border: 1px solid #183c3a;
      border-radius: 9px;

      background: #0b2428;
    }

    .system-status strong {
      display: block;

      color: #68d9bd;

      font-size: 13px;
      font-weight: 650;
    }

    .system-status small {
      display: block;

      margin-top: 4px;

      color: #67869a;

      font-size: 11px;
    }

    .system-status.offline {
      border-color: #543335;
      background: #24191d;
    }

    .system-status.offline strong {
      color: #ff9c87;
    }

    .sidebar-footer {
      display: flex;
      justify-content: space-between;

      margin-top: 15px;
      padding: 0 8px;

      color: #536f84;

      font-size: 10px;
      font-weight: 600;

      letter-spacing: 0.05em;
    }


    /* =========================
       MAIN AREA
       ========================= */

    .main-area {
      min-width: 0;
      flex: 1;
    }


    /* HEADER */

    .topbar {
      min-height: 132px;

      display: flex;
      align-items: center;
      justify-content: space-between;

      gap: 30px;

      padding: 25px 44px;

      border-bottom: 1px solid #1b344d;
    }

    .header-left {
      min-width: 0;
    }

    .eyebrow {
      display: flex;
      align-items: center;
      gap: 9px;

      margin-bottom: 7px;

      color: #63859e;

      font-size: 11px;
      font-weight: 700;

      letter-spacing: 0.13em;
    }

    .eyebrow-dot {
      width: 6px;
      height: 6px;

      border-radius: 50%;

      background: #31d0ad;

      box-shadow:
        0 0 8px
        rgba(49, 208, 173, 0.6);
    }

    .slash {
      color: #34546d;
    }

    h1 {
      margin: 0;

      color: #f3f8fc;

      font-size: 34px;
      font-weight: 700;

      letter-spacing: -0.04em;
    }

    .header-description {
      margin: 8px 0 0;

      color: #7593a8;

      font-size: 14px;
      line-height: 1.5;
    }


    /* CONNECTION CARD */

    .connection-card {
      min-width: 156px;

      padding: 12px 14px;

      border: 1px solid #19443f;
      border-radius: 9px;

      background: #0b292a;
    }

    .connection-title {
      display: flex;
      align-items: center;
      gap: 7px;

      color: #6d9b9d;

      font-size: 9px;
      font-weight: 700;

      letter-spacing: 0.1em;
    }

    .connection-dot {
      width: 7px;
      height: 7px;

      border-radius: 50%;

      background: #31d0ad;

      box-shadow:
        0 0 7px
        rgba(49, 208, 173, 0.5);
    }

    .connection-card strong {
      display: block;

      margin-top: 6px;

      color: #c8e0e5;

      font-size: 15px;
    }

    .connection-card small {
      display: block;

      margin-top: 3px;

      color: #557b82;

      font-size: 9px;
    }

    .connection-card.offline {
      border-color: #583536;
      background: #281a1e;
    }

    .connection-card.offline .connection-dot {
      background: #ff765e;
      box-shadow: none;
    }


    /* STATUS STRIP */

    .status-strip {
      height: 36px;

      display: flex;
      align-items: center;

      gap: 22px;

      padding: 0 44px;

      border-bottom: 1px solid #1b344d;

      color: #64849a;

      font-size: 9px;
      font-weight: 650;

      letter-spacing: 0.08em;
    }

    .status-strip div {
      white-space: nowrap;
    }

    .status-strip div span {
      margin-right: 7px;

      color: #3e6077;

      font-size: 8px;
    }

    .strip-line {
      height: 1px;

      flex: 1;

      background: #29455b;
    }

    .system-ready {
      color: #708da0;
    }

    .system-ready span {
      display: inline-block;

      width: 6px;
      height: 6px;

      margin-left: 6px;

      border-radius: 50%;

      background: #31d0ad;
    }


    /* CONTENT */

    .content {
      width: 100%;
      max-width: 1400px;

      margin: 0 auto;

      padding: 32px 44px 50px;
    }

    .global-error {
      display: flex;
      align-items: center;

      gap: 11px;

      margin-top: 20px;

      padding: 13px 15px;

      border: 1px solid #59363a;
      border-radius: 8px;

      background: #24191e;

      color: #ff9e8a;
    }

    .error-icon {
      width: 24px;
      height: 24px;

      flex-shrink: 0;

      display: flex;
      align-items: center;
      justify-content: center;

      border-radius: 50%;

      background: #513035;

      font-size: 12px;
      font-weight: 800;
    }

    .global-error strong {
      display: block;

      font-size: 11px;
    }

    .global-error small {
      display: block;

      margin-top: 3px;

      color: #a16d6a;

      font-size: 11px;
    }


    /* =========================
       RESPONSIVE
       ========================= */

    @media (max-width: 900px) {

      .sidebar {
        width: 225px;
      }

      .topbar {
        padding: 22px 28px;
      }

      .status-strip {
        padding: 0 28px;
      }

      .content {
        padding: 26px 28px;
      }

    }


    @media (max-width: 700px) {

      .sidebar {
        width: 190px;
      }

      .connection-card {
        display: none;
      }

      .topbar {
        padding: 20px 22px;
      }

      .status-strip {
        padding: 0 22px;
      }

      .content {
        padding: 22px;
      }

      h1 {
        font-size: 29px;
      }

    }


    @media (max-width: 600px) {

      .sidebar {
        width: 70px;
        padding: 20px 10px;
      }

      .brand {
        justify-content: center;
        padding: 4px 0 28px;
      }

      .brand > div:not(.brand-mark) {
        display: none;
      }

      .nav-label {
        display: none;
      }

      .nav-item {
        justify-content: center;
        padding: 9px;
      }

      .nav-text,
      .active-indicator {
        display: none;
      }

      .sidebar-bottom {
        display: none;
      }

      .status-strip {
        display: none;
      }

      .topbar {
        min-height: 100px;
      }

      .content {
        padding: 20px 16px;
      }

    }

  `]
})
export class AppComponent implements OnInit {

  readonly tabs = [
    'Dashboard',
    'Procurement',
    'Supply chain'
  ];

  view = 'Dashboard';

  error = '';
  eventError = '';
  strategyError = '';

  eventLoading = false;
  strategyLoading = false;

  constructor(
    public readonly state: DataService,
    private readonly api: ApiService
  ) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {

    forkJoin({
      events: this.api.events(),
      risks: this.api.corridorRisks(),
      routes: this.api.routes()
    }).subscribe({

      next: data => {

        this.state.events.next(data.events.events);
        this.state.risks.next(data.risks);
        this.state.routes.next(data.routes);

        this.error = '';
      },

      error: () => {

        this.error =
          'Cannot reach the backend. Start it on port 8000 and refresh.';

      }

    });

  }

  analyze(description: string): void {

    this.eventLoading = true;
    this.eventError = '';

    this.api.createEvent(description).subscribe({

      next: event => {

        this.api.analyze(event.event_id).subscribe({

          next: () => {

            this.eventLoading = false;
            this.refresh();

          },

          error: () => {

            this.eventLoading = false;

            this.eventError =
              'The event was saved but risk analysis failed.';

          }

        });

      },

      error: () => {

        this.eventLoading = false;

        this.eventError =
          'Could not save the event.';

      }

    });

  }

  generate(riskTolerance: number): void {

    this.strategyLoading = true;
    this.strategyError = '';

    this.api.strategies(riskTolerance).subscribe({

      next: results => {

        this.state.strategies.next(results);

        this.strategyLoading = false;

      },

      error: () => {

        this.strategyLoading = false;

        this.strategyError =
          'Could not generate strategies. Check available route capacity.';

      }

    });

  }

}