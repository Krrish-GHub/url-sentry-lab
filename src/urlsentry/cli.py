from __future__ import annotations
import argparse
from .model import score_url


def main() -> None:
    parser = argparse.ArgumentParser(description="Score URL structure locally; does not visit the URL.")
    parser.add_argument("url")
    args = parser.parse_args()
    result = score_url(args.url)
    print(f"Model output: {result['label']} ({result['risk']:.1%} phishing-pattern score)")
    print("This is an educational model output, not a safety verdict.")

if __name__ == "__main__":
    main()
