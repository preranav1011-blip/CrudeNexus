import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { GeopoliticalEvent, RiskSummary } from '../models/types';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],

  template: `
    <div class="dashboard">

      <!-- =========================================================
           TOP METRICS
           ========================================================= -->

      <section class="metrics" *ngIf="risks as summary">

        <!-- INDIA CRUDE RISK -->
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


        <!-- HIGHEST ALERT -->
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


        <!-- MONITORED CORRIDORS -->
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


      <!-- =========================================================
           BACKEND OFFLINE STATE
           ========================================================= -->

      <section class="offline-card" *ngIf="!risks">

        <div class="offline-icon">!</div>

        <div>
          <strong>Live risk data unavailable</strong>

          <p>
            Connect the backend to load corridor intelligence
            and latest events.
          </p>
        </div>

      </section>


      <!-- =========================================================
           EVENT ANALYSIS
           ========================================================= -->

      <section class="panel analysis-panel">

        <div class="section-heading">

          <div>
            <span class="section-eyebrow">
              RISK INTELLIGENCE
            </span>

            <h2>
              Analyze a geopolitical event
            </h2>
          </div>

          <span class="analysis-status">
            ML + LLM ANALYSIS
          </span>

        </div>


        <p class="section-description">
          Paste a crude supply, shipping, sanctions, or geopolitical
          event to assess its potential impact on India's energy supply.
        </p>


        <form (ngSubmit)="submit()">

          <textarea
            [(ngModel)]="description"
            name="description"
            placeholder="Example: Naval tensions escalate near the Strait of Hormuz, raising crude disruption concerns..."
          ></textarea>


          <div class="form-footer">

            <span class="input-hint">
              Event intelligence will be assessed across affected corridors.
            </span>

            <button
              type="submit"
              [disabled]="!description.trim() || loading"
            >
              {{ loading ? 'Analyzing…' : 'Analyze Impact →' }}
            </button>

          </div>

        </form>


        <p class="error" *ngIf="error">
          {{ error }}
        </p>

      </section>


      <!-- =========================================================
           CORRIDOR RISK
           ========================================================= -->

      <section class="panel corridor-panel" *ngIf="risks">

        <div class="section-heading">

          <div>
            <span class="section-eyebrow">
              SUPPLY CORRIDORS
            </span>

            <h2>
              Corridor risk
            </h2>

            <p class="section-subtitle">
              Current disruption exposure across India's major crude supply routes.
            </p>
          </div>

          <span class="section-meta">
            {{ risks.total_corridors }} monitored
          </span>

        </div>


        <!-- CORRIDOR LIST -->
        <div class="corridor-list">

          <div
            class="corridor"
            *ngFor="let corridor of risks.corridors"
          >

            <!-- LEFT: NAME + STATUS -->
            <div class="corridor-info">

              <div class="corridor-title">

                <span
                  class="corridor-dot"
                  [class.warning]="
                    corridor.risk_score >= 35 &&
                    corridor.risk_score < 60
                  "
                  [class.critical]="corridor.risk_score >= 60"
                ></span>

                <strong>
                  {{ corridor.corridor_name }}
                </strong>

              </div>

              <span
                class="corridor-status"
                [class.status-warning]="
                  corridor.risk_score >= 35 &&
                  corridor.risk_score < 60
                "
                [class.status-critical]="corridor.risk_score >= 60"
              >
                {{
                  corridor.risk_score >= 60
                    ? 'CRITICAL'
                    : corridor.risk_score >= 35
                      ? 'ELEVATED'
                      : 'STABLE'
                }}
              </span>

            </div>


            <!-- MIDDLE: RISK BAR -->
            <div class="corridor-risk">

              <div class="risk-bar-header">

                <span>
                  Disruption risk
                </span>

                <span>
                  {{ corridor.risk_score | number:'1.0-0' }}/100
                </span>

              </div>


              <div class="risk-bar">

                <div
                  class="risk-bar-fill"
                  [class.warning]="
                    corridor.risk_score >= 35 &&
                    corridor.risk_score < 60
                  "
                  [class.critical]="corridor.risk_score >= 60"
                  [style.width.%]="corridor.risk_score"
                ></div>

              </div>

            </div>


            <!-- RIGHT: INDIA EXPOSURE -->
            <div class="corridor-exposure">

              <strong>
                {{ corridor.india_exposure_pct }}%
              </strong>

              <span>
                India exposure
              </span>

            </div>

          </div>

        </div>

      </section>


      <!-- =========================================================
           LATEST EVENTS
           ========================================================= -->

      <section class="panel events-panel">

        <div class="section-heading">

          <div>
            <span class="section-eyebrow">
              INTELLIGENCE FEED
            </span>

            <h2>
              Latest events
            </h2>
          </div>

          <span class="section-meta">
            {{ events.length }} events
          </span>

        </div>


        <!-- EMPTY STATE -->
        <div
          class="empty-events"
          *ngIf="!events.length"
        >

          <div class="empty-icon">
            ◌
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
          class="event"
          *ngFor="let event of events"
        >

          <div class="event-indicator"></div>

          <div class="event-content">

            <strong>
              {{ event.affected_corridor || event.location }}
            </strong>

            <span>
              {{ event.description }}
            </span>

          </div>

          <time>
            {{ event.timestamp | date:'medium' }}
          </time>

        </div>

      </section>

    </div>
  `,

  styles: [`

    /* ============================================================
       MAIN DASHBOARD
       ============================================================ */

    .dashboard {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }


    /* ============================================================
       METRICS
       ============================================================ */

    .metrics {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 2px;
    }

    .metric-card {
      position: relative;
      overflow: hidden;

      padding: 22px;

      background:
        linear-gradient(
          145deg,
          #122842,
          #0e2035
        );

      border: 1px solid #203f5d;
      border-radius: 12px;

      min-height: 155px;

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
      width: 27px;
      height: 27px;

      display: flex;
      align-items: center;
      justify-content: center;

      border-radius: 7px;

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
      margin-top: 16px;

      color: #f2f7fb;

      font-size: 40px;
      font-weight: 650;

      letter-spacing: -0.04em;
    }

    .metric-value span {
      color: #66859c;

      font-size: 16px;
      font-weight: 500;

      letter-spacing: 0;
    }

    .metric-bottom {
      display: flex;
      align-items: center;
      justify-content: space-between;

      margin-top: 13px;
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
      color: #66859c;
      font-size: 12px;
    }

    .event-count {
      color: #83a4ba;
      font-size: 12px;
    }


    /* ============================================================
       OFFLINE
       ============================================================ */

    .offline-card {
      display: flex;
      align-items: center;
      gap: 13px;

      padding: 15px 17px;

      border: 1px solid #493137;
      border-radius: 9px;

      background: #20191f;
    }

    .offline-icon {
      width: 27px;
      height: 27px;

      display: flex;
      align-items: center;
      justify-content: center;

      border-radius: 50%;

      background: #4a292e;
      color: #ff8d79;

      font-size: 13px;
      font-weight: 700;
    }

    .offline-card strong {
      color: #d7b7b2;
      font-size: 13px;
    }

    .offline-card p {
      margin: 3px 0 0;

      color: #866b6c;
      font-size: 11px;
    }


    /* ============================================================
       GENERAL PANELS
       ============================================================ */

    .panel {
      padding: 22px;

      background:
        linear-gradient(
          145deg,
          #122842,
          #0e2035
        );

      border: 1px solid #203f5d;
      border-radius: 12px;
    }

    .section-heading {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;

      gap: 20px;
    }

    .section-eyebrow {
      display: block;

      margin-bottom: 6px;

      color: #5e829b;

      font-size: 11px;
      font-weight: 700;

      letter-spacing: 0.12em;
    }

    h2 {
      margin: 0;

      color: #edf6fc;

      font-size: 20px;
      font-weight: 650;
    }

    .section-subtitle {
      margin: 6px 0 0;

      color: #69869b;

      font-size: 12px;
      line-height: 1.5;
    }

    .section-meta,
    .analysis-status {
      padding: 6px 9px;

      border: 1px solid #254760;
      border-radius: 5px;

      color: #7695aa;

      font-size: 10px;
      font-weight: 700;

      letter-spacing: 0.05em;

      white-space: nowrap;
    }

    .analysis-status {
      border-color: #19504c;

      background: #102f32;

      color: #61cfc0;
    }


    /* ============================================================
       EVENT ANALYSIS
       ============================================================ */

    .section-description {
      max-width: 800px;

      margin: 8px 0 18px;

      color: #7693a8;

      font-size: 14px;
      line-height: 1.6;
    }

    textarea {
      width: 100%;
      min-height: 115px;

      box-sizing: border-box;
      resize: vertical;

      padding: 15px;

      background: #091827;

      border: 1px solid #294a65;
      border-radius: 8px;

      color: #eef7ff;

      font: inherit;
      font-size: 14px;

      outline: none;
    }

    textarea:focus {
      border-color: #2caea4;

      box-shadow:
        0 0 0 2px
        rgba(38, 180, 166, 0.08);
    }

    textarea::placeholder {
      color: #4e6b80;
    }

    .form-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;

      gap: 20px;

      margin-top: 12px;
    }

    .input-hint {
      color: #55748b;
      font-size: 11px;
    }

    button {
      padding: 10px 17px;

      border: 0;
      border-radius: 7px;

      background: #26b4a6;
      color: #03141b;

      font-size: 12px;
      font-weight: 700;

      cursor: pointer;
    }

    button:hover:not(:disabled) {
      background: #35c8b8;
    }

    button:disabled {
      opacity: 0.45;
      cursor: not-allowed;
    }

    .error {
      margin-top: 10px;

      color: #ff9b83;

      font-size: 12px;
    }


    /* ============================================================
       CORRIDOR RISK
       ============================================================ */

    .corridor-list {
      margin-top: 20px;
    }

    .corridor {
      display: grid;

      grid-template-columns:
        210px
        minmax(200px, 1fr)
        120px;

      align-items: center;

      gap: 24px;

      padding: 18px 4px;

      border-top: 1px solid #1c3850;

      transition:
        background 0.2s ease,
        padding 0.2s ease;
    }

    .corridor:first-child {
      border-top: none;
    }

    .corridor:hover {
      padding-left: 8px;
      padding-right: 8px;

      background: rgba(255, 255, 255, 0.015);
    }


    /* CORRIDOR NAME */

    .corridor-info {
      display: flex;
      align-items: center;
      justify-content: space-between;

      gap: 10px;
    }

    .corridor-title {
      display: flex;
      align-items: center;

      gap: 10px;

      min-width: 0;
    }

    .corridor-title strong {
      color: #dcebf5;

      font-size: 14px;
      font-weight: 600;

      white-space: nowrap;
    }

    .corridor-dot {
      flex-shrink: 0;

      width: 9px;
      height: 9px;

      border-radius: 50%;

      background: #31d0ad;

      box-shadow:
        0 0 7px
        rgba(49, 208, 173, 0.25);
    }

    .corridor-dot.warning {
      background: #e6b85c;

      box-shadow:
        0 0 7px
        rgba(230, 184, 92, 0.25);
    }

    .corridor-dot.critical {
      background: #ff725f;

      box-shadow:
        0 0 9px
        rgba(255, 114, 95, 0.5);
    }


    /* STATUS */

    .corridor-status {
      padding: 4px 7px;

      border-radius: 4px;

      background: #173d3a;
      color: #65d7bf;

      font-size: 9px;
      font-weight: 700;

      letter-spacing: 0.06em;

      white-space: nowrap;
    }

    .corridor-status.status-warning {
      background: #403725;
      color: #e7bb68;
    }

    .corridor-status.status-critical {
      background: #43282d;
      color: #ff9581;
    }


    /* RISK BAR */

    .corridor-risk {
      width: 100%;
    }

    .risk-bar-header {
      display: flex;
      justify-content: space-between;

      margin-bottom: 7px;

      color: #607f95;

      font-size: 10px;
    }

    .risk-bar-header span:last-child {
      color: #a1b8c8;

      font-weight: 600;
    }

    .risk-bar {
      width: 100%;
      height: 7px;

      overflow: hidden;

      border-radius: 10px;

      background: #192f43;
    }

    .risk-bar-fill {
      height: 100%;

      border-radius: inherit;

      background:
        linear-gradient(
          90deg,
          #269f92,
          #31cdb5
        );

      transition:
        width 0.5s ease;
    }

    .risk-bar-fill.warning {
      background:
        linear-gradient(
          90deg,
          #b58b3f,
          #e0b452
        );
    }

    .risk-bar-fill.critical {
      background:
        linear-gradient(
          90deg,
          #c95247,
          #ee7160
        );
    }


    /* INDIA EXPOSURE */

    .corridor-exposure {
      text-align: right;
    }

    .corridor-exposure strong {
      display: block;

      color: #eef7fc;

      font-size: 20px;
      font-weight: 650;

      letter-spacing: -0.02em;
    }

    .corridor-exposure span {
      display: block;

      margin-top: 2px;

      color: #607f95;

      font-size: 10px;
    }


    /* ============================================================
       EVENTS
       ============================================================ */

    .events-panel {
      min-height: 180px;
    }

    .event {
      display: grid;

      grid-template-columns:
        8px
        1fr
        auto;

      gap: 14px;

      align-items: start;

      padding: 15px 0;

      border-top: 1px solid #1c3850;
    }

    .event-indicator {
      width: 8px;
      height: 8px;

      margin-top: 6px;

      border-radius: 50%;

      background: #e6b85c;
    }

    .event-content strong {
      display: block;

      color: #dcebf5;

      font-size: 14px;
    }

    .event-content span {
      display: block;

      margin-top: 5px;

      color: #7693a8;

      font-size: 13px;

      line-height: 1.5;
    }

    .event time {
      color: #5c788e;

      font-size: 10px;

      white-space: nowrap;
    }

    .empty-events {
      padding: 35px 10px;

      text-align: center;
    }

    .empty-icon {
      margin-bottom: 9px;

      color: #3e6178;

      font-size: 28px;
    }

    .empty-events strong {
      display: block;

      color: #a8bfd0;

      font-size: 14px;
    }

    .empty-events p {
      margin: 6px 0 0;

      color: #55738a;

      font-size: 11px;
    }


    /* ============================================================
       RESPONSIVE
       ============================================================ */

    @media (max-width: 900px) {

      .corridor {
        grid-template-columns:
          180px
          minmax(150px, 1fr)
          100px;

        gap: 14px;
      }

    }


    @media (max-width: 800px) {

      .metrics {
        grid-template-columns: 1fr;
      }

      .corridor {
        grid-template-columns: 1fr;
        gap: 12px;
      }

      .corridor-info {
        justify-content: flex-start;
      }

      .corridor-exposure {
        text-align: left;
      }

    }


    @media (max-width: 600px) {

      .section-heading {
        flex-direction: column;
      }

      .form-footer {
        align-items: stretch;
        flex-direction: column;
      }

      .form-footer button {
        width: 100%;
      }

      .event {
        grid-template-columns: 8px 1fr;
      }

      .event time {
        grid-column: 2;
      }

    }

  `]
})
export class DashboardComponent {

  @Input() risks: RiskSummary | null = null;

  @Input() events: GeopoliticalEvent[] = [];

  @Input() loading = false;

  @Input() error = '';

  @Output() analyze = new EventEmitter<string>();

  description = '';

  submit(): void {
    this.analyze.emit(this.description);
    this.description = '';
  }
}