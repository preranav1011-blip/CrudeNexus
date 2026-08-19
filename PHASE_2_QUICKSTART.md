# Phase 2: Quick Start Guide

## What You Now Have

✅ **Data Layer Complete**
- 8 suppliers, 6 routes, 12 ports, 5 corridors loaded from CSV
- 3 sample geopolitical events in database
- 5 REST API endpoints serving data
- Comprehensive test suite (all tests passing)

---

## To Use Phase 2

### 1️⃣ Seed Database (One-time)
```bash
cd backend && python -m app.data.seed_data
```

Output:
```
✓ 8 suppliers loaded
✓ 6 routes loaded
✓ 12 ports loaded
✓ 5 corridors loaded
✓ Sample geopolitical events seeded
```

### 2️⃣ Run Tests
```bash
cd backend && python test_phase_2.py
```

Output:
```
PHASE 2 TEST SUITE: ✓ ALL TESTS PASSED
```

### 3️⃣ Start Backend Server
```bash
cd backend && uvicorn app.main:app --reload
```

Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 4️⃣ Test API Endpoints

**Option A: curl**
```bash
curl http://localhost:8000/api/data/suppliers | python -m json.tool
curl http://localhost:8000/api/data/routes | python -m json.tool
curl http://localhost:8000/api/data/ports | python -m json.tool
curl http://localhost:8000/api/data/corridors | python -m json.tool
```

**Option B: Browser**
- Visit http://localhost:8000/docs for interactive API docs
- Click "Try it out" on each endpoint

---

## API Endpoints

| Endpoint | Returns | Example |
|----------|---------|---------|
| `GET /api/data/suppliers` | 8 suppliers | Saudi Aramco, Rosneft, etc. |
| `GET /api/data/routes` | 6 routes | Saudi→Paradip, Russia→Mangalore |
| `GET /api/data/ports` | 12 ports | Ras Tanura, Paradip, etc. |
| `GET /api/data/corridors` | 5 chokepoints | Hormuz, Suez, Red Sea |
| `GET /api/data/refresh-cache` | Cache status | Reloads all CSVs |

---

## Sample API Response

```bash
$ curl http://localhost:8000/api/data/suppliers
[
  {
    "supplier_id": "S001",
    "name": "Saudi Aramco",
    "country": "Saudi Arabia",
    "capacity_mbd": 3500.0,
    "cost_per_barrel": 75.0,
    "geopolitical_risk": 45.0
  },
  {
    "supplier_id": "S002",
    "name": "Rosneft",
    "country": "Russia",
    "capacity_mbd": 2800.0,
    "cost_per_barrel": 70.0,
    "geopolitical_risk": 68.0
  }
]
```

---

## Database Check

### View Events in Database
```bash
cd backend
sqlite3 crudenexus.db "SELECT COUNT(*) FROM geopolitical_events;"
# Output: 3
```

### See Event Details
```bash
sqlite3 crudenexus.db "SELECT event_id, location, event_type FROM geopolitical_events;"
```

---

## Files Created/Modified

### New Files
- `backend/app/data/csv_loaders.py` - CSV data loaders
- `backend/app/data/seed_data.py` - Database seeding script  
- `backend/test_phase_2.py` - Test suite

### Modified Files
- `backend/app/routes/data.py` - Implemented data endpoints
- `backend/app/models/supplier.py` - Added port model

### Data Files (Already Exist)
- `backend/data/suppliers.csv`
- `backend/data/routes.csv`
- `backend/data/ports.csv`
- `backend/data/corridors.csv`
- `backend/data/sample_events.json`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError" | Run from `backend/` directory |
| "CSV not found" | Check `backend/data/` folder exists |
| "Address already in use" | Use different port: `--port 8001` |
| API returns no data | Run `python -m app.data.seed_data` first |
| Tests fail | Most likely need venv: `source venv/bin/activate` |

---

## Next Steps → Phase 3

Once Phase 2 is working, Phase 3 will add:
- ✏️ CRUD operations for events
- 📊 Risk assessment calculations
- 🔗 Supply chain exposure analysis
- 🤖 ML model integration
- 📈 Procurement optimization

See [PHASE_2_COMPLETE.md](PHASE_2_COMPLETE.md) for full details.

---

## Commands Summary

```bash
# Setup (one-time)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Development workflow
python -m app.data.seed_data      # Populate database
python test_phase_2.py             # Run tests
uvicorn app.main:app --reload     # Start server
# Then test: curl http://localhost:8000/api/data/suppliers
```

---

**Status**: ✅ COMPLETE | **Test Results**: ✅ PASSED | **Ready for Phase 3**: ✅ YES
