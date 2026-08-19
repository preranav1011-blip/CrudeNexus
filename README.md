# CrudeNexus: EnergyResilience AI for India

**AI-powered decision-intelligence platform for India's crude-oil supply chain resilience.**

Detects geopolitical disruptions, assesses India's procurement exposure, and generates explainable, risk-aware procurement strategies in real-time.

---

## 🎯 Quick Start

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **Git** (already initialized)
- **Ollama** (optional, for LLM features; instructions below)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m app.database.db init

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at `http://localhost:8000`

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at `http://localhost:5173`

### 3. Optional: Ollama Setup for LLM Features

The backend runs **without Ollama** — LLM features are gracefully disabled if Ollama is unavailable.

To enable LLM-based event extraction:

#### Installation

1. **Download Ollama** from https://ollama.ai
2. **Install** for your OS (macOS/Linux/Windows)
3. **Run** Ollama service:
   ```bash
   ollama serve
   # Starts on http://localhost:11434
   ```
4. **Pull the model**:
   ```bash
   ollama pull qwen:8b
   ```
5. **Verify**:
   ```bash
   ollama list  # Should show qwen:8b
   ```

#### Testing Connection

```bash
# From backend directory
curl http://localhost:11434/api/tags

# Should return model list including qwen:8b
```

#### Switching Models

Edit `backend/app/config.py`:
```python
LLM_CONFIG = {
    "enabled": True,
    "model": "qwen:8b",  # Change to qwen:13b, mistral, etc.
    "base_url": "http://localhost:11434",
}
```

---

## 📋 Project Structure

```
CrudeNexus/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # API entrypoint
│   │   ├── config.py          # Configuration (LLM, database, etc.)
│   │   ├── models/            # Pydantic models
│   │   ├── agents/            # Business logic (risk, optimization)
│   │   ├── ml/                # ML pipeline (training, inference)
│   │   ├── data/              # Data loaders
│   │   ├── database/          # SQLite ORM
│   │   └── routes/            # API endpoints
│   ├── data/
│   │   ├── suppliers.csv      # Indian crude suppliers
│   │   ├── routes.csv         # Maritime routes
│   │   ├── ports.csv          # Port data
│   │   ├── corridors.csv      # Critical chokepoints
│   │   └── sample_events.json # Test events
│   ├── models/                # Trained ML models
│   ├── requirements.txt       # Python dependencies
│   └── pytest.ini
├── frontend/                   # Angular frontend
│   ├── src/
│   │   ├── app/               # Angular components
│   │   │   ├── dashboard/
│   │   │   ├── supply-chain/
│   │   │   └── procurement/
│   │   └── services/          # API integration
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # Documentation
│   ├── SETUP.md
│   ├── API.md
│   └── ML_MODEL.md
├── IMPLEMENTATION_PLAN.md      # Detailed build plan
└── README.md (this file)
```

---

## 🚀 API Endpoints

### Events
- `POST /api/events` — Ingest geopolitical event
- `GET /api/events` — List recent events
- `GET /api/events/{event_id}` — Get event details

### Risk Analysis
- `POST /api/analysis/risk` — Analyze risk for event
- `GET /api/analysis/risk/{id}` — Get risk assessment
- `GET /api/corridors/risk` — Get all corridor risks

### Procurement Optimization
- `POST /api/optimization/strategies` — Generate strategies
- `GET /api/optimization/{id}` — Get strategy details

### Data
- `GET /api/data/suppliers` — List suppliers
- `GET /api/data/routes` — List routes
- `GET /api/data/corridors` — List corridors

Full API docs available at `http://localhost:8000/docs` (FastAPI Swagger UI)

---

## 🧠 LLM Architecture

### Soft Dependency Design

**Ollama is optional**. The system has two modes:

1. **LLM Enabled** (Ollama running):
   - Uses Qwen 8B for event extraction
   - Full structured geopolitical signal extraction
   - Better accuracy on complex events

2. **LLM Disabled** (Ollama not available):
   - Falls back to keyword/regex heuristic extraction
   - Basic event structure still produced
   - App runs normally, just less intelligent

**Status** is logged on backend startup:
```
2026-08-19 10:30:45 | INFO  | LLM Status: ENABLED (Qwen 8B)
2026-08-19 10:30:45 | INFO  | Using fallback heuristic extraction
```

---

## 📊 Frontend Views

### Dashboard
- India crude risk summary (0-100)
- Critical chokepoints (Hormuz, Suez, Red Sea, Cape of Good Hope)
- Latest geopolitical events feed
- India supply chain exposure %

### Event Analysis
- Event details (location, severity, India relevance)
- ML risk score + confidence
- Evidence breakdown
- Affected corridors

### Supply-Chain Graph
- Interactive network visualization (Cytoscape.js)
- Suppliers, ports, routes, chokepoints
- Geospatial map (Leaflet + OpenStreetMap)

### Procurement Strategies
- Three competing strategies: Cheapest, Balanced, Safest
- Supplier allocation pie chart
- Cost/Risk/Transit tradeoffs
- Explainable recommendation

---

## 🔧 Configuration

### Backend Config

`backend/app/config.py`:
```python
# Database
DATABASE_URL = "sqlite:///./crudenexus.db"

# LLM (Ollama)
LLM_CONFIG = {
    "enabled": True,
    "provider": "ollama",
    "model": "qwen:8b",
    "base_url": "http://localhost:11434",
    "timeout": 30,
}

# GDELT
GDELT_KEYWORDS = ["crude oil", "Hormuz", "sanctions", "tanker", ...]
GDELT_LOOKBACK_HOURS = 24

# Optimization
INDIA_CRUDE_DEMAND_MBD = 4.5  # million barrels/day
```

### Frontend Config

`frontend/src/environments/environment.ts`:
```typescript
export const environment = {
  apiUrl: 'http://localhost:8000/api',
  production: false,
};
```

---

## 📈 ML Model

**Model**: XGBoost (trained on historical events + synthetic scenarios)

**Input Features** (~35):
- Event count (7d, 14d, 30d windows)
- Conflict intensity (GDELT Goldstein scores)
- Sanctions exposure
- Shipping indicators (mocked initially)
- Oil price volatility
- Corridor disruption history
- Geospatial proximity signals

**Output**: P(corridor disruption in next 7 days) [0-1]

**Model File**: `backend/models/disruption_predictor.pkl`

**Retrain**: As real disruption data accumulates, retrain with:
```bash
cd backend
python app/ml/training.py --retrain --data-file new_disruptions.csv
```

---

## 📚 Data Sources

### Real (Integrated)
- **GDELT**: Geopolitical event data
- **India Supply Dataset**: Curated CSV of suppliers, routes, ports

### Mocked (MVP)
- **Sanctions Data**: Placeholder scores per supplier
- **Trade Data**: Historical India import shares
- **Shipping Indicators**: Synthetic logistics signals

**Upgrade plan**: Replace mock sources with real APIs (UN Comtrade, EIA, etc.) post-MVP.

---

## 🧪 Testing

### Unit Tests
```bash
cd backend
pytest tests/
```

### Sample Scenarios
```bash
python scripts/run_sample_scenarios.py
```

Executes test cases:
- Hormuz escalation → expects high exposure, diversification strategy
- Russia sanctions → expects shift away from Rosneft
- Suez disruption → expects rerouting via Cape of Good Hope

---

## 📖 Documentation

- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) — Full technical architecture
- [docs/SETUP.md](docs/SETUP.md) — Detailed setup guide
- [docs/API.md](docs/API.md) — API reference
- [docs/ML_MODEL.md](docs/ML_MODEL.md) — ML pipeline details

---

## 🗂️ Development Workflow

### Make Backend Changes
```bash
cd backend
source venv/bin/activate
# Edit files in app/
uvicorn app.main:app --reload  # Auto-reloads on save
```

### Make Frontend Changes
```bash
cd frontend
npm run dev
# Edit files in src/
# Browser auto-refreshes
```

### Debug ML Model
```bash
cd backend
python
>>> from app.ml.inference import predict_disruption
>>> score = predict_disruption(features)
>>> print(score)
```

---

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Check virtual environment activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend dev server fails
```bash
# Clear cache & node_modules
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Ollama connection error
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# If error, restart Ollama service and pull model
ollama pull qwen:8b
ollama serve
```

### Database errors
```bash
# Reset database
rm backend/crudenexus.db
cd backend
python -m app.database.db init
```

---

## 🌍 Deployment (Future)

- **Backend**: Docker + Cloud Run / AWS Lambda
- **Frontend**: Vercel / Netlify
- **Database**: PostgreSQL (upgrade from SQLite)
- **LLM**: Self-hosted Ollama or cloud LLM API

---

## 📝 License

TBD

---

## 👥 Contributing

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for development phases and architecture.

---

## 📞 Support

For questions or issues, refer to:
1. [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) — Technical design
2. [docs/SETUP.md](docs/SETUP.md) — Detailed setup
3. Code comments in `backend/app/` and `frontend/src/`
