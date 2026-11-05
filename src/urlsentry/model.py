"""Model I/O and safe inference."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from .features import FEATURES, extract_features

DEFAULT_MODEL = Path(__file__).resolve().parents[2] / "artifacts" / "model.json"


def score_url(url: str, model_path: Path = DEFAULT_MODEL) -> dict:
    model = json.loads(Path(model_path).read_text())
    x = np.asarray(extract_features(url), dtype=float)
    nodes = model["trees"]
    probabilities = [tree_probability(tree, x) for tree in nodes]
    risk = float(np.mean(probabilities))
    return {"risk": risk, "label": "higher-risk pattern" if risk >= model["threshold"] else "lower-risk pattern",
            "features": dict(zip(FEATURES, x.tolist()))}


def tree_probability(tree: dict, x: np.ndarray) -> float:
    i = 0
    while tree["left"][i] != -1:
        i = tree["left"][i] if x[tree["feature"][i]] <= tree["thresholds"][i] else tree["right"][i]
    counts = tree["positive_fraction"][i]
    return float(counts)
