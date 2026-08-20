from datetime import datetime, timezone
from types import SimpleNamespace

from app.agents import geopolitical_risk


def test_heuristic_extraction_when_llm_is_disabled(monkeypatch):
    monkeypatch.setitem(geopolitical_risk.LLM_CONFIG, "enabled", False)
    event = geopolitical_risk.extract_event_from_text("Severe tanker disruption in the Strait of Hormuz threatens Indian crude imports")
    assert event["extraction_method"] == "heuristic"
    assert event["affected_corridor"] == "Hormuz"
    assert event["severity"] >= .8


def test_llm_response_is_normalized(monkeypatch):
    monkeypatch.setitem(geopolitical_risk.LLM_CONFIG, "enabled", True)
    monkeypatch.setattr(geopolitical_risk, "_extract_event_llm", lambda _: {"event_type": "blockade", "location": "Hormuz", "severity": 1.4, "affected_corridor": "Hormuz", "india_relevance": .9, "confidence": .88})
    event = geopolitical_risk.extract_event_from_text("Any text")
    assert event["extraction_method"] == "ollama"
    assert event["event_type"] == "blockade"
    assert event["severity"] == 1


def test_conflicting_evidence_is_explained():
    result = geopolitical_risk.detect_signal_conflict(.9, .1, .2, .85)
    assert result["conflicting_signals"]
    assert "conflicts" in result["conflicting_signals_detail"]


def test_risk_score_works_without_a_trained_model(monkeypatch):
    monkeypatch.setattr("app.ml.inference._load_artifact", lambda: (_ for _ in ()).throw(FileNotFoundError()))
    event = SimpleNamespace(timestamp=datetime.now(timezone.utc), severity_raw=.8, india_relevance=.9, raw_confidence=.8, event_type="blockade", affected_corridor="Hormuz")
    score = geopolitical_risk.calculate_risk_score(event)
    assert 0 <= score["risk_score_ml"] <= 100
    assert 0 <= score["confidence"] <= 1
    assert score["conflicting_signals"]
