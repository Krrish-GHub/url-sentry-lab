"""Safe, URL-only feature extraction shared with the browser demo."""
from __future__ import annotations
import ipaddress
import re
from urllib.parse import urlsplit

FEATURES = [
    "url_length", "hostname_length", "path_length", "query_length",
    "dot_count", "subdomain_count", "hyphen_count", "at_count",
    "digit_ratio", "letter_ratio", "special_ratio", "has_ip_host",
    "https_scheme", "https_in_text", "suspicious_token_count",
    "encoded_char_count", "double_slash_path", "port_present",
]
_TOKENS = re.compile(r"(?:login|verify|account|secure|update|bank|signin|confirm|password|wallet)", re.I)


def extract_features(value: str) -> list[float]:
    """Extract fixed-order lexical features; never resolves DNS or fetches the URL."""
    raw = value.strip()
    candidate = raw if "://" in raw else "http://" + raw
    try:
        parts = urlsplit(candidate)
        host = (parts.hostname or "").lower().rstrip(".")
        path = parts.path or "/"
        query = parts.query
        authority = parts.netloc.rsplit("@", 1)[-1]
        port_present = bool(re.search(r"\]:\d+$", authority) if authority.startswith("[") else re.search(r":\d+$", authority))
    except ValueError:
        host, path, query, port_present = "", "/", "", False
    total = max(len(raw), 1)
    alnum = sum(ch.isascii() and ch.isalnum() for ch in raw)
    digits = sum(ch.isascii() and ch.isdigit() for ch in raw)
    letters = sum(ch.isascii() and ch.isalpha() for ch in raw)
    special = sum(not ch.isalnum() for ch in raw)
    try:
        ipaddress.ip_address(host.strip("[]"))
        is_ip = 1.0
    except ValueError:
        is_ip = 0.0
    labels = [part for part in host.split(".") if part]
    return [
        float(len(raw)), float(len(host)), float(len(path)), float(len(query)),
        float(host.count(".")), float(max(0, len(labels) - 2)),
        float(raw.count("-")), float(raw.count("@")),
        digits / total, letters / total, special / total, is_ip,
        float(parts.scheme.lower() == "https"), float("https" in raw.lower()),
        float(len(_TOKENS.findall(raw))), float(raw.lower().count("%")),
        float("//" in path[1:]), float(port_present),
    ]
