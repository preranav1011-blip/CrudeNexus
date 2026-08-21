import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { OptimizationResults, ProcurementStrategy } from '../models/types';

@Component({
  selector: 'app-procurement',
  standalone: true,
  imports: [CommonModule, FormsModule],

  template: `
    <!-- PROCUREMENT CONTROL PANEL -->

    <section class="panel control-panel">

      <div class="heading">

        <div>
          <div class="eyebrow">OPTIMIZATION ENGINE</div>

          <h2>
            Adaptive Procurement
          </h2>

          <p>
            Generate procurement strategies balancing cost,
            geopolitical risk and supplier concentration.
          </p>
        </div>

        <button
          class="generate-button"
          (click)="generate.emit(riskTolerance)"
          [disabled]="loading"
        >
          {{ loading ? 'Optimizing…' : 'Generate Strategies →' }}
        </button>

      </div>


      <div class="risk-control">

        <div class="risk-label">

          <span>
            Risk tolerance
          </span>

          <strong>
            {{ riskTolerance | number:'1.1-1' }}
          </strong>

        </div>

        <input
          type="range"
          min="0"
          max="1"
          step=".1"
          [(ngModel)]="riskTolerance"
        />

        <div class="range-labels">
          <span>Risk averse</span>
          <span>Balanced</span>
          <span>Risk tolerant</span>
        </div>

      </div>
      <div class="risk-insight">

  <span class="insight-icon">✦</span>

  <div>
    <strong>
      {{
        riskTolerance <= 0.3
          ? 'Risk-averse strategy'
          : riskTolerance <= 0.6
            ? 'Balanced strategy'
            : 'Risk-tolerant strategy'
      }}
    </strong>

    <p>
      {{
        riskTolerance <= 0.3
          ? 'Prioritizes safer corridors and diversified suppliers to reduce disruption exposure.'
          : riskTolerance <= 0.6
            ? 'Balances procurement cost, supply resilience and geopolitical exposure.'
            : 'Accepts higher exposure to pursue lower procurement costs and greater flexibility.'
      }}
    </p>
  </div>

</div>

      <p
        class="error"
        *ngIf="error"
      >
        {{ error }}
      </p>

    </section>


    <!-- STRATEGIES -->

    <section
      class="cards"
      *ngIf="results"
    >

      <article
        *ngFor="let strategy of allStrategies"
        class="strategy-card"
        [class.recommended]="strategy.strategy_id === results.recommended"
      >

        <div class="strategy-header">

          <div>

            <span class="strategy-label">
              STRATEGY
            </span>

            <h3>
              {{ strategy.strategy_type }}
            </h3>

          </div>

          <span
            class="recommended-badge"
            *ngIf="strategy.strategy_id === results.recommended"
          >
            RECOMMENDED
          </span>

        </div>


        <div class="cost">

          {{ strategy.total_cost / 1000000
            | currency:'USD':'symbol':'1.1-1' }}M

          <span>
            / year
          </span>

        </div>


        <div class="metrics">

          <div class="metric">

            <span>
              RISK
            </span>

            <strong>
              {{ strategy.avg_risk_score | number:'1.0-0' }}/100
            </strong>

          </div>


          <div class="metric">

            <span>
              TRANSIT
            </span>

            <strong>
              {{ strategy.avg_transit_time | number:'1.0-1' }} days
            </strong>

          </div>


          <div class="metric">

            <span>
              HHI
            </span>

            <strong>
              {{ strategy.supplier_concentration_ratio | number:'1.3-3' }}
            </strong>

          </div>

        </div>


        <div class="explanation">

          {{ strategy.explanation }}

        </div>


        <div class="allocation-title">
          SUPPLIER ALLOCATION
        </div>


        <div
          class="allocation"
          *ngFor="let allocation of strategy.allocations"
        >

          <div class="allocation-top">

            <span>
              {{ allocation.supplier_id }}
            </span>

            <strong>
              {{ allocation.allocation_percentage | number:'1.0-0' }}%
            </strong>

          </div>

          <div class="allocation-track">

            <i
              [style.width.%]="allocation.allocation_percentage"
            ></i>

          </div>

        </div>

      </article>

    </section>
  `,

  styles: [`

    /* ============================================================
       CONTROL PANEL
       ============================================================ */

    .panel {
      background:
        linear-gradient(
          145deg,
          #122842,
          #0e2035
        );

      border: 1px solid #254260;

      border-radius: 13px;

      padding: 24px;

      margin-bottom: 18px;
    }


    .heading {
      display: flex;

      justify-content: space-between;

      align-items: flex-start;

      gap: 25px;
    }


    .eyebrow {
      margin-bottom: 7px;

      color: #5d879d;

      font-size: 11px;

      font-weight: 750;

      letter-spacing: 0.13em;
    }


    h2 {
      margin: 0;

      color: #eef7fb;

      font-size: 25px;

      font-weight: 650;

      letter-spacing: -0.025em;
    }


    .heading p {
      margin: 8px 0 0;

      color: #7694a8;

      font-size: 14px;

      line-height: 1.55;

      max-width: 680px;
    }


    /* ============================================================
       BUTTON
       ============================================================ */

    .generate-button {
      flex-shrink: 0;

      padding: 12px 18px;

      border: 0;

      border-radius: 8px;

      background: #26b4a6;

      color: #03141b;

      font-size: 13px;

      font-weight: 750;

      cursor: pointer;

      transition: 0.2s ease;
    }


    .generate-button:hover:not(:disabled) {
      background: #36cabb;

      transform: translateY(-1px);

      box-shadow:
        0 7px 20px
        rgba(38, 180, 166, 0.18);
    }


    .generate-button:disabled {
      opacity: 0.55;

      cursor: not-allowed;
    }


    /* ============================================================
       RISK CONTROL
       ============================================================ */

    .risk-control {
      margin-top: 25px;

      padding-top: 20px;

      border-top: 1px solid #203d57;
    }


    .risk-label {
      display: flex;

      justify-content: space-between;

      align-items: center;

      margin-bottom: 11px;
    }


    .risk-label span {
      color: #7694a8;

      font-size: 13px;

      font-weight: 550;
    }


    .risk-label strong {
      color: #65d8c6;

      font-size: 16px;

      font-weight: 700;
    }


    input[type="range"] {
      display: block;

      width: 100%;

      accent-color: #26b4a6;

      cursor: pointer;
    }


    .range-labels {
      display: flex;

      justify-content: space-between;

      margin-top: 7px;

      color: #5d7b90;

      font-size: 11px;
    }


    /* ============================================================
       ERROR
       ============================================================ */

    .error {
      margin: 15px 0 0;

      color: #ff9b83;

      font-size: 13px;
    }


    /* ============================================================
       STRATEGY CARDS
       ============================================================ */

    .cards {
      display: grid;

      grid-template-columns:
        repeat(3, minmax(0, 1fr));

      gap: 16px;
    }


    .strategy-card {
      position: relative;

      overflow: hidden;

      padding: 21px;

      background:
        linear-gradient(
          145deg,
          #122842,
          #0e2035
        );

      border: 1px solid #254260;

      border-radius: 13px;

      transition:
        transform 0.2s ease,
        border-color 0.2s ease;
    }


    .strategy-card:hover {
      transform: translateY(-3px);

      border-color: #315875;
    }


    .strategy-card.recommended {
      border-color: #26b4a6;

      box-shadow:
        0 0 0 1px
        rgba(38, 180, 166, 0.08),
        0 15px 35px
        rgba(0, 0, 0, 0.12);
    }


    .strategy-card.recommended::before {
      content: '';

      position: absolute;

      top: 0;
      left: 0;
      right: 0;

      height: 3px;

      background: #26b4a6;
    }


    /* ============================================================
       STRATEGY HEADER
       ============================================================ */

    .strategy-header {
      display: flex;

      align-items: flex-start;

      justify-content: space-between;

      gap: 10px;
    }


    .strategy-label {
      display: block;

      margin-bottom: 6px;

      color: #5c7f95;

      font-size: 10px;

      font-weight: 750;

      letter-spacing: 0.12em;
    }


    h3 {
      margin: 0;

      color: #edf6fa;

      font-size: 19px;

      font-weight: 650;

      text-transform: capitalize;
    }


    .recommended-badge {
      padding: 5px 8px;

      border-radius: 5px;

      background: #173d3a;

      color: #65d7bf;

      font-size: 9px;

      font-weight: 750;

      letter-spacing: 0.06em;

      white-space: nowrap;
    }


    /* ============================================================
       COST
       ============================================================ */

    .cost {
      margin-top: 21px;

      color: #f1f8fb;

      font-size: 29px;

      font-weight: 650;

      letter-spacing: -0.035em;
    }


    .cost span {
      color: #66869b;

      font-size: 12px;

      font-weight: 500;

      letter-spacing: 0;
    }


    /* ============================================================
       METRICS
       ============================================================ */

    .metrics {
      display: grid;

      grid-template-columns:
        repeat(3, 1fr);

      gap: 8px;

      margin-top: 18px;
    }


    .metric {
      padding: 10px;

      border: 1px solid #203f59;

      border-radius: 7px;

      background: #0c1e31;
    }


    .metric span {
      display: block;

      color: #58788e;

      font-size: 9px;

      font-weight: 750;

      letter-spacing: 0.08em;
    }


    .metric strong {
      display: block;

      margin-top: 5px;

      color: #c8dce7;

      font-size: 12px;

      font-weight: 650;
    }


    /* ============================================================
       EXPLANATION
       ============================================================ */

    .explanation {
      min-height: 78px;

      margin-top: 18px;

      padding-top: 17px;

      border-top: 1px solid #203d57;

      color: #7896a9;

      font-size: 13px;

      line-height: 1.6;
    }


    /* ============================================================
       ALLOCATION
       ============================================================ */

    .allocation-title {
      margin-top: 17px;

      margin-bottom: 11px;

      color: #587a91;

      font-size: 10px;

      font-weight: 750;

      letter-spacing: 0.1em;
    }


    .allocation {
      margin-bottom: 11px;
    }


    .allocation-top {
      display: flex;

      justify-content: space-between;

      margin-bottom: 5px;

      color: #91aabc;

      font-size: 12px;
    }


    .allocation-top strong {
      color: #c7dce7;

      font-size: 12px;
    }


    .allocation-track {
      height: 6px;

      overflow: hidden;

      border-radius: 5px;

      background: #10283b;
    }


    .allocation-track i {
      display: block;

      height: 100%;

      min-width: 2px;

      border-radius: 5px;

      background:
        linear-gradient(
          90deg,
          #1d9188,
          #32c6b5
        );
    }


    /* ============================================================
       RESPONSIVE
       ============================================================ */

    @media (max-width: 1000px) {

      .cards {
        grid-template-columns:
          repeat(2, minmax(0, 1fr));
      }

    }


    @media (max-width: 750px) {

      .heading {
        flex-direction: column;
      }

      .generate-button {
        width: 100%;
      }

      .cards {
        grid-template-columns: 1fr;
      }
      .risk-insight {
  display: flex;
  align-items: flex-start;

  gap: 11px;

  margin-top: 17px;
  padding: 12px 14px;

  border: 1px solid #1e4058;
  border-radius: 8px;

  background: #0c2032;
}

.insight-icon {
  width: 25px;
  height: 25px;

  display: flex;
  align-items: center;
  justify-content: center;

  flex-shrink: 0;

  border-radius: 6px;

  background: #123c42;

  color: #5ed7c8;

  font-size: 12px;
}

.risk-insight strong {
  display: block;

  color: #a9c8d5;

  font-size: 12px;
  font-weight: 700;
}

.risk-insight p {
  margin: 3px 0 0;

  color: #66869b;

  font-size: 11px;

  line-height: 1.45;
}
    }

  `]
})
export class ProcurementComponent {

  @Input()
  results: OptimizationResults | null = null;

  @Input()
  loading = false;

  @Input()
  error = '';

  @Output()
  generate = new EventEmitter<number>();

  riskTolerance = 0.5;


  get allStrategies(): ProcurementStrategy[] {

    return this.results
      ? [
          this.results.cheapest,
          this.results.balanced,
          this.results.safest
        ]
      : [];

  }

}