"""Inference and lightweight explanation for the persisted disruption model."""
from __future__ import annotations

import logging
from pathlib import Path
import pickle
from typing import Dict

import pandas as pd
from app.ml.feature_engineering import FEATURE_NAMES
from app.ml.training import MODEL_PATH

logger = logging.getLogger(__name__)
_artifact = None


def _load_artifact():
    global _artifact
    if _artifact is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model is not trained. Run `python -m app.ml.training` first: {MODEL_PATH}")
        with MODEL_PATH.open("rb") as file:
            _artifact = pickle.load(file)
    return _artifact


def predict_disruption(corridor: str, features: Dict[str, float]) -> Dict:
    """Predict 7-day disruption probability and report strongest feature effects."""
    artifact = _load_artifact()
    missing = [name for name in artifact["feature_names"] if name not in features]
    if missing:
        raise ValueError(f"Missing inference features: {', '.join(missing)}")
    row = pd.DataFrame([{name: float(features[name]) for name in artifact["feature_names"]}])
    probability = float(artifact["model"].predict_proba(row)[0, 1])
    effects = {name: abs(float(row.iloc[0][name]) - float(artifact["feature_medians"][name])) * float(weight) for name, weight in zip(artifact["feature_names"], artifact["model"].feature_importances_)}
    contributors = dict(sorted(effects.items(), key=lambda item: item[1], reverse=True)[:5])
    confidence = min(.95, .55 + (artifact["validation_auc"] - .5) * .7 + min(.15, len(contributors) * .02))
    return {"corridor": corridor, "disruption_probability": probability, "confidence": max(.3, confidence), "contributing_features": contributors, "model_trained_at": artifact["trained_at"]}


def get_model_info() -> Dict:
    """Return model availability and metadata without forcing model training."""
    if not MODEL_PATH.exists():
        return {"status": "not_trained", "model_file": str(MODEL_PATH), "feature_count": len(FEATURE_NAMES)}
    artifact = _load_artifact()
    return {"status": "loaded", "model_file": str(MODEL_PATH), "feature_count": len(artifact["feature_names"]), "training_rows": artifact["training_rows"], "validation_auc": artifact["validation_auc"], "trained_at": artifact["trained_at"], "data_source": artifact["data_source"]}
