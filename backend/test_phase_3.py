#!/usr/bin/env python3
"""
Phase 3: Backend Core - Test Suite
Tests all CRUD operations, risk assessment, and optimization
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.database.db import SessionLocal, Base, engine
from app.database.models import GeopoliticalEvent, RiskAssessment, ProcurementStrategy
from app.agents.geopolitical_risk import calculate_risk_score, extract_event_from_text
from app.agents.supply_exposure import calculate_supply_exposure
from app.agents.procurement_optimizer import optimize_procurement
from app.data.csv_loaders import SupplierLoader, RouteLoader


def setup_test_database():
    """Initialize clean database for testing"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✓ Test database initialized")


def test_event_creation():
    """Test event creation and CRUD"""
    print("\n[1/6] Testing Event Creation & Management...")
    db = SessionLocal()
    
    try:
        # Create event
        event = GeopoliticalEvent(
            event_id="EVT_TEST_001",
            timestamp=datetime.utcnow(),
            event_type="geopolitical_tension",
            location="Strait of Hormuz",
            description="Naval tensions escalate between Iran and UAE",
            severity_raw=0.75,
            affected_corridor="C001",
            india_relevance=0.9,
            source="TEST",
            raw_confidence=0.85
        )
        
        db.add(event)
        db.commit()
        
        # Retrieve event
        retrieved = db.query(GeopoliticalEvent).filter_by(
            event_id="EVT_TEST_001"
        ).first()
        
        assert retrieved is not None, "Event not found"
        assert retrieved.location == "Strait of Hormuz"
        print("✓ Event creation: PASSED")
        
        # List events
        all_events = db.query(GeopoliticalEvent).all()
        assert len(all_events) >= 1
        print(f"✓ Event listing: PASSED ({len(all_events)} events)")
        
        # Delete event
        db.delete(retrieved)
        db.commit()
        
        deleted = db.query(GeopoliticalEvent).filter_by(
            event_id="EVT_TEST_001"
        ).first()
        
        assert deleted is None
        print("✓ Event deletion: PASSED")
        
    except Exception as e:
        print(f"✗ Event test failed: {e}")
        return False
    finally:
        db.close()
    
    return True


def test_risk_scoring():
    """Test risk assessment calculation"""
    print("\n[2/6] Testing Risk Scoring...")
    db = SessionLocal()
    
    try:
        # Create test event with known values
        event = GeopoliticalEvent(
            event_id="EVT_RISK_001",
            timestamp=datetime.utcnow(),
            event_type="port_disruption",
            location="Suez Canal",
            description="Suez Canal blockade reported",
            severity_raw=0.8,
            affected_corridor="C002",
            india_relevance=0.7,
            source="TEST",
            raw_confidence=0.9
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        # Calculate risk
        risk_data = calculate_risk_score(event)
        
        assert "risk_score_ml" in risk_data
        assert "confidence" in risk_data
        assert "disruption_probability" in risk_data
        assert 0 <= risk_data["risk_score_ml"] <= 100
        assert 0 <= risk_data["confidence"] <= 1
        
        print(f"✓ Risk score calculation: {risk_data['risk_score_ml']:.0f}/100")
        print(f"  Confidence: {risk_data['confidence']:.2f}")
        print(f"  Disruption prob: {risk_data['disruption_probability']:.2f}")
        
        # Create risk assessment
        risk_assessment = RiskAssessment(
            assessment_id="RSK_TEST_001",
            event_id=event.event_id,
            corridor_name="C002",
            risk_score_ml=risk_data["risk_score_ml"],
            risk_confidence=risk_data["confidence"],
            disruption_probability_7d=risk_data["disruption_probability"],
            india_exposure_percentage=30.0
        )
        
        db.add(risk_assessment)
        db.commit()
        
        # Retrieve
        retrieved = db.query(RiskAssessment).filter_by(
            assessment_id="RSK_TEST_001"
        ).first()
        
        assert retrieved is not None
        print("✓ Risk assessment storage: PASSED")
        
    except Exception as e:
        print(f"✗ Risk scoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True


def test_supply_exposure():
    """Test supply exposure calculation"""
    print("\n[3/6] Testing Supply Exposure Calculation...")
    
    try:
        # Test each corridor
        corridors = ["Strait of Hormuz", "Suez Canal", "Red Sea Route", "Cape of Good Hope"]
        
        for corridor in corridors:
            exposure = calculate_supply_exposure(
                corridor=corridor,
                risk_score=60,
                event=None
            )
            
            assert "exposed_percentage" in exposure
            assert "affected_suppliers" in exposure
            assert exposure["exposed_percentage"] >= 0
            
            if exposure["exposed_percentage"] > 0:
                print(f"  - {corridor}: {exposure['exposed_percentage']:.0f}% exposed, "
                      f"{len(exposure['affected_suppliers'])} suppliers affected")
        
        print("✓ Supply exposure calculation: PASSED")
        
    except Exception as e:
        print(f"✗ Supply exposure test failed: {e}")
        return False
    
    return True


def test_procurement_optimization():
    """Test procurement strategy generation"""
    print("\n[4/6] Testing Procurement Optimization...")
    
    try:
        suppliers = SupplierLoader.load_suppliers()
        routes = RouteLoader.load_routes()
        
        if not suppliers or not routes:
            raise ValueError("Missing supplier or route data")
        
        print(f"  - Loaded {len(suppliers)} suppliers")
        print(f"  - Loaded {len(routes)} routes")
        
        # Generate strategies
        cheapest, balanced, safest = optimize_procurement(
            suppliers=suppliers,
            routes=routes,
            india_demand_mbd=4.5,
            risk_tolerance=0.5,
            blocked_corridors=[]
        )
        
        # Validate cheapest strategy
        assert cheapest.get("strategy_type") == "cheapest"
        assert cheapest.get("total_crude_supply") >= 4.0
        assert len(cheapest.get("allocations", [])) > 0
        avg_risk = cheapest.get("avg_risk_score", 50)
        cost = cheapest.get("total_cost", 0)
        
        print(f"✓ Cheapest strategy:")
        print(f"    Cost: ${cost:,.0f}M/year")
        print(f"    Risk: {avg_risk:.0f}/100")
        print(f"    Suppliers: {len(cheapest.get('allocations', []))}")
        
        # Validate balanced strategy
        assert balanced.get("strategy_type") == "balanced"
        assert balanced.get("total_crude_supply") >= 4.0
        avg_risk = balanced.get("avg_risk_score", 50)
        cost = balanced.get("total_cost", 0)
        
        print(f"✓ Balanced strategy:")
        print(f"    Cost: ${cost:,.0f}M/year")
        print(f"    Risk: {avg_risk:.0f}/100")
        print(f"    Suppliers: {len(balanced.get('allocations', []))}")
        
        # Validate safest strategy
        assert safest.get("strategy_type") == "safest"
        assert safest.get("total_crude_supply") >= 4.0
        avg_risk = safest.get("avg_risk_score", 50)
        cost = safest.get("total_cost", 0)
        
        print(f"✓ Safest strategy:")
        print(f"    Cost: ${cost:,.0f}M/year")
        print(f"    Risk: {avg_risk:.0f}/100")
        print(f"    Suppliers: {len(safest.get('allocations', []))}")
        
    except Exception as e:
        print(f"✗ Procurement optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_event_extraction():
    """Test LLM/heuristic event extraction"""
    print("\n[5/6] Testing Event Extraction...")
    
    try:
        test_texts = [
            "Iran threatens to block Strait of Hormuz after US sanctions",
            "Suez Canal experiences congestion due to weather",
            "Russian oil sanctions tighten as sanctions escalate",
        ]
        
        for text in test_texts:
            extracted = extract_event_from_text(text)
            
            assert "severity" in extracted or "event_type" in extracted
            print(f"✓ Extracted from: '{text[:50]}...'")
        
        print("✓ Event extraction: PASSED")
        
    except Exception as e:
        print(f"✗ Event extraction test failed: {e}")
        return False
    
    return True


def test_risk_corridor_analysis():
    """Test corridor-level risk analysis"""
    print("\n[6/6] Testing Corridor Risk Analysis...")
    db = SessionLocal()
    
    try:
        from app.data.csv_loaders import CorridorLoader
        
        corridors = CorridorLoader.load_corridors()
        
        for corridor in corridors:
            corridor_name = corridor.get('corridor_name', '')
            india_traffic = corridor.get('annual_traffic_pct_india', 0)
            
            if india_traffic > 0:
                print(f"  - {corridor_name}: {india_traffic}% of India's crude traffic")
        
        print(f"✓ Identified {len(corridors)} critical corridors")
        print("✓ Corridor analysis: PASSED")
        
    except Exception as e:
        print(f"✗ Corridor analysis test failed: {e}")
        return False
    finally:
        db.close()
    
    return True


def main():
    """Run all Phase 3 tests"""
    print("\n" + "="*70)
    print("PHASE 3: BACKEND CORE - TEST SUITE")
    print("="*70)
    
    try:
        # Setup
        setup_test_database()
        
        # Run tests
        results = [
            ("Event Management", test_event_creation()),
            ("Risk Scoring", test_risk_scoring()),
            ("Supply Exposure", test_supply_exposure()),
            ("Procurement Optimization", test_procurement_optimization()),
            ("Event Extraction", test_event_extraction()),
            ("Corridor Analysis", test_risk_corridor_analysis()),
        ]
        
        # Summary
        print("\n" + "="*70)
        print("PHASE 3 TEST RESULTS")
        print("="*70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASSED" if result else "✗ FAILED"
            print(f"{test_name}: {status}")
        
        print("\n" + "="*70)
        print(f"TOTAL: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n✓ PHASE 3: ALL TESTS PASSED")
            print("="*70)
            print("\nPhase 3 Core Backend is fully operational:")
            print("  ✓ Event CRUD operations working")
            print("  ✓ Risk assessment calculation working")
            print("  ✓ Supply exposure analysis working")
            print("  ✓ Procurement optimization working (basic)")
            print("  ✓ Event extraction working")
            print("  ✓ Corridor risk analysis working")
            print("\nNext: Start backend server and test API endpoints")
            print("  uvicorn app.main:app --reload")
            print("="*70)
            return 0
        else:
            print(f"\n✗ {total - passed} test(s) failed")
            return 1
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
