"""Download UCI PhiUSIIL, train URL-only models, evaluate by held-out domain, export demo model."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from ucimlrepo import fetch_ucirepo
sys.path.insert(0, str(Path(__file__).parent / "src"))
from urlsentry.features import FEATURES, extract_features


def export_trees(clf):
    exported=[]
    for est in clf.estimators_:
        t=est.tree_
        # Per leaf: P(phishing), class 1 is phishing.
        frac=[]
        for row in t.value[:,0,:]:
            frac.append(float(row[1]/row.sum()) if row.sum() else 0.0)
        exported.append({"left":t.children_left.astype(int).tolist(),"right":t.children_right.astype(int).tolist(),
                         "feature":t.feature.astype(int).tolist(),"thresholds":t.threshold.astype(float).tolist(),
                         "positive_fraction":frac})
    return exported


def main():
    data=fetch_ucirepo(id=967)
    df=data.data.features
    target=data.data.targets["label"].astype(int).to_numpy()
    y=1-target # UCI: 0 phishing, 1 legitimate.
    urls=df["URL"].astype(str).to_numpy()
    groups=df["Domain"].fillna("").astype(str).str.lower().to_numpy()
    X=np.asarray([extract_features(u) for u in urls],dtype=np.float32)
    # Grouped holdout keeps domains disjoint, reducing memorization from repeated domains.
    split=GroupShuffleSplit(n_splits=1,test_size=.20,random_state=2026)
    train_i,test_i=next(split.split(X,y,groups))
    results={}
    candidates={
      "logistic_regression":make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,class_weight="balanced",C=.2,random_state=2026)),
      "random_forest":RandomForestClassifier(n_estimators=120,max_depth=12,min_samples_leaf=5,max_features="sqrt",class_weight="balanced_subsample",n_jobs=-1,random_state=2026),
      "extra_trees":ExtraTreesClassifier(n_estimators=120,max_depth=12,min_samples_leaf=5,max_features="sqrt",class_weight="balanced",n_jobs=-1,random_state=2026),
    }
    for name,clf in candidates.items():
        clf.fit(X[train_i],y[train_i])
        pred=clf.predict_proba(X[test_i])[:,1]
        results[name]={"roc_auc":float(roc_auc_score(y[test_i],pred)),"average_precision":float(average_precision_score(y[test_i],pred)),
          "precision":float(precision_score(y[test_i],pred>=.5)),"recall":float(recall_score(y[test_i],pred>=.5)),
          "f1":float(f1_score(y[test_i],pred>=.5)),"accuracy":float(accuracy_score(y[test_i],pred>=.5))}
        print(name,results[name], flush=True)
    # Use the highest ROC-AUC forest family, exact threshold is deliberately only a demo cutoff.
    selected=max(("random_forest","extra_trees"),key=lambda n: results[n]["roc_auc"])
    clf=candidates[selected]
    artifact={"model":"ExtraTrees" if selected=="extra_trees" else "RandomForest","features":FEATURES,"trees":export_trees(clf),
              "threshold":.5,"seed":2026,"dataset_id":967,"rows":int(len(y)),"train_rows":int(len(train_i)),"test_rows":int(len(test_i)),
              "test_metrics":results[selected],"model_comparison":results,"positive_label":"phishing-pattern",
              "train_domains":int(np.unique(groups[train_i]).size),"test_domains":int(np.unique(groups[test_i]).size),
              "domain_overlap":int(len(set(groups[train_i]).intersection(groups[test_i])))}
    Path("artifacts/model.json").write_text(json.dumps(artifact,separators=(",",":")))
    Path("artifacts/metrics.json").write_text(json.dumps(artifact|{"trees":"omitted from metrics summary"},indent=2))
    print("selected",selected,"model json bytes",Path("artifacts/model.json").stat().st_size,flush=True)

if __name__=="__main__": main()
