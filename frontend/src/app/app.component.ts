import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  standalone: true,
  template: `
    <div class="app-container">
      <header class="app-header">
        <h1>🛢️ CrudeNexus - EnergyResilience AI for India</h1>
      </header>
      <main class="app-main">
        <p>Frontend scaffolding - Phase 1 complete.</p>
        <p><strong>API Running at:</strong> http://localhost:8000</p>
        <p><strong>API Docs:</strong> http://localhost:8000/docs</p>
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      font-family: Arial, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    .app-header {
      text-align: center;
      color: #1976d2;
      border-bottom: 2px solid #1976d2;
      padding-bottom: 20px;
    }
    .app-main {
      margin-top: 30px;
      padding: 20px;
      background: #f5f5f5;
      border-radius: 8px;
    }
  `],
})
export class AppComponent {}
