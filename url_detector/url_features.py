from urllib.parse import urlparse
import math
import re


SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "cutt.ly",
    "rb.gy",
    "shorturl.at",
}

SUSPICIOUS_WORDS = {
    "login",
    "signin",
    "verify",
    "verification",
    "account",
    "secure",
    "security",
    "update",
    "kyc",
    "otp",
    "password",
    "bank",
    "wallet",
    "payment",
    "refund",
    "cashback",
    "reward",
    "prize",
    "winner",
    "claim",
    "urgent",
    "suspended",
    "blocked",
    "confirm",
}


def entropy(text):
    if not text:
        return 0.0

    counts = {}

    for c in text:
        counts[c] = counts.get(c, 0) + 1

    total = len(text)

    return -sum(
        (n / total) * math.log2(n / total)
        for n in counts.values()
    )


def extract_features(url):

    p = urlparse(url)

    host = p.hostname or ""
    path = p.path or ""
    query = p.query or ""

    host = host.lower()

    full = url.lower()

    suspicious_count = sum(
        word in full
        for word in SUSPICIOUS_WORDS
    )

    digits = sum(c.isdigit() for c in url)

    special = sum(
        not c.isalnum()
        for c in url
    )

    return {

        # Basic
        "url_len": len(url),
        "domain_len": len(host),
        "path_len": len(path),
        "query_len": len(query),

        # Structure
        "dots": url.count("."),
        "hyphens": url.count("-"),
        "slashes": url.count("/"),
        "digits": digits,
        "special_chars": special,

        # Domain
        "subdomains": max(host.count(".") - 1, 0),
        "domain_entropy": entropy(host),

        # URL tricks
        "has_ip": int(
            bool(re.fullmatch(
                r"\d{1,3}(\.\d{1,3}){3}",
                host
            ))
        ),

        "has_at": int("@" in url),
        "has_percent": int("%" in url),
        "has_question": int("?" in url),
        "has_equals": int("=" in url),
        "has_ampersand": int("&" in url),

        # Protocol
        "https": int(p.scheme == "https"),

        # Shorteners
        "is_shortener": int(
            host in SHORTENERS
        ),

        # Suspicious language
        "suspicious_words": suspicious_count,

        # Numeric ratios
        "digit_ratio": digits / max(len(url), 1),

        "special_ratio": (
            special / max(len(url), 1)
        ),
    }
