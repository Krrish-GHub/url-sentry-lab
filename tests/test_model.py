import json
from pathlib import Path
from urlsentry.model import score_url, tree_probability
import numpy as np


def test_exported_model_is_loadable_and_deterministic():
    a = score_url("https://accounts.example.com/signin")
    b = score_url("https://accounts.example.com/signin")
    assert a == b
    assert 0 <= a["risk"] <= 1
    assert len(a["features"]) == 18


def test_export_has_evaluation_and_nonempty_forest():
    data = json.loads((Path(__file__).parents[1] / "artifacts/model.json").read_text())
    assert data["test_rows"] > 1000
    assert data["trees"]
    assert data["test_metrics"]["roc_auc"] > .5
