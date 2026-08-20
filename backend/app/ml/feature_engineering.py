"""Deterministic feature engineering for corridor-disruption prediction."""
from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Iterable, Optional

from app.data.csv_loaders import CorridorLoader
from app.data.mock_sources import get_mock_sanctions_exposure

logger = logging.getLogger(__name__)

FEATURE_NAMES = [
    "event_count_7d", "event_count_14d", "event_count_30d", "severity_mean",
    "severity_max", "india_relevance_mean", "confidence_mean", "conflict_event_ratio",
    "sanctions_event_ratio", "port_disruption_ratio", "days_since_latest_event",
    "baseline_risk_score", "baseline_disruption_probability", "india_import_percentage",
    "affected_route_count", "affected_supplier_count", "sanctions_exposure_mean",
    "oil_price_usd", "oil_price_volatility", "shipping_delay_index",
    "historical_disruption_frequency",
]


def _value(event: Any, name: str, default: Any = None) -> Any:
    return event.get(name, default) if isinstance(event, dict) else getattr(event, name, default)


def _timestamp(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError:
            return None
    return None


def _corridor_details(corridor: str) -> dict[str, Any]:
    normalized = corridor.strip().lower()
    return next((item for item in CorridorLoader.load_corridors()
                 if item.get("corridor_name", "").strip().lower() == normalized), {})


def engineer_features(events: Iterable[Any], corridor: str, lookback_days: int = 30,
                      as_of: Optional[datetime] = None) -> dict[str, float]:
    """Build a stable, model-ready feature vector for a maritime corridor.

    Inputs can be ORM events or dictionaries. Missing live signals use neutral,
    documented prototype values, keeping inference available without external feeds.
    """
    if lookback_days <= 0:
        raise ValueError("lookback_days must be positive")
    now = as_of or datetime.now(timezone.utc)
    now = now.replace(tzinfo=timezone.utc) if now.tzinfo is None else now.astimezone(timezone.utc)
    normalized, details = corridor.strip().lower(), _corridor_details(corridor)
    relevant = []
    for event in events:
        occurred_at = _timestamp(_value(event, "timestamp"))
        event_corridor = str(_value(event, "affected_corridor", "")).strip().lower()
        if event_corridor == normalized and occurred_at and 0 <= (now - occurred_at).days <= lookback_days:
            relevant.append((event, occurred_at))

    def count(days: int) -> int:
        return sum(1 for _, at in relevant if (now - at).total_seconds() <= days * 86400)

    severity = [float(_value(e, "severity_raw", 0.5) or 0.5) for e, _ in relevant]
    relevance = [float(_value(e, "india_relevance", 0.5) or 0.5) for e, _ in relevant]
    confidence = [float(_value(e, "raw_confidence", _value(e, "confidence", 0.5)) or 0.5) for e, _ in relevant]
    event_types = [str(_value(e, "event_type", "")).lower() for e, _ in relevant]
    latest_days = min(((now - at).total_seconds() / 86400 for _, at in relevant), default=float(lookback_days))
    suppliers = details.get("affected_suppliers", [])
    sanctions = [get_mock_sanctions_exposure(s).get("sanctions_risk_score", 50) / 100 for s in suppliers]
    baseline_risk = float(details.get("baseline_risk_score", 35))
    features = {
        "event_count_7d": count(7), "event_count_14d": count(14), "event_count_30d": count(30),
        "severity_mean": sum(severity) / len(severity) if severity else 0, "severity_max": max(severity, default=0),
        "india_relevance_mean": sum(relevance) / len(relevance) if relevance else 0,
        "confidence_mean": sum(confidence) / len(confidence) if confidence else 0,
        "conflict_event_ratio": sum("tension" in t or "blockade" in t for t in event_types) / len(event_types) if event_types else 0,
        "sanctions_event_ratio": sum("sanction" in t for t in event_types) / len(event_types) if event_types else 0,
        "port_disruption_ratio": sum("port" in t or "shipping" in t for t in event_types) / len(event_types) if event_types else 0,
        "days_since_latest_event": min(latest_days, float(lookback_days)), "baseline_risk_score": baseline_risk,
        "baseline_disruption_probability": float(details.get("estimated_current_disruption_probability", 0.05)),
        "india_import_percentage": float(details.get("india_import_percentage", 0)),
        "affected_route_count": len(details.get("affected_routes", [])), "affected_supplier_count": len(suppliers),
        "sanctions_exposure_mean": sum(sanctions) / len(sanctions) if sanctions else 0.5,
        "oil_price_usd": 85, "oil_price_volatility": 0.08,
        "shipping_delay_index": min(1, max(severity, default=0) * 0.6 + count(7) * 0.08),
        "historical_disruption_frequency": baseline_risk / 100,
    }
    return {name: float(features[name]) for name in FEATURE_NAMES}
