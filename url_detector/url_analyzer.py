import re
import sys
from urllib.parse import urlparse

import requests


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
    "tiny.one",
}

SUSPICIOUS_WORDS = {
    "verify",
    "verification",
    "login",
    "signin",
    "account",
    "kyc",
    "update",
    "secure",
    "security",
    "claim",
    "cashback",
    "refund",
    "reward",
    "prize",
    "winner",
    "payment",
    "withdraw",
    "urgent",
    "suspended",
    "deactivate",
}

SUSPICIOUS_TLDS = {
    ".buzz",
    ".click",
    ".top",
    ".xyz",
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
}


def extract_urls(text):
    pattern = (
        r'https?://[^\s<>"\']+'
        r'|(?:https?://)?'
        r'(?:bit\.ly|tinyurl\.com|cutt\.ly|t\.co|goo\.gl|'
        r'ow\.ly|is\.gd|rb\.gy)/[^\s<>"\']+'
    )

    return re.findall(pattern, text, re.IGNORECASE)


def normalize_url(url):
    url = url.rstrip(".,!?;:)]}")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def get_domain(url):
    return urlparse(url).netloc.lower().split(":")[0]


def analyze_domain(url):
    parsed = urlparse(url)
    domain = get_domain(url)

    score = 0
    reasons = []

    combined = (
        domain
        + parsed.path.lower()
        + parsed.query.lower()
    )

    # Shortener
    if domain in SHORTENERS:
        score += 30
        reasons.append("URL shortener")

    # HTTP
    if parsed.scheme == "http":
        score += 10
        reasons.append("No HTTPS")

    # Suspicious keywords
    found = []

    for word in SUSPICIOUS_WORDS:
        if word in combined:
            found.append(word)

    if found:
        score += min(len(found) * 8, 30)
        reasons.append(
            "Suspicious keywords: " + ", ".join(found)
        )

    # IP address
    if re.fullmatch(
        r"\d{1,3}(?:\.\d{1,3}){3}",
        domain
    ):
        score += 35
        reasons.append("IP address used as domain")

    # Punycode
    if "xn--" in domain:
        score += 25
        reasons.append("Punycode domain")

    # Too many subdomains
    if domain.count(".") >= 3:
        score += 15
        reasons.append("Many subdomains")

    # Suspicious TLD
    for tld in SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            score += 20
            reasons.append("Suspicious TLD: " + tld)
            break

    # Long URL
    if len(url) > 150:
        score += 10
        reasons.append("Very long URL")

    return min(score, 100), reasons


def resolve_url(url):
    try:
        session = requests.Session()

        response = session.get(
            url,
            allow_redirects=True,
            timeout=7,
            stream=True,
            headers={
                "User-Agent": "ScamLens-URL-Analyzer/2.0"
            },
        )

        chain = [url]

        for item in response.history:
            location = item.headers.get("Location")

            if location:
                chain.append(location)

        chain.append(response.url)

        # Remove duplicates while preserving order
        clean_chain = []

        for item in chain:
            if item not in clean_chain:
                clean_chain.append(item)

        return {
            "success": True,
            "status": response.status_code,
            "final_url": response.url,
            "chain": clean_chain,
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e),
        }


def analyze_url(url):
    url = normalize_url(url)

    original_score, original_reasons = analyze_domain(url)

    print("\n" + "=" * 60)
    print("ORIGINAL URL")
    print("=" * 60)

    print("URL    :", url)
    print("Domain :", get_domain(url))
    print("Score  :", original_score, "/ 100")

    if original_reasons:
        print("Reasons:")

        for reason in original_reasons:
            print("  -", reason)

    print("\nResolving redirects...")

    resolved = resolve_url(url)

    if not resolved["success"]:
        print("Could not resolve URL:")
        print(resolved["error"])
        return

    chain = resolved["chain"]

    print("\nREDIRECT CHAIN")
    print("=" * 60)

    for i, item in enumerate(chain):
        print(f"{i}: {item}")

    print("\nRedirect count:", len(chain) - 1)
    print("HTTP status  :", resolved["status"])

    final_url = resolved["final_url"]

    print("\nFINAL DESTINATION")
    print("=" * 60)

    print("URL    :", final_url)
    print("Domain :", get_domain(final_url))

    final_score, final_reasons = analyze_domain(final_url)

    print("Score  :", final_score, "/ 100")

    if final_reasons:
        print("Reasons:")

        for reason in final_reasons:
            print("  -", reason)

    # Cross-domain redirect
    original_domain = get_domain(url)
    final_domain = get_domain(final_url)

    if original_domain != final_domain:
        print("\nWARNING: DOMAIN CHANGED")
        print(
            f"{original_domain} -> {final_domain}"
        )

        final_score = min(final_score + 15, 100)

    # Redirects themselves are useful evidence,
    # but don't automatically mean scam.
    if len(chain) > 2:
        final_score = min(final_score + 5, 100)

    if final_score >= 70:
        risk = "HIGH"
    elif final_score >= 40:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    print("\n" + "=" * 60)
    print("FINAL URL RISK")
    print("=" * 60)

    print("Score :", final_score, "/ 100")
    print("Risk  :", risk)


def analyze_message(text):
    urls = extract_urls(text)

    if not urls:
        print("No URLs detected.")
        return

    print(f"\nURLs detected: {len(urls)}")

    for url in urls:
        analyze_url(url)


if __name__ == "__main__":

    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        analyze_message(message)

    else:
        print("========== SCAMLENS URL ANALYZER V2 ==========")
        print("Paste an SMS and press Enter.")
        print("Type 'exit' to quit.\n")

        while True:
            try:
                text = input("SMS: ")

                if text.strip().lower() == "exit":
                    break

                if not text.strip():
                    print("Please enter an SMS.")
                    continue

                analyze_message(text)

            except KeyboardInterrupt:
                print("\nExiting.")
                break
