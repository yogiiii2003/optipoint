from __future__ import annotations

import pickle
from pathlib import Path
from typing import Optional

import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"

_bundle: Optional[dict] = None


def _load() -> dict:
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(
                f"Model not found at {MODEL_PATH}. Run `python -m app.ml.train` first."
            )
        with MODEL_PATH.open("rb") as f:
            _bundle = pickle.load(f)
    return _bundle


def classify(distances_km: dict[str, float]) -> tuple[str, float]:
    bundle = _load()
    feature_order: list[str] = bundle["feature_order"]
    row = {col: distances_km.get(col.replace("Nearest_", "").replace("_Distance", ""), 100000.0)
           for col in feature_order}
    df = pd.DataFrame([row], columns=feature_order)

    pipeline = bundle["pipeline"]
    pred = pipeline.predict(df)[0]
    proba = pipeline.predict_proba(df)[0].max() if hasattr(pipeline, "predict_proba") else None

    verdict = "Optimal" if pred == 0 else "Not Optimal"
    return verdict, float(proba) if proba is not None else 0.0
