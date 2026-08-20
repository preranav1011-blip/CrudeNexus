"""Training and persistence for the corridor-disruption model."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import logging
from pathlib import Path
import pickle
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from app.ml.feature_engineering import FEATURE_NAMES

logger = logging.getLogger(__name__)
MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "disruption_predictor.pkl"
LABEL_COLUMN = "disruption_label"


def build_training_dataset(samples: int = 800, random_state: int = 42) -> pd.DataFrame:
    """Create a reproducible labelled prototype dataset until public history is added."""
    if samples < 100:
        raise ValueError("samples must be at least 100")
    rng, risk = np.random.default_rng(random_state), None
    risk = rng.choice([25, 42, 48, 60, 65], samples)
    data = pd.DataFrame({
        "event_count_7d": rng.poisson(1.5, samples), "event_count_14d": rng.poisson(2.5, samples), "event_count_30d": rng.poisson(4.5, samples),
        "severity_mean": rng.uniform(0, 1, samples), "severity_max": rng.uniform(0, 1, samples), "india_relevance_mean": rng.uniform(.2, 1, samples),
        "confidence_mean": rng.uniform(.35, 1, samples), "conflict_event_ratio": rng.uniform(0, 1, samples), "sanctions_event_ratio": rng.uniform(0, 1, samples),
        "port_disruption_ratio": rng.uniform(0, 1, samples), "days_since_latest_event": rng.uniform(0, 30, samples), "baseline_risk_score": risk,
        "baseline_disruption_probability": risk / 500, "india_import_percentage": rng.uniform(5, 60, samples), "affected_route_count": rng.integers(1, 6, samples),
        "affected_supplier_count": rng.integers(1, 7, samples), "sanctions_exposure_mean": rng.uniform(.1, .95, samples), "oil_price_usd": rng.normal(85, 8, samples),
        "oil_price_volatility": rng.uniform(.02, .25, samples), "shipping_delay_index": rng.uniform(0, 1, samples), "historical_disruption_frequency": risk / 100,
    })
    odds = -4.3 + 2.1 * data.severity_max + 1.4 * data.conflict_event_ratio + 1.1 * data.shipping_delay_index + .8 * data.sanctions_exposure_mean + data.historical_disruption_frequency + .05 * data.event_count_7d - .035 * data.days_since_latest_event + rng.normal(0, .55, samples)
    data[LABEL_COLUMN] = rng.binomial(1, 1 / (1 + np.exp(-odds)))
    return data


def _load_dataset(data_file: Optional[str]) -> pd.DataFrame:
    data = build_training_dataset() if data_file is None else pd.read_csv(data_file)
    missing = set(FEATURE_NAMES + [LABEL_COLUMN]) - set(data.columns)
    if missing:
        raise ValueError(f"Training data is missing columns: {', '.join(sorted(missing))}")
    return data[FEATURE_NAMES + [LABEL_COLUMN]].copy()


def train_model(data_file: Optional[str] = None, output_path: Optional[str] = None) -> dict:
    """Train XGBoost and persist the model, schema, and evaluation metadata."""
    data = _load_dataset(data_file)
    X, y = data[FEATURE_NAMES], data[LABEL_COLUMN].astype(int)
    if y.nunique() < 2:
        raise ValueError("Training labels must contain both disruption classes")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)
    model = XGBClassifier(n_estimators=120, max_depth=3, learning_rate=.06, subsample=.9, colsample_bytree=.9, eval_metric="logloss", random_state=42, n_jobs=1)
    model.fit(X_train, y_train)
    auc = float(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
    artifact = {"model": model, "feature_names": FEATURE_NAMES, "feature_medians": X.median().to_dict(), "trained_at": datetime.now(timezone.utc).isoformat(), "training_rows": len(data), "validation_auc": auc, "data_source": data_file or "synthetic_prototype"}
    path = Path(output_path) if output_path else MODEL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as file:
        pickle.dump(artifact, file)
    logger.info("Trained disruption predictor with %d rows (validation AUC %.3f)", len(data), auc)
    return {"model_path": str(path), "training_rows": len(data), "validation_auc": auc, "feature_count": len(FEATURE_NAMES), "data_source": artifact["data_source"]}


def retrain_model(new_disruption_data: Optional[str] = None) -> dict:
    return train_model(data_file=new_disruption_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CrudeNexus disruption model")
    parser.add_argument("--data-file"), parser.add_argument("--output-path")
    args = parser.parse_args()
    print(train_model(args.data_file, args.output_path))
