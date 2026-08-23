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


def extract_urls(text):
    pattern = r'https?://[^\s<>"\']+|(?:https?://)?(?:bit\.ly|tinyurl\.com|cutt\.ly|t\.co|goo\.gl|ow\.ly|is\.gd|rb\.gy)/[^\s<>"\']+'
    return re.findall(pattern, text, re.IGNORECASE)


def normalize_url(url):
    url = url.rstrip(".,!?;:)]}")
    
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def analyze_url(url):
    url = normalize_url(url)

    parsed = urlparse(url)
    domain = parsed.netloc.lower().split(":")[0]
    path = parsed.path.lower()

    score = 0
    reasons = []

    # Shortened URL
    if domain in SHORTENERS:
        score += 30
        reasons.append("URL shortener")

    # HTTP instead of HTTPS
    if parsed.scheme == "http":
        score += 10
        reasons.append("No HTTPS")

    # Suspicious words
    found_words = []

    combined = (domain + path + parsed.query).lower()

    for word in SUSPICIOUS_WORDS:
        if word in combined:
            found_words.append(word)

    if found_words:
        score += min(len(found_words) * 8, 30)
        reasons.append(
            "Suspicious keywords: " + ", ".join(found_words)
        )

    # IP address instead of domain
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", domain):
        score += 35
        reasons.append("IP address used as domain")

    # Excessive subdomains
    if domain.count(".") >= 3:
        score += 15
        reasons.append("Many subdomains")

    # Punycode
    if "xn--" in domain:
        score += 25
        reasons.append("Punycode domain")

    # Long URL
    if len(url) > 150:
        score += 10
        reasons.append("Very long URL")

    score = min(score, 100)

    if score >= 70:
        risk = "HIGH"
    elif score >= 40:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "url": url,
        "domain": domain,
        "score": score,
        "risk": risk,
        "reasons": reasons,
    }


def resolve_url(url):
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=5,
            headers={
                "User-Agent": "ScamLens-URL-Analyzer/1.0"
            },
        )

        return {
            "final_url": response.url,
            "status": response.status_code,
            "redirected": response.url != url,
        }

    except requests.RequestException as e:
        return {
            "error": str(e)
        }


def analyze_message(text):
    urls = extract_urls(text)

    if not urls:
        print("No URLs detected.")
        return

    print(f"URLs detected: {len(urls)}")

    for i, raw_url in enumerate(urls, 1):
        print("\n" + "=" * 55)
        print(f"URL #{i}")

        result = analyze_url(raw_url)

        print("URL     :", result["url"])
        print("Domain  :", result["domain"])
        print("Score   :", result["score"], "/ 100")
        print("Risk    :", result["risk"])

        if result["reasons"]:
            print("Reasons :")
            for reason in result["reasons"]:
                print("  -", reason)

        print("\nChecking redirects...")

        resolved = resolve_url(result["url"])

        if "error" in resolved:
            print("Redirect check failed:", resolved["error"])
        else:
            print("HTTP status :", resolved["status"])
            print("Final URL   :", resolved["final_url"])

            if resolved["redirected"]:
                print("WARNING     : URL redirects elsewhere")


if __name__ == "__main__":

    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        analyze_message(message)

    else:
        print("========== SCAMLENS URL ANALYZER ==========")
        print("Paste an SMS and press Enter.")
        print("Type 'exit' to quit.\n")

        while True:
            text = input("SMS: ")

            if text.lower() == "exit":
                break

            analyze_message(text)
