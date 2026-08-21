# CrudeNexus: EnergyResilience AI — Implementation Plan

**Status**: Ready for execution  
**Last Updated**: 2026-08-19

---

## 1. Project Structure (Monorepo)

```
CrudeNexus/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── config.py               # Configuration
│   │   ├── models/                 # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── event.py            # Geopolitical event
│   │   │   ├── supplier.py         # Supplier/route data
│   │   │   └── optimization.py     # Optimization results
│   │   ├── agents/                 # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── geopolitical_risk.py # Risk assessment + LLM integration
│   │   │   ├── supply_exposure.py  # Supply chain analysis
│   │   │   └── procurement_optimizer.py # OR-Tools optimization
│   │   ├── ml/                     # ML pipeline
│   │   │   ├── __init__.py
│   │   │   ├── training.py         # Model training
│   │   │   ├── inference.py        # Risk prediction
│   │   │   └── feature_engineering.py
│   │   ├── data/                   # Data layer
│   │   │   ├── __init__.py
│   │   │   ├── gdelt_fetcher.py    # GDELT data retrieval
│   │   │   ├── mock_sources.py     # Mocked sanctions/trade data
│   │   │   └── loaders.py          # CSV/JSON loaders
│   │   ├── database/               # SQLite ORM
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   └── db.py               # Database init
│   │   └── routes/                 # API endpoints
│   │       ├── __init__.py
│   │       ├── events.py           # Event management endpoints
│   │       ├── analysis.py         # Risk analysis endpoints
│   │       └── optimization.py     # Procurement endpoints
│   ├── data/
│   │   ├── suppliers.csv           # Major Indian crude suppliers
│   │   ├── routes.csv              # India-focused routes
│   │   ├── ports.csv               # Indian & global ports
│   │   ├── corridors.csv           # Critical chokepoints
│   │   └── sample_events.json      # Test geopolitical events
│   ├── models/                     # Trained ML models
│   │   └── disruption_predictor.pkl
│   ├── requirements.txt
│   ├── setup.py
│   └── pytest.ini                  # Testing config
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── app.component.ts
    │   │   ├── app.component.html
    │   │   ├── app.component.scss
    │   │   ├── dashboard/          # Main dashboard
    │   │   │   ├── dashboard.component.*
    │   │   │   ├── risk-cards/
    │   │   │   └── latest-events/
    │   │   ├── supply-chain/       # Supply chain graph view
    │   │   │   └── supply-chain.component.*
    │   │   ├── procurement/        # Procurement strategies
    │   │   │   └── procurement.component.*
    │   │   ├── services/
    │   │   │   ├── api.service.ts
    │   │   │   └── data.service.ts
    │   │   └── models/
    │   │       └── types.ts
    │   ├── assets/
    │   ├── styles/
    │   ├── main.ts
    │   └── index.html
    ├── angular.json
    ├── tsconfig.json
    ├── package.json
    └── vite.config.ts

├── docs/
│   ├── API.md
│   ├── DATA_SOURCES.md
│   ├── ML_MODEL.md
│   └── SETUP.md
├── .gitignore
├── README.md
└── IMPLEMENTATION_PLAN.md (this file)
```

---

## 2. Backend Dependencies

### Python Packages

```
# Core framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Data & ML
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
xgboost==2.0.3
requests==2.31.0

# Database
sqlalchemy==2.0.23
sqlite3  # built-in

# Graph & optimization
networkx==3.2
ortools==9.7.2996

# NLP & LLM
langchain==0.1.4
ollama==0.1.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1

# Environment
python-dotenv==1.0.0
```

**Python Version**: 3.10+

---

## 3. Frontend Dependencies

```json
{
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0",
    "@angular/router": "^17.0.0",
    "echarts": "^5.4.3",
    "leaflet": "^1.9.4",
    "cytoscape": "^3.28.1",
    "axios": "^1.6.2",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.0"
  }
}
```

**Node Version**: 18+

---

## 4. Data Layer

### 4.1 India Suppliers Dataset (`backend/data/suppliers.csv`)

```
supplier_id,supplier_name,supplier_country,production_capacity_mbd,estimated_cost_per_barrel,geopolitical_baseline_risk_score
S001,Saudi Aramco,Saudi Arabia,3500,75,45
S002,Rosneft,Russia,2800,70,68
S003,NIOC,Iran,1500,60,85
S004,ADNOC,UAE,2800,76,38
S005,Kuwait Petroleum,Kuwait,1200,72,48
S006,Qatar Petroleum,Qatar,800,74,42
S007,ExxonMobil US,USA,600,82,20
S008,BP Baku,Azerbaijan,500,73,52
```

**Fields Explained**:
- `production_capacity_mbd`: Million barrels per day
- `estimated_cost_per_barrel`: USD per barrel (baseline)
- `geopolitical_baseline_risk_score`: 0-100 (higher = more risk)

### 4.2 Routes Dataset (`backend/data/routes.csv`)

```
route_id,route_name,origin_port,destination_port,corridor,distance_km,transit_time_days,capacity_mbd,baseline_risk_score,is_blocked
R001,Ras Tanura→Hormuz→Indian Ocean→Mundra,Ras Tanura,Mundra,Hormuz,5200,18,3500,48,0
R002,Baku→Hormuz→Indian Ocean→Jawaharlal Nehru Port,Baku,Jawaharlal Nehru Port,Hormuz,6800,22,800,52,0
R003,Houston→Good Hope→Indian Ocean→Mundra,Houston,Mundra,Cape of Good Hope,12500,35,600,25,0
R004,Novorossiysk→Suez→Mundra,Novorossiysk,Mundra,Suez,8200,24,500,58,0
R005,Kharg Island→Hormuz→Chabahar→Mundra,Kharg Island,Mundra,Hormuz+Chabahar,4800,16,1200,78,0
```

**Fields**:
- `corridor`: Geopolitical chokepoint (Hormuz, Suez, Red Sea, etc.)
- `is_blocked`: Binary flag (1 = currently unavailable)

### 4.3 Ports Dataset (`backend/data/ports.csv`)

```
port_id,port_name,country,port_type,capacity_mbd,geopolitical_risk_score
P001,Ras Tanura,Saudi Arabia,export,3500,45
P002,Baku,Azerbaijan,export,500,52
P003,Houston,USA,export,600,20
P004,Mundra,India,import,2500,30
P005,Jawaharlal Nehru Port,India,import,1800,30
P006,Cochin Port,India,import,800,30
P007,Hormuz Strait,International,chokepoint,8000,65
```

### 4.4 Corridors Dataset (`backend/data/corridors.csv`)

```
corridor_name,location,baseline_risk_score,estimated_current_disruption_probability,affected_routes,affected_suppliers,india_import_percentage
Hormuz,Persian Gulf,65,0.15,R001|R002|R005,S001|S002|S003|S004|S005|S006,55
Suez,Red Sea,42,0.08,R004,S008,12
Red Sea,International Waters,48,0.10,R001|R002|R004,S001|S002|S008,35
Cape of Good Hope,South Africa,25,0.02,R003,S007,8
```

### 4.5 Sample Geopolitical Events (`backend/data/sample_events.json`)

```json
[
  {
    "event_id": "EVT001",
    "timestamp": "2026-08-19T10:30:00Z",
    "event_type": "geopolitical_tension",
    "location": "Strait of Hormuz",
    "description": "Naval tensions escalate near Strait of Hormuz, raising crude disruption concerns",
    "severity_raw": 0.72,
    "affected_corridor": "Hormuz",
    "india_relevance": 0.91,
    "source": "GDELT_NEWS",
    "confidence": 0.78
  },
  {
    "event_id": "EVT002",
    "timestamp": "2026-08-18T14:15:00Z",
    "event_type": "port_disruption",
    "location": "Novorossiysk Port, Russia",
    "description": "Technical issues reported at Novorossiysk export terminal",
    "severity_raw": 0.45,
    "affected_corridor": "Suez",
    "india_relevance": 0.65,
    "source": "GDELT_NEWS",
    "confidence": 0.62
  }
]
```

---

## 5. SQLite Database Schema

### Table: `geopolitical_events`

```sql
CREATE TABLE geopolitical_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    timestamp DATETIME NOT NULL,
    event_type TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    severity_raw REAL,
    affected_corridor TEXT,
    india_relevance REAL,
    source TEXT,
    raw_confidence REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `risk_assessments`

```sql
CREATE TABLE risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT UNIQUE NOT NULL,
    event_id TEXT,
    corridor_name TEXT,
    risk_score_ml REAL NOT NULL,
    risk_confidence REAL NOT NULL,
    disruption_probability_7d REAL,
    evidence_news_signal REAL,
    evidence_sanctions_signal REAL,
    evidence_historical REAL,
    india_exposure_percentage REAL,
    affected_suppliers TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(event_id) REFERENCES geopolitical_events(event_id)
);
```

### Table: `procurement_strategies`

```sql
CREATE TABLE procurement_strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id TEXT UNIQUE NOT NULL,
    strategy_type TEXT NOT NULL,
    risk_assessment_id TEXT,
    total_cost REAL,
    total_crude_supply REAL,
    avg_risk_score REAL,
    avg_transit_time REAL,
    supplier_concentration_ratio REAL,
    allocation_json TEXT,
    explanation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(risk_assessment_id) REFERENCES risk_assessments(assessment_id)
);
```

### Table: `supplier_allocations`

```sql
CREATE TABLE supplier_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id TEXT,
    supplier_id TEXT,
    allocation_percentage REAL,
    allocated_volume_mbd REAL,
    allocated_cost REAL,
    FOREIGN KEY(strategy_id) REFERENCES procurement_strategies(strategy_id)
);
```

---

## 6. ML Pipeline

### 6.1 Training Dataset Construction

**Approach**: Hybrid historical + synthetic

1. **Historical events**: GDELT events from past 2 years
2. **Labelled disruptions**: Manually curated historical corridor disruptions
3. **Synthetic scenarios**: Generated disruption scenarios for training diversity

**Features** (30-40 total):
- Event count (7d, 14d, 30d windows)
- Conflict intensity (avg Goldstein score)
- Sanctions exposure
- Shipping/logistics indicators (mocked)
- Oil price volatility
- Corridor historical disruption frequency
- Time since previous disruption
- Geographic proximity signals

**Target**: Binary or probability — P(corridor disruption in next 7 days)

### 6.2 Model

- **Algorithm**: XGBoost (for interpretability + performance)
- **Training approach**: Train on 80% historical + synthetic data, validate on 20%
- **Output**: Disruption probability (0-1), shap values for explainability
- **Model storage**: Pickle file at `backend/models/disruption_predictor.pkl`

### 6.3 Training Script Location

`backend/app/ml/training.py`

---

## 7. API Endpoints

### 7.1 Event Management

```
POST   /api/events                 → Ingest geopolitical event
GET    /api/events                 → List recent events
GET    /api/events/{event_id}      → Get event details
DELETE /api/events/{event_id}      → Delete event
```

### 7.2 Risk Analysis

```
POST   /api/analysis/risk          → Analyze risk for event
GET    /api/analysis/risk/{id}     → Get risk assessment
GET    /api/corridors/risk         → Get all corridor risks
```

### 7.3 Procurement Optimization

```
POST   /api/optimization/strategies → Generate procurement strategies
GET    /api/optimization/{id}      → Get strategy details
GET    /api/optimization/compare   → Compare strategies
```

### 7.4 Data

```
GET    /api/data/suppliers         → Get supplier list
GET    /api/data/routes            → Get routes
GET    /api/data/corridors         → Get corridors
```

---

## 8. Frontend Components

### 8.1 Dashboard (Main View)

- **Risk Summary Card**: Overall India crude risk (0-100)
- **Critical Chokepoints**: Hormuz, Red Sea, Suez, etc. with risk badges
- **Latest Events Feed**: Recent geopolitical events
- **India Exposure Gauge**: % of procurement exposed to risk
- **Action Button**: "Analyze Impact" → Risk Analysis view

### 8.2 Event Analysis View

- **Event Details**: Location, severity, duration, India relevance
- **Risk Scoring**: ML risk score + confidence
- **Evidence Panel**: News signals, sanctions signals, historical similarity
- **Conflicting Signals Alert**: If signals disagree
- **Affected Corridors**: List of impacted routes

### 8.3 Supply-Chain Graph View

- **Interactive Graph** (Cytoscape.js):
  - Nodes: Suppliers, ports, corridors, India
  - Edges: Routes with capacity/risk labels
  - Highlight affected routes/suppliers on risk event
- **Geospatial Map** (Leaflet):
  - Map of India, suppliers, ports, chokepoints
  - Route visualization overlaid

### 8.4 Procurement View

- **Risk Tolerance Slider**: LOW ←→ HIGH
- **Three Strategy Cards**:
  - Cheapest: Cost / Risk / Transit
  - Balanced: Cost / Risk / Transit
  - Safest: Cost / Risk / Transit
- **Recommended Strategy Highlight**
- **Supplier Allocation Chart**: Pie/bar chart of % distribution
- **Cost/Risk Tradeoff Visualization**
- **Explanation Panel**: Why this strategy recommended

---

## 9. Data Flow & Integration Points

### 9.1 User Flow: Default Dashboard

```
1. Frontend loads dashboard
2. API call: GET /api/corridors/risk
3. Backend fetches latest risk assessments from SQLite
4. Risk scores calculated from ML model + latest events
5. Display dashboard with risk cards + events feed
```

### 9.2 User Flow: New Geopolitical Event

```
1. User pastes news article or event description
2. Frontend: POST /api/events { description, location, etc. }
3. Backend:
   a. LLM extracts structured event info (via Ollama)
   b. Store in SQLite: geopolitical_events table
   c. Call ML inference: predict disruption probability
   d. Store in SQLite: risk_assessments table
   e. Calculate India supply exposure
   f. Return to frontend
4. Frontend: Display event + risk analysis
```

### 9.3 User Flow: Generate Procurement Strategy

```
1. User selects risk tolerance on Procurement view
2. Frontend: POST /api/optimization/strategies { risk_tolerance, event_id }
3. Backend:
   a. Fetch suppliers, routes, current allocations
   b. Set optimization objective (cost vs. risk tradeoff)
   c. Run Google OR-Tools solver
   d. Generate 3 strategies: cheapest, balanced, safest
   e. Store in SQLite: procurement_strategies table
   f. Return all 3 strategies
4. Frontend: Display comparison + recommend strategy
```

---

## 10. Mocked Data Sources

### 10.1 Sanctions Risk (Mocked)

```python
# backend/app/data/mock_sources.py

MOCK_SANCTIONS_EXPOSURE = {
    "S001": {"country": "Saudi Arabia", "sanctions_risk_score": 15},
    "S002": {"country": "Russia", "sanctions_risk_score": 85},
    "S003": {"country": "Iran", "sanctions_risk_score": 95},
    "S004": {"country": "UAE", "sanctions_risk_score": 20},
    # ...
}

def get_sanctions_exposure(supplier_id):
    return MOCK_SANCTIONS_EXPOSURE.get(supplier_id, {})
```

### 10.2 Trade/Energy Data (Mocked)

```python
# Historical supplier shares, India demand, etc.
MOCK_INDIA_CRUDE_DEMAND = 4.5  # million barrels per day

MOCK_SUPPLIER_SHARES = {
    "S001": 0.35,  # 35% of India crude from Saudi
    "S002": 0.28,  # 28% from Russia
    "S004": 0.18,  # 18% from UAE
    # ...
}
```

---

## 11. GDELT Integration

### 11.1 Data Fetching

```python
# backend/app/data/gdelt_fetcher.py

def fetch_gdelt_events(keywords, hours_back=24):
    """
    Fetch events from GDELT related to crude, geopolitical tensions, etc.
    Params:
    - keywords: ["Hormuz", "crude oil", "sanctions", ...]
    - hours_back: Historical window (default 24h)
    
    Returns: List of events with timestamp, description, location, etc.
    """
    # Calls GDELT API or GKG (GDELT 2.0)
    pass
```

### 11.2 Event Processing

Extract structured features:
- Location
- Event type (conflict, cooperation, etc.)
- Mentioned commodities
- Actors involved
- Goldstein score (conflict intensity, -10 to +10)

---

## 12. LLM Setup (Ollama + Qwen3 8B)

### 12.1 Important: Soft Dependency Design

**LLM is NOT a hard dependency**. The backend will run without Ollama initially, with LLM features gracefully disabled.

**Feature flags**:
- If Ollama is unavailable: Use fallback heuristic event extraction (regex + keyword matching)
- If Ollama is available: Use LLM for full structured event extraction
- Configuration: `config.py` specifies model name and base URL (easily switched later)

### 12.2 Installation (When Ready)

```bash
# Install Ollama (macOS/Linux/Windows)
# https://ollama.ai

# Then in terminal:
ollama pull qwen:8b

# Verify running (should show model info)
ollama list

# Start Ollama service (runs on http://localhost:11434)
# On macOS/Linux: ollama serve
# On Windows: Ollama app runs as background service
```

### 12.3 Configuration

```python
# backend/app/config.py

LLM_CONFIG = {
    "enabled": True,  # Set to False to disable LLM features
    "provider": "ollama",
    "model": "qwen:8b",  # Configurable, can be switched to qwen:13b, etc.
    "base_url": "http://localhost:11434",
    "timeout": 30,
}
```

### 12.4 Usage in Backend (With Graceful Fallback)

```python
# backend/app/agents/geopolitical_risk.py

from app.config import LLM_CONFIG
from app.agents.fallbacks import extract_event_heuristic

def extract_event_from_text(text):
    """
    Extract structured event from text.
    Tries LLM first, falls back to heuristic if unavailable.
    """
    if LLM_CONFIG.get("enabled"):
        try:
            return extract_event_llm(text)
        except ConnectionError:
            logger.warning("Ollama unavailable, using heuristic extraction")
            return extract_event_heuristic(text)
    else:
        return extract_event_heuristic(text)

def extract_event_llm(text):
    """LLM-based extraction (requires Ollama)"""
    from langchain.callbacks.manager import CallbackManager
    from langchain.llms import Ollama
    
    llm = Ollama(
        model=LLM_CONFIG["model"],
        base_url=LLM_CONFIG["base_url"],
    )
    
    prompt = f"""Extract structured geopolitical event:

{text}

Return JSON: {{"event_type": "...", "location": "...", "severity": 0.0, "disruption_probability": 0.0, "affected_corridor": "...", "india_relevance": 0.0}}"""
    
    response = llm(prompt)
    return response
```

### 12.5 Heuristic Fallback

```python
# backend/app/agents/fallbacks.py

import re

def extract_event_heuristic(text):
    """
    Fallback event extraction without LLM.
    Uses keywords + regex to extract basic structure.
    """
    event_type = "geopolitical_event"  # Default
    
    if "port" in text.lower() or "shipping" in text.lower():
        event_type = "port_disruption"
    if "sanction" in text.lower():
        event_type = "sanctions"
    
    # Extract location (simple heuristic)
    locations = ["Hormuz", "Suez", "Red Sea", "Cape of Good Hope", "Persian Gulf"]
    location = next((loc for loc in locations if loc.lower() in text.lower()), "Unknown")
    
    # Severity: 0-1 scale based on keywords
    severity = 0.5  # Default moderate
    if any(word in text.lower() for word in ["escalat", "crisis", "critical", "severe"]):
        severity = 0.75
    if any(word in text.lower() for word in ["minor", "report", "technical"]):
        severity = 0.35
    
    return {
        "event_type": event_type,
        "location": location,
        "severity": severity,
        "disruption_probability": severity * 0.8,
        "affected_corridor": location,
        "india_relevance": 0.7 if "india" in text.lower() else 0.5,
    }
```

---

## 13. Testing & Sample Scenarios

### 13.1 Unit Tests

```
backend/tests/
├── test_ml_inference.py          # Test ML model predictions
├── test_event_extraction.py      # Test LLM + event parsing
├── test_optimization.py          # Test OR-Tools solver
├── test_supply_exposure.py       # Test exposure calculation
└── test_database.py              # Test SQLite operations
```

### 13.2 Sample Scenarios

```
backend/data/test_scenarios.json

[
  {
    "scenario_id": "SC001",
    "name": "Hormuz escalation",
    "event": "Naval conflict in Strait of Hormuz",
    "expected_risk": 0.85,
    "expected_exposure": 0.55,
    "expected_strategies": ["diversify to US/Baku", "increase UAE/ADNOC", ...]
  },
  {
    "scenario_id": "SC002",
    "name": "Russia sanctions tightened",
    "event": "Additional sanctions on Russian oil",
    "expected_risk": 0.55,
    "expected_exposure": 0.28,
    "expected_strategies": ["reduce Rosneft allocation", "shift to Saudi/UAE", ...]
  }
]
```

---

## 14. Setup Instructions (High-Level)

### 14.1 Prerequisites

```bash
# System
Python 3.10+
Node.js 18+
Ollama (installed + running)

# Clone repo
git clone ...
cd CrudeNexus
```

### 14.2 Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Download/train ML model (if not included)
python app/ml/training.py --train

# Seed SQLite with sample data
python -m app.database.db init

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 14.3 Frontend Setup

```bash
cd frontend
npm install

# Development
npm run dev  # Runs on http://localhost:5173

# Build for prod
npm run build
```

### 14.4 Ollama Setup

```bash
# (Already installed)
# Verify service running
curl http://localhost:11434/api/tags
```

---

## 15. Execution Phases

### Phase 1: Project Scaffolding
- [ ] Create directory structure
- [ ] Initialize monorepo Git history
- [ ] Create requirements.txt + package.json
- [ ] Set up backend FastAPI skeleton
- [ ] Set up frontend Angular skeleton

### Phase 2: Data Layer
- [ ] Create CSV/JSON files (suppliers, routes, ports, corridors, sample events)
- [ ] Create SQLite schema + initialization script
- [ ] Create CSV loaders + mock data sources

### Phase 3: Backend Core
- [x] Pydantic models (Event, Supplier, Optimization)
- [x] SQLAlchemy ORM + database init
- [x] API endpoints (CRUD for events, data retrieval)

### Phase 4: ML Pipeline
- [x] Feature engineering module
- [x] Training dataset construction + labelling
- [x] Model training (XGBoost)
- [x] Inference module

Phase 4 provides a reproducible prototype disruption-prediction pipeline. It transforms recent corridor events and documented baseline signals into 21 stable features, generates a labelled synthetic dataset until historical data is connected, and persists an XGBoost artifact with its schema and validation metadata. Inference validates the feature contract and returns a seven-day disruption probability, calibrated confidence, and the strongest contributing signals.

Run `python -m app.ml.training` from `backend/` to create `models/disruption_predictor.pkl`; provide `--data-file` with a labelled CSV containing the same feature schema to retrain on external data.

### Phase 5: Risk Intelligence Agent
- [x] LLM integration (Ollama + Qwen)
- [x] Event extraction logic
- [x] Risk scoring + confidence
- [x] Signal conflict detection

Phase 5 adds a soft-dependency Ollama extractor that requests structured JSON and validates it before use; unavailable, malformed, or disabled LLM calls transparently fall back to deterministic heuristics. The risk agent combines event severity, India relevance, recency, sanctions, corridor history, and optional Phase 4 predictions into an explainable seven-day disruption score. It also flags material disagreement between news, sanctions, historical, and model signals so downstream recommendations can communicate uncertainty.

### Phase 6: Supply Chain & Optimization
- [x] NetworkX supply-chain graph
- [x] Supply exposure calculation
- [x] OR-Tools procurement optimizer
- [x] Multi-strategy generation (cheapest, balanced, safest)

Phase 6 models each committed supplier-to-India maritime path in a NetworkX graph and calculates exposure from the corridor master dataset instead of hard-coded mappings. Its OR-Tools optimizer enforces supplier and route capacities, excludes blocked corridors/routes, incorporates an active risk assessment into route risk, and produces cheapest, balanced, and safest allocations with cost, risk, transit, and concentration metrics.

### Phase 7: API Integration
- [x] Connect all endpoints
- [x] Database persistence
- [x] Error handling + validation

Phase 7 verifies the complete backend workflow: an event is ingested, risk-assessed, persisted, used as optimization context, and returned as a retrievable procurement strategy. API request models validate event text, risk tolerance, demand, and blocked corridors; route, supplier, allocation, risk-evidence, and conflict data are consistently serialized for clients.

### Phase 8: Frontend (Basic)
- [x] Dashboard view (risk cards, events feed)
- [x] Event analysis view
- [x] Procurement strategies view
- [x] API service integration

Phase 8 delivers a standalone Angular dashboard with India corridor-risk cards, an event-analysis form, latest-event feed, procurement risk-tolerance control, side-by-side strategy comparison, and a route view. The shared API and state services connect those views to the FastAPI endpoints and provide visible loading and failure states when the backend is unavailable.

### Phase 9: Testing & Data
- [x] Unit tests for core modules (backend pytest suite: loader, ML pipeline, optimization, API workflow)
- [x] Sample scenarios + integration test (validated end-to-end Event → Risk → Strategy API workflow)
- [x] GDELT data fetching + processing (resilient fetcher and parsing in backend/app/data/loaders.py)

Summary: Phase 9 is complete. The backend now includes a safe GDELT fetcher with graceful error handling, a focused loader unit test, and a passing end-to-end workflow test that exercises API-driven event ingestion, risk generation, and strategy selection. The local backend test suite passes in the project venv and confirms the system remains stable during data-fetching failures.

### Phase 10: Deployment & Documentation
- [ ] Setup instructions
- [ ] API documentation
- [ ] Deployment guide

---

## 16. Success Criteria (MVP Complete)

The MVP is complete when:

1. ✅ Backend FastAPI running, all endpoints functional
2. ✅ SQLite persisting events, risk assessments, strategies
3. ✅ ML model predicting disruption probability (even if accuracy low initially)
4. ✅ LLM (Ollama/Qwen) extracting structured events from text
5. ✅ OR-Tools generating 3 procurement strategies (cheapest, balanced, safest)
6. ✅ Frontend dashboard displaying:
   - Risk summary
   - Chokepoint risk cards
   - Event feed
   - India exposure %
7. ✅ End-to-end workflow: Event → Risk → Exposure → Strategy → Display
8. ✅ Sample scenario execution produces sensible recommendations

---

## 17. Notes & Assumptions

- **Qwen 3.8B assumption**: Assumed user meant 3.8B parameters; if 38B intended, model will be larger but more capable
- **LLM accuracy**: Initial LLM event extraction may require prompt tuning
- **ML model accuracy**: Model will improve as historical disruption data accumulated
- **Mocked data realism**: Sanctions/trade data are simplified for MVP; can be replaced with real APIs later
- **Graph visualization**: Cytoscape.js for interactive graph; Leaflet for geospatial
- **OR-Tools solver**: Will use SCIP backend (free); can upgrade to commercial solver if needed

---

## Ready to Execute?

This plan is comprehensive and execution-ready. All structure, dependencies, schemas, and workflows are defined.

**Proceed with Phase 1 (Project Scaffolding)?** → Answer YES to start.
