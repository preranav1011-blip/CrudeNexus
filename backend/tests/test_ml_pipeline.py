from datetime import datetime, timedelta, timezone

from app.ml.feature_engineering import FEATURE_NAMES, engineer_features
from app.ml import inference
from app.ml.training import build_training_dataset, train_model


def test_features_are_stable_and_corridor_specific():
    now = datetime(2026, 8, 20, tzinfo=timezone.utc)
    features = engineer_features([
        {"timestamp": (now - timedelta(days=2)).isoformat(), "affected_corridor": "Hormuz",
         "event_type": "geopolitical_tension", "severity_raw": .8, "india_relevance": .9, "raw_confidence": .8},
        {"timestamp": (now - timedelta(days=1)).isoformat(), "affected_corridor": "Suez",
         "event_type": "port_disruption", "severity_raw": .7},
    ], "Hormuz", as_of=now)
    assert list(features) == FEATURE_NAMES
    assert features["event_count_7d"] == 1
    assert features["baseline_risk_score"] == 65
    assert features["affected_supplier_count"] == 6


def test_synthetic_dataset_has_schema_and_two_classes():
    dataset = build_training_dataset(samples=200)
    assert set(FEATURE_NAMES).issubset(dataset.columns)
    assert set(dataset["disruption_label"].unique()) == {0, 1}


def test_training_and_inference_round_trip(tmp_path, monkeypatch):
    path = tmp_path / "predictor.pkl"
    result = train_model(output_path=str(path))
    assert path.exists()
    assert result["feature_count"] == len(FEATURE_NAMES)
    monkeypatch.setattr(inference, "MODEL_PATH", path)
    monkeypatch.setattr(inference, "_artifact", None)
    features = engineer_features([], "Hormuz", as_of=datetime(2026, 8, 20, tzinfo=timezone.utc))
    prediction = inference.predict_disruption("Hormuz", features)
    assert 0 <= prediction["disruption_probability"] <= 1
    assert 0 <= prediction["confidence"] <= 1
    assert prediction["contributing_features"]
