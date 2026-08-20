import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { Route } from '../models/types';
@Component({ selector: 'app-supply-chain', standalone: true, imports: [CommonModule], template: `<section class="panel"><h2>Supply-chain routes</h2><p>Live route master data used by the procurement optimizer.</p><div *ngFor="let route of routes"><b>{{ route.origin }}</b><span> → {{ route.corridor_name }} → </span><b>{{ route.destination }}</b><small>{{ route.transit_days }}d · risk {{ route.geopolitical_risk_score }}/100</small></div></section>`, styles: [`.panel{background:#12233b;border:1px solid #254260;border-radius:10px;padding:16px;margin-top:14px}h2{margin:0}div{padding:10px 0;border-top:1px solid #254260}small{display:block;color:#a8c0d8;margin-top:3px}`] })
export class SupplyChainComponent { @Input() routes: Route[] = []; }
