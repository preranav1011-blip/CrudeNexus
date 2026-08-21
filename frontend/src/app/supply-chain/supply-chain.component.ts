import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { Route } from '../models/types';

@Component({
  selector: 'app-supply-chain',
  standalone: true,
  imports: [CommonModule],

  template: `
    <section class="panel">

      <div class="section-header">

        <div>

          <div class="eyebrow">
            GLOBAL SUPPLY NETWORK
          </div>

          <h2>
            Supply Chain Routes
          </h2>

          <p>
            Live route master data used by the procurement
            optimization engine.
          </p>

        </div>


        <div class="route-count">

          <strong>
            {{ routes.length }}
          </strong>

          <span>
            ACTIVE ROUTES
          </span>

        </div>

      </div>


      <!-- ROUTES -->

      <div class="routes">

        <div
          class="route"
          *ngFor="let route of routes"
        >

          <!-- ROUTE NUMBER -->

          <div class="route-number">
            {{ routes.indexOf(route) + 1 | number:'2.0-0' }}
          </div>


          <!-- ROUTE -->

          <div class="route-main">

            <div class="route-path">

              <strong>
                {{ route.origin }}
              </strong>

              <span class="route-line"></span>

              <span class="corridor">
                {{ route.corridor_name }}
              </span>

              <span class="route-line"></span>

              <strong>
                {{ route.destination }}
              </strong>

            </div>


            <div class="route-details">

              <span>
                Transit:
                <strong>
                  {{ route.transit_days }} days
                </strong>
              </span>

              <span>
                Geopolitical risk:
                <strong
                  [class.high-risk]="route.geopolitical_risk_score >= 60"
                >
                  {{ route.geopolitical_risk_score }}/100
                </strong>
              </span>

            </div>

          </div>


          <!-- RISK -->

          <div
            class="risk-indicator"
            [class.high]="route.geopolitical_risk_score >= 60"
            [class.medium]="
              route.geopolitical_risk_score >= 35 &&
              route.geopolitical_risk_score < 60
            "
          >

            <span>
              RISK
            </span>

            <strong>
              {{ route.geopolitical_risk_score }}
            </strong>

          </div>

        </div>


        <!-- EMPTY STATE -->

        <div
          class="empty-state"
          *ngIf="!routes.length"
        >

          <div class="empty-icon">
            ◎
          </div>

          <strong>
            No routes available
          </strong>

          <span>
            Route data will appear here once the backend is connected.
          </span>

        </div>

      </div>

    </section>
  `,

  styles: [`

    /* ============================================================
       PANEL
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

      padding: 25px;
    }


    /* ============================================================
       HEADER
       ============================================================ */

    .section-header {
      display: flex;

      align-items: flex-start;

      justify-content: space-between;

      gap: 25px;

      padding-bottom: 22px;

      border-bottom: 1px solid #203d57;
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

      font-size: 26px;

      font-weight: 650;

      letter-spacing: -0.025em;
    }


    .section-header p {
      margin: 8px 0 0;

      color: #7694a8;

      font-size: 14px;

      line-height: 1.55;
    }


    /* ============================================================
       ROUTE COUNT
       ============================================================ */

    .route-count {
      min-width: 115px;

      padding: 11px 13px;

      border: 1px solid #21445b;

      border-radius: 8px;

      background: #0c2032;

      text-align: right;
    }


    .route-count strong {
      display: block;

      color: #69d8c7;

      font-size: 22px;

      font-weight: 700;
    }


    .route-count span {
      display: block;

      margin-top: 3px;

      color: #5d7e93;

      font-size: 9px;

      font-weight: 750;

      letter-spacing: 0.08em;
    }


    /* ============================================================
       ROUTES
       ============================================================ */

    .routes {
      margin-top: 5px;
    }


    .route {
      display: grid;

      grid-template-columns:
        42px
        minmax(0, 1fr)
        80px;

      align-items: center;

      gap: 17px;

      padding: 20px 7px;

      border-bottom: 1px solid #203b54;

      transition:
        background 0.2s ease,
        transform 0.2s ease;
    }


    .route:hover {
      background:
        linear-gradient(
          90deg,
          rgba(28, 74, 91, 0.18),
          transparent
        );

      transform: translateX(3px);
    }


    .route:last-child {
      border-bottom: 0;
    }


    /* ============================================================
       NUMBER
       ============================================================ */

    .route-number {
      width: 36px;
      height: 36px;

      display: flex;

      align-items: center;
      justify-content: center;

      border-radius: 8px;

      background: #10283b;

      color: #5d8097;

      font-size: 11px;

      font-weight: 700;
    }


    /* ============================================================
       PATH
       ============================================================ */

    .route-path {
      display: flex;

      align-items: center;

      gap: 10px;

      min-width: 0;
    }


    .route-path > strong {
      color: #dcebf2;

      font-size: 15px;

      font-weight: 650;

      white-space: nowrap;
    }


    .route-line {
      flex: 1;

      min-width: 20px;

      height: 1px;

      background:
        linear-gradient(
          90deg,
          #2c536c,
          #397084
        );
    }


    .corridor {
      padding: 6px 9px;

      border: 1px solid #21465c;

      border-radius: 6px;

      background: #0d2234;

      color: #70a1ad;

      font-size: 11px;

      font-weight: 650;

      white-space: nowrap;
    }


    /* ============================================================
       DETAILS
       ============================================================ */

    .route-details {
      display: flex;

      gap: 22px;

      margin-top: 10px;

      color: #66859a;

      font-size: 12px;
    }


    .route-details strong {
      color: #a8c2cf;

      font-weight: 650;
    }


    .route-details .high-risk {
      color: #ff9884;
    }


    /* ============================================================
       RISK
       ============================================================ */

    .risk-indicator {
      padding: 10px;

      border: 1px solid #214e4a;

      border-radius: 8px;

      background: #102e2e;

      text-align: center;
    }


    .risk-indicator span {
      display: block;

      color: #60958f;

      font-size: 9px;

      font-weight: 750;

      letter-spacing: 0.08em;
    }


    .risk-indicator strong {
      display: block;

      margin-top: 3px;

      color: #63d4c0;

      font-size: 19px;

      font-weight: 700;
    }


    .risk-indicator.medium {
      border-color: #55462b;

      background: #302a1e;
    }


    .risk-indicator.medium span {
      color: #aa8b54;
    }


    .risk-indicator.medium strong {
      color: #e2bd6d;
    }


    .risk-indicator.high {
      border-color: #59363a;

      background: #301f24;
    }


    .risk-indicator.high span {
      color: #ad6e6d;
    }


    .risk-indicator.high strong {
      color: #ff9582;
    }


    /* ============================================================
       EMPTY
       ============================================================ */

    .empty-state {
      display: flex;

      flex-direction: column;

      align-items: center;

      justify-content: center;

      padding: 60px 20px;

      text-align: center;
    }


    .empty-icon {
      width: 48px;
      height: 48px;

      display: flex;

      align-items: center;
      justify-content: center;

      margin-bottom: 14px;

      border: 1px solid #254760;

      border-radius: 50%;

      color: #5d8198;

      font-size: 22px;
    }


    .empty-state strong {
      color: #b7ccd8;

      font-size: 16px;
    }


    .empty-state span {
      margin-top: 6px;

      color: #648197;

      font-size: 13px;
    }


    /* ============================================================
       RESPONSIVE
       ============================================================ */

    @media (max-width: 800px) {

      .route {
        grid-template-columns:
          36px
          minmax(0, 1fr)
          65px;

        gap: 11px;
      }

      .route-path {
        flex-wrap: wrap;
      }

      .route-line {
        display: none;
      }

      .route-details {
        flex-direction: column;

        gap: 4px;
      }

    }


    @media (max-width: 600px) {

      .panel {
        padding: 18px;
      }

      .section-header {
        flex-direction: column;
      }

      .route-count {
        text-align: left;
      }

      .route {
        grid-template-columns:
          34px
          1fr;
      }

      .risk-indicator {
        display: none;
      }

      .route-path > strong {
        font-size: 14px;
      }

      .route-details {
        font-size: 11px;
      }

    }

  `]
})
export class SupplyChainComponent {

  @Input()
  routes: Route[] = [];

}