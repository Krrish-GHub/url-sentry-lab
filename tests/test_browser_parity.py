import json
import subprocess
from pathlib import Path
from urlsentry.features import extract_features

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    "https://accounts.google.com/signin",
    "http://192.0.2.1:8080/login?x=1",
    "example.co.uk/path/a?verify=1",
    "https://user@example.org:443/a%20b",
]


def test_browser_and_python_feature_vectors_match():
    script = "const f=require('./site/features.js').featuresFor; console.log(JSON.stringify(process.argv.slice(1).map(f)))"
    actual = json.loads(subprocess.check_output(["node", "-e", script, *CASES], cwd=ROOT, text=True))
    expected = [extract_features(s) for s in CASES]
    for got, want in zip(actual, expected):
        assert len(got) == len(want)
        assert all(abs(float(a) - float(b)) < 1e-10 for a, b in zip(got, want))
