# URL Sentry Lab

A compact, practical machine-learning security project: train and inspect a URL-only phishing-pattern classifier, run it locally, or try the same exported decision-tree model in a static browser demo.

- Live demo: https://krrish-ghub.github.io/url-sentry-lab/
- Repository: https://github.com/Krrish-GHub/url-sentry-lab
- The browser demo is static: it does not call a scoring API, visit submitted links, or transmit the input URL.

## Why publish this?

Phishing detection is a concrete model task that connects classification, feature engineering, model comparison, evaluation design, model export, and a small client-side inference runtime. The demo makes one boundary visible: a URL-shape model can only recognize patterns represented in its training data; it cannot establish that a site is legitimate or safe.

## What the project does

`train.py` fetches the public UCI PhiUSIIL dataset, extracts 18 lightweight features from each raw URL only, and compares logistic regression, random forest, and extra trees. It holds out entire domains with a fixed-seed grouped split, so domains in the test fold are excluded from training. The best of the two tree ensembles by test ROC-AUC is exported as `artifacts/model.json` for the Python CLI and the browser demo.

The experiment intentionally does **not** use HTML, page content, labels inferred from the hostname, or target-lookups as inference features. It never opens submitted URLs. The browser score is the forest’s mean leaf score, not a calibrated probability, reputation lookup, browser warning, or verdict.

## Current experiment

Reproduce with seed `2026`; the checked-in `artifacts/metrics.json` records the exact run. Holdout is a single 80/20 `GroupShuffleSplit`, grouped on the dataset's `Domain` value. The fixed classification threshold for the reported precision/recall/F1 is 0.50.

| Model | ROC-AUC | Average precision | Precision | Recall | F1 | Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Logistic regression | 0.9945 | 0.9956 | 0.9846 | 0.9747 | 0.9796 | 0.9821 |
| Random forest | 0.9970 | 0.9976 | 0.9931 | 0.9694 | 0.9811 | 0.9835 |
| Extra trees | 0.9895 | 0.9896 | 0.9859 | 0.9020 | 0.9421 | 0.9511 |

All 235,795 rows were retained: 187,562 training and 48,233 test examples, with disjoint `Domain` groups. These are results on this particular historical, curated dataset and split. They should not be interpreted as current real-world detection performance: labels, collection choices, repeated patterns, class mix and threat tactics can differ in deployment. High offline scores do not establish safe-link coverage. The dataset contains both URLs and corresponding webpages; this project uses URL strings and labels only, and makes no claim about browsing safety.

## Run locally

Requires Python 3.11+ and Node 20+ only for the cross-language parity test. Training fetches the dataset from UCI; ordinary tests use the checked-in model and no dataset download.

```bash
uv sync --group dev
uv run pytest -q
uv run url-sentry https://example.com/account
uv run python train.py  # downloads/retrains from UCI; overwrites model artifacts
uv run python -m http.server 8000 --directory site
```

Then open `http://localhost:8000`. To run the demo after retraining, copy the newly exported artifact with `cp artifacts/model.json site/artifacts/model.json` first. Do not commit the downloaded raw dataset.

## Dataset and attribution

Prasad, A. & Chandra, S. (2024). [PhiUSIIL Phishing URL (Website)](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+website), UCI Machine Learning Repository. DOI: [10.1016/j.cose.2023.103545](https://doi.org/10.1016/j.cose.2023.103545). Licensed CC BY 4.0. UCI documents 235,795 examples (134,850 legitimate, 100,945 phishing); UCI label 1 means legitimate and label 0 means phishing. The trainer maps label 0 to the positive phishing-pattern class. Dataset construction was donated in March 2024; its authors note most URLs analyzed were the latest at the time of construction, which does not make this a live or continually refreshed source.

## Privacy and safe use

The web demo scores the typed string locally after static assets load. Its JavaScript contains no code to send that string anywhere or fetch the destination. This repository is an educational experiment; do not rely on it to make security decisions. Never enter passwords through an unknown link. Visit a service through its known address or official app instead.
