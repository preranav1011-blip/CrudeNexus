import { CommonModule } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  Output
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  GeopoliticalEvent,
  RiskSummary
} from '../models/types';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],

  template: `

    <!-- =========================
         METRICS
         ========================= -->

    <section
      class="metrics"
      *ngIf="risks as summary"
    >

      <article class="metric-card primary">

        <div class="metric-top">
          <span>INDIA CRUDE RISK</span>
          <span class="metric-icon">↗</span>
        </div>

        <div class="metric-value">
          {{ summary.average_risk | number:'1.0-0' }}
          <span>/100</span>
        </div>

        <div class="metric-bottom">

          <span
            class="risk-badge"
            [class.high]="summary.average_risk >= 60"
            [class.medium]="
              summary.average_risk >= 35 &&
              summary.average_risk < 60
            "
          >
            {{
              summary.average_risk >= 60
                ? 'HIGH RISK'
                : summary.average_risk >= 35
                  ? 'ELEVATED'
                  : 'LOW RISK'
            }}
          </span>

          <span class="metric-label">
            Overall corridor exposure
          </span>

        </div>

      </article>


      <article class="metric-card">

        <div class="metric-top">
          <span>HIGHEST ALERT</span>
          <span class="metric-icon danger-icon">!</span>
        </div>

        <div class="metric-value">
          {{ summary.highest_risk | number:'1.0-0' }}
          <span>/100</span>
        </div>

        <div class="metric-bottom">

          <span class="risk-badge high">
            {{
              summary.highest_risk >= 60
                ? 'CRITICAL'
                : 'ELEVATED'
            }}
          </span>

          <span class="metric-label">
            Most exposed corridor
          </span>

        </div>

      </article>


      <article class="metric-card">

        <div class="metric-top">
          <span>MONITORED CORRIDORS</span>
          <span class="metric-icon">◎</span>
        </div>

        <div class="metric-value">
          {{ summary.total_corridors }}
        </div>

        <div class="metric-bottom">

          <span class="metric-label">
            Active geopolitical routes
          </span>

          <span class="event-count">
            {{ events.length }} events
          </span>

        </div>

      </article>

    </section>


    <!-- =========================
         BACKEND WARNING
         ========================= -->

    <section
      class="data-warning"
      *ngIf="!risks"
    >

      <span class="warning-icon">!</span>

      <div>
        <strong>Live risk data unavailable</strong>

        <p>
          Connect the backend to load corridor intelligence
          and latest events.
        </p>
      </div>

    </section>


    <!-- =========================
         EVENT ANALYSIS
         ========================= -->

    <section class="panel analysis-panel">

      <div class="section-header">

        <div>

          <div class="section-eyebrow">
            RISK INTELLIGENCE
          </div>

          <h2>
            Analyze a geopolitical event
          </h2>

          <p class="section-description">
            Paste a crude supply, shipping, sanctions, or geopolitical
            event to assess its potential impact on India's energy supply.
          </p>

        </div>

        <span class="analysis-badge">
          ML + LLM ANALYSIS
        </span>

      </div>


      <form
        class="analysis-form"
        (ngSubmit)="submit()"
      >

        <textarea
          [(ngModel)]="description"
          name="description"
          placeholder="Example: Naval tensions escalate near the Strait of Hormuz, raising crude disruption concerns..."
        ></textarea>


        <div class="analysis-footer">

          <span>
            Event intelligence will be assessed across affected corridors.
          </span>

          <button
            type="submit"
            [disabled]="!description.trim() || loading"
          >
            {{
              loading
                ? 'Analyzing...'
                : 'Analyze Impact →'
            }}
          </button>

        </div>

      </form>


      <p
        class="error"
        *ngIf="error"
      >
        {{ error }}
      </p>

    </section>


    <!-- =========================
         CORRIDOR RISK
         ========================= -->

    <section
      class="panel"
      *ngIf="risks"
    >

      <div class="section-header compact">

        <div>

          <div class="section-eyebrow">
            CORRIDOR INTELLIGENCE
          </div>

          <h2>
            Corridor risk
          </h2>

          <p class="section-description">
            Current geopolitical exposure across monitored
            crude supply corridors.
          </p>

        </div>

      </div>


      <div class="corridor-list">

        <div
          class="corridor"
          *ngFor="let corridor of risks?.corridors"
        >

          <div class="corridor-name">
            <strong>
              {{ corridor.corridor_name }}
            </strong>

            <small>
              {{ corridor.india_exposure_pct }}% India exposure
            </small>
          </div>

          <div class="risk-bar">

            <div
              class="risk-fill"
              [class.high]="corridor.risk_score >= 60"
              [class.medium]="
                corridor.risk_score >= 35 &&
                corridor.risk_score < 60
              "
              [style.width.%]="corridor.risk_score"
            ></div>

          </div>

          <strong
            class="corridor-score"
            [class.danger]="corridor.risk_score >= 60"
          >
            {{ corridor.risk_score | number:'1.0-0' }}/100
          </strong>

        </div>

      </div>

    </section>


    <!-- =========================
         LATEST EVENTS
         ========================= -->

    <section class="panel events-panel">

      <div class="section-header">

        <div>

          <div class="section-eyebrow">
            INTELLIGENCE FEED
          </div>

          <h2>
            Latest events
          </h2>

          <p class="section-description">
            Recent geopolitical developments affecting
            monitored energy corridors.
          </p>

        </div>

        <span class="event-counter">
          {{ events.length }} events
        </span>

      </div>


      <!-- EMPTY STATE -->

      <div
        class="empty-state"
        *ngIf="!events.length"
      >

        <div class="empty-icon">
          ↓
        </div>

        <strong>
          No events yet
        </strong>

        <p>
          Geopolitical events analyzed by the system
          will appear here.
        </p>

      </div>


      <!-- EVENTS -->

      <div
        class="event-list"
        *ngIf="events.length"
      >

        <div
          class="event"
          *ngFor="let event of events"
        >

          <div class="event-marker"></div>

          <div class="event-main">

            <strong>
              {{ event.affected_corridor || event.location }}
            </strong>

            <p>
              {{ event.description }}
            </p>

          </div>

          <small>
            {{ event.timestamp | date:'medium' }}
          </small>

        </div>

      </div>

    </section>

  `,

  styles: [`

    /* =========================
       METRICS
       ========================= */

    .metrics {
      display: grid;

      grid-template-columns:
        repeat(3, 1fr);

      gap: 14px;

      margin-bottom: 18px;
    }

    .metric-card {
      position: relative;
      overflow: hidden;

      padding: 20px;

      background:
        linear-gradient(
          145deg,
          #122842,
          #0e2035
        );

      border: 1px solid #203f5d;

      border-radius: 12px;

      min-height: 145px;

      transition:
        transform 0.2s ease,
        border-color 0.2s ease;
    }

    .metric-card:hover {
      transform: translateY(-2px);

      border-color: #2c5879;
    }

    .metric-card.primary {
      border-color: #21605f;

      background:
        radial-gradient(
          circle at 100% 0%,
          rgba(38, 180, 166, 0.12),
          transparent 45%
        ),
        linear-gradient(
          145deg,
          #122e3d,
          #0e2035
        );
    }

    .metric-top {
      display: flex;
      align-items: center;
      justify-content: space-between;

      color: #6f92aa;

      font-size: 11px;
      font-weight: 700;

      letter-spacing: 0.1em;
    }

    .metric-icon {
      width: 26px;
      height: 26px;

      display: flex;
      align-items: center;
      justify-content: center;

      border-radius: 6px;

      background: #17364c;

      color: #62d7c8;

      font-size: 14px;
      font-weight: 700;
    }

    .danger-icon {
      background: #38272c;
      color: #ff937d;
    }

    .metric-value {
      margin-top: 15px;

      color: #f2f7fb;

      font-size: 36px;
      font-weight: 650;

      letter-spacing: -0.04em;
    }

    .metric-value span {
      color: #66859c;

      font-size: 15px;
      font-weight: 500;

      letter-spacing: 0;
    }

    .metric-bottom {
      display: flex;
      align-items: center;
      justify-content: space-between;

      gap: 10px;

      margin-top: 12px;
    }

    .risk-badge {
      padding: 5px 9px;

      border-radius: 5px;

      background: #173d3a;

      color: #65d7bf;

      font-size: 10px;
      font-weight: 700;

      letter-spacing: 0.06em;
    }

    .risk-badge.medium {
      background: #403725;
      color: #e7bb68;
    }

    .risk-badge.high {
      background: #43282d;
      color: #ff9581;
    }

    .metric-label {
      color: #718fa3;

      font-size: 11px;
    }

    .event-count {
      color: #83a4ba;

      font-size: 12px;
    }


    /* =========================
       WARNING
       ========================= */

    .data-warning {
      display: flex;
      align-items: center;

      gap: 12px;

      margin-bottom: 18px;

      padding: 13px 15px;

      border: 1px solid #59363a;
      border-radius: 9px;

      background: #24191e;
    }

    .warning-icon {
      width: 27px;
      height: 27px;

      flex-shrink: 0;

      display: flex;
      align-items: center;
      justify-content: center;

      border-radius: 50%;

      background: #513035;

      color: #ff9e8a;

      font-size: 12px;
      font-weight: 800;
    }

    .data-warning strong {
      display: block;

      color: #ffab98;

      font-size: 13px;
    }

    .data-warning p {
      margin: 3px 0 0;

      color: #956d6d;

      font-size: 11px;
    }


    /* =========================
       PANELS
       ========================= */

    .panel {
      margin-bottom: 18px;

      padding: 20px;

      background:
        linear-gradient(
          145deg,
          #122842,
          #10243a
        );

      border: 1px solid #254867;

      border-radius: 12px;
    }

    .section-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;

      gap: 20px;

      margin-bottom: 17px;
    }

    .section-header.compact {
      margin-bottom: 12px;
    }

    .section-eyebrow {
      margin-bottom: 5px;

      color: #5d89a5;

      font-size: 10px;
      font-weight: 750;

      letter-spacing: 0.13em;
    }

    h2 {
      margin: 0;

      color: #eef6fb;

      font-size: 20px;
      font-weight: 700;

      letter-spacing: -0.02em;
    }

    .section-description {
      margin: 7px 0 0;

      color: #7897ab;

      font-size: 13px;

      line-height: 1.5;
    }

    .analysis-badge {
      flex-shrink: 0;

      padding: 6px 9px;

      border: 1px solid #155f5d;
      border-radius: 5px;

      background: #0c3337;

      color: #65d7c7;

      font-size: 9px;
      font-weight: 700;

      letter-spacing: 0.07em;
    }


    /* =========================
       ANALYSIS FORM
       ========================= */

    .analysis-form textarea {
      width: 100%;
      min-height: 110px;

      box-sizing: border-box;

      resize: vertical;

      padding: 13px;

      background: #081927;

      color: #eff7ff;

      border: 1px solid #355a76;

      border-radius: 7px;

      font-family: inherit;

      font-size: 13px;

      line-height: 1.5;

      outline: none;
    }

    .analysis-form textarea::placeholder {
      color: #52738b;
    }

    .analysis-form textarea:focus {
      border-color: #2a8c91;

      box-shadow:
        0 0 0 2px
        rgba(38, 180, 166, 0.08);
    }

    .analysis-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;

      gap: 15px;

      margin-top: 10px;
    }

    .analysis-footer > span {
      color: #63859b;

      font-size: 11px;
    }

    button {
      border: 0;
      border-radius: 7px;

      padding: 10px 15px;

      background: #26b4a6;

      color: #03141b;

      font-size: 12px;
      font-weight: 750;

      cursor: pointer;
    }

    button:hover:not(:disabled) {
      background: #34c6b7;
    }

    button:disabled {
      opacity: 0.45;
      cursor: not-allowed;
    }

    .error {
      margin: 10px 0 0;

      color: #ff9b83;

      font-size: 12px;
    }


    /* =========================
       CORRIDOR RISK
       ========================= */

    .corridor-list {
      border-top: 1px solid #24445e;
    }

    .corridor {
      display: grid;

      grid-template-columns:
        minmax(180px, 0.8fr)
        minmax(160px, 2fr)
        75px;

      align-items: center;

      gap: 18px;

      padding: 14px 0;

      border-bottom: 1px solid #203d55;
    }

    .corridor-name strong {
      display: block;

      color: #dceaf2;

      font-size: 13px;
    }

    .corridor-name small {
      display: block;

      margin-top: 4px;

      color: #718fa3;

      font-size: 11px;
    }

    .risk-bar {
      height: 7px;

      overflow: hidden;

      border-radius: 10px;

      background: #0a1a29;
    }

    .risk-fill {
      height: 100%;

      border-radius: inherit;

      background: #2bb9a9;
    }

    .risk-fill.medium {
      background: #c59b55;
    }

    .risk-fill.high {
      background: #dc705e;
    }

    .corridor-score {
      color: #70d7c8;

      font-size: 13px;

      text-align: right;
    }

    .corridor-score.danger {
      color: #ff9581;
    }


    /* =========================
       LATEST EVENTS
       ========================= */

    .events-panel {
      min-height: 250px;
    }

    .event-counter {
      padding: 5px 9px;

      border: 1px solid #28516c;
      border-radius: 5px;

      color: #7ba1b7;

      font-size: 11px;
    }

    .empty-state {
      min-height: 150px;

      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;

      text-align: center;
    }

    .empty-icon {
      width: 46px;
      height: 46px;

      display: flex;
      align-items: center;
      justify-content: center;

      margin-bottom: 10px;

      border: 1px solid #28536e;

      border-radius: 50%;

      color: #52788e;

      font-size: 18px;
    }

    .empty-state strong {
      color: #a9c3d4;

      font-size: 14px;
      font-weight: 650;
    }

    .empty-state p {
      max-width: 430px;

      margin: 5px 0 0;

      color: #6f8da3;

      font-size: 12px;

      line-height: 1.5;
    }


    /* EVENT LIST */

    .event-list {
      border-top: 1px solid #24445e;
    }

    .event {
      display: grid;

      grid-template-columns:
        8px 1fr auto;

      align-items: start;

      gap: 13px;

      padding: 15px 0;

      border-bottom: 1px solid #203d55;
    }

    .event-marker {
      width: 7px;
      height: 7px;

      margin-top: 6px;

      border-radius: 50%;

      background: #31c7b4;

      box-shadow:
        0 0 7px
        rgba(49, 199, 180, 0.45);
    }

    .event-main strong {
      display: block;

      color: #dceaf2;

      font-size: 13px;
    }

    .event-main p {
      margin: 5px 0 0;

      color: #7897aa;

      font-size: 12px;

      line-height: 1.5;
    }

    .event > small {
      color: #638197;

      font-size: 11px;

      white-space: nowrap;
    }


    /* =========================
       RESPONSIVE
       ========================= */

    @media (max-width: 800px) {

      .metrics {
        grid-template-columns: 1fr;
      }

      .corridor {
        grid-template-columns: 1fr;
      }

      .corridor-score {
        text-align: left;
      }

      .section-header {
        flex-direction: column;
      }

    }

    @media (max-width: 600px) {

      .analysis-footer {
        flex-direction: column;
        align-items: stretch;
      }

      .analysis-footer button {
        width: 100%;
      }

      .event {
        grid-template-columns: 8px 1fr;
      }

      .event > small {
        grid-column: 2;
      }

    }

  `]
})
export class DashboardComponent {

  @Input()
  risks: RiskSummary | null = null;

  @Input()
  events: GeopoliticalEvent[] = [];

  @Input()
  loading = false;

  @Input()
  error = '';

  @Output()
  analyze = new EventEmitter<string>();

  description = '';

  submit(): void {

    if (!this.description.trim() || this.loading) {
      return;
    }

    this.analyze.emit(this.description);

    this.description = '';
  }

}