"""Geopolitical risk intelligence with an optional Ollama extraction provider."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import re
from typing import Any, Dict
import requests

from app.config import LLM_CONFIG
from app.data.fallbacks import extract_event_heuristic

logger = logging.getLogger(__name__)
EVENT_TYPES = {"geopolitical_tension", "geopolitical_conflict", "port_disruption", "sanctions", "blockade", "price_movement", "geopolitical_event"}


def _clamp(value: Any, default: float) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def _json_from_response(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("LLM response did not contain a JSON object")
        return json.loads(match.group())


def _extract_event_llm(text: str) -> Dict:
    """Call Ollama's HTTP API. This provider is a soft dependency."""
    prompt = f"""Extract the India crude-supply event below. Return only JSON with event_type,
location, severity, disruption_probability, affected_corridor, india_relevance, confidence.
All numeric values must be between 0 and 1. Use: {', '.join(sorted(EVENT_TYPES))}.

Event: {text}"""
    response = requests.post(
        f"{LLM_CONFIG['base_url'].rstrip('/')}/api/generate",
        json={"model": LLM_CONFIG["model"], "prompt": prompt, "stream": False, "format": "json"},
        timeout=LLM_CONFIG["timeout"],
    )
    response.raise_for_status()
    return _json_from_response(response.json().get("response", ""))


def _normalize_extraction(payload: Dict, fallback: Dict) -> Dict:
    """Validate untrusted model output and deterministically fill missing fields."""
    event_type = str(payload.get("event_type") or fallback["event_type"]).lower().strip()
    if event_type not in EVENT_TYPES:
        event_type = fallback["event_type"]
    location = str(payload.get("location") or fallback["location"]).strip() or "Unknown"
    corridor = str(payload.get("affected_corridor") or fallback["affected_corridor"]).strip() or fallback["affected_corridor"]
    severity = _clamp(payload.get("severity"), fallback["severity"])
    return {"event_type": event_type, "location": location, "severity": severity,
            "disruption_probability": _clamp(payload.get("disruption_probability"), severity * .8),
            "affected_corridor": corridor, "india_relevance": _clamp(payload.get("india_relevance"), fallback["india_relevance"]),
            "confidence": _clamp(payload.get("confidence"), .65), "extraction_method": "ollama"}


def extract_event_from_text(text: str) -> Dict:
    """Extract a structured event using Ollama when available, otherwise heuristics."""
    fallback = extract_event_heuristic(text)
    if not text or not LLM_CONFIG.get("enabled"):
        return {**fallback, "extraction_method": "heuristic"}
    try:
        return _normalize_extraction(_extract_event_llm(text), fallback)
    except (requests.RequestException, ValueError, TypeError, json.JSONDecodeError) as error:
        logger.info("Ollama extraction unavailable or invalid (%s); using heuristic fallback", error)
        return {**fallback, "extraction_method": "heuristic"}


def detect_signal_conflict(news_signal: float, sanctions_signal: float, historical_signal: float,
                           model_signal: float | None = None) -> Dict:
    """Flag materially divergent evidence for an explainable user warning."""
    signals = {"news": _clamp(news_signal, 0), "sanctions": _clamp(sanctions_signal, 0), "historical": _clamp(historical_signal, 0)}
    if model_signal is not None:
        signals["model"] = _clamp(model_signal, 0)
    low, high = min(signals.values()), max(signals.values())
    conflict = high - low >= .45
    detail = None
    if conflict:
        high_sources = ", ".join(name for name, value in signals.items() if value >= high - .05)
        low_sources = ", ".join(name for name, value in signals.items() if value <= low + .05)
        detail = f"High {high_sources} signal conflicts with low {low_sources} signal."
    return {"conflicting_signals": conflict, "conflicting_signals_detail": detail, "signals": signals}


def calculate_risk_score(event: Any) -> Dict:
    """Combine event, corridor, sanctions, history, and optional ML evidence."""
    severity = _clamp(getattr(event, "severity_raw", .5), .5)
    relevance = _clamp(getattr(event, "india_relevance", .5), .5)
    raw_confidence = _clamp(getattr(event, "raw_confidence", .5), .5)
    event_type = str(getattr(event, "event_type", "geopolitical_event")).lower()
    multipliers = {"geopolitical_tension": 1.2, "geopolitical_conflict": 1.35, "port_disruption": 1.5, "sanctions": 1.3, "blockade": 1.8, "price_movement": .8}
    rule_probability = _clamp(((severity + relevance) / 2) * multipliers.get(event_type, 1), .5)
    corridor = getattr(event, "affected_corridor", "Unknown") or "Unknown"
    historical_signal, model_probability = .35, None
    try:
        from app.ml.feature_engineering import engineer_features
        from app.ml.inference import predict_disruption
        features = engineer_features([event], corridor)
        historical_signal = features["historical_disruption_frequency"]
        model_probability = predict_disruption(corridor, features)["disruption_probability"]
    except (FileNotFoundError, ImportError, ValueError) as error:
        logger.debug("ML evidence unavailable: %s", error)
    sanctions_signal = .75 if "sanction" in event_type else .2
    news_signal = severity * raw_confidence
    probability = (.6 * model_probability + .4 * rule_probability) if model_probability is not None else rule_probability
    timestamp = getattr(event, "timestamp", datetime.now(timezone.utc))
    timestamp = timestamp.replace(tzinfo=timezone.utc) if getattr(timestamp, "tzinfo", None) is None else timestamp.astimezone(timezone.utc)
    recency = max(.3, 1 - max(0, (datetime.now(timezone.utc) - timestamp).total_seconds()) / (30 * 86400))
    conflict = detect_signal_conflict(news_signal, sanctions_signal, historical_signal, model_probability)
    confidence = _clamp(raw_confidence * recency * (.75 if conflict["conflicting_signals"] else 1), .3)
    return {"risk_score_ml": round(probability * 100, 2), "confidence": round(confidence, 3), "disruption_probability": round(probability, 4), "news_signal": round(news_signal, 3), "sanctions_signal": sanctions_signal, "historical_signal": round(historical_signal, 3), "model_signal": model_probability, **conflict}
