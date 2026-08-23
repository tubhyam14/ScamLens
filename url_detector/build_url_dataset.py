import pandas as pd
from urllib.parse import urlparse
from pathlib import Path

OUT = Path("data/url_dataset_v1.csv")


def features(url):
    p = urlparse(url)

    host = p.netloc.lower()
    path = p.path
    query = p.query

    return {
        "url": url,
        "url_len": len(url),
        "domain_len": len(host),
        "path_len": len(path),
        "query_len": len(query),
        "dots": url.count("."),
        "hyphens": url.count("-"),
        "digits": sum(c.isdigit() for c in url),
        "special": sum(not c.isalnum() for c in url),
        "slashes": url.count("/"),
        "subdomains": max(host.count(".") - 1, 0),
        "https": int(p.scheme == "https"),
        "has_ip": int(host.replace(".", "").isdigit()),
        "has_at": int("@" in url),
        "has_question": int("?" in url),
        "has_equals": int("=" in url),
        "has_percent": int("%" in url),
        "has_shortener": int(
            any(x in host for x in [
                "bit.ly",
                "tinyurl.com",
                "t.co",
                "goo.gl",
                "ow.ly",
                "is.gd",
                "cutt.ly",
                "rb.gy"
            ])
        ),
    }


# Temporary seed data.
# We will replace this with real datasets next.
legitimate = [
    "https://www.google.com/",
    "https://www.amazon.in/",
    "https://www.microsoft.com/",
    "https://www.apple.com/",
    "https://www.airtel.in/",
    "https://www.hdfcbank.com/",
    "https://www.icicibank.com/",
    "https://www.sbi.co.in/",
    "https://www.flipkart.com/",
    "https://www.wikipedia.org/",
]

malicious = [
    "http://verify-account-login.com/secure",
    "http://bank-account-verification.com/login",
    "http://claim-prize-now.com/winner",
    "http://free-cashback-offer.com/claim",
    "http://kyc-update-account.com/verify",
    "http://urgent-bank-login.com/security",
    "http://account-suspended-verify.com/login",
    "http://parcel-customs-payment.com/pay",
    "http://lottery-winner-claim.com/prize",
    "http://upi-cashback-claim.com/verify",
]


rows = []

for url in legitimate:
    row = features(url)
    row["label"] = 0
    rows.append(row)

for url in malicious:
    row = features(url)
    row["label"] = 1
    rows.append(row)


df = pd.DataFrame(rows)

OUT.parent.mkdir(exist_ok=True)

df.to_csv(OUT, index=False)

print("========== URL DATASET ==========")
print("Total:", len(df))
print()
print(df["label"].value_counts())
print()
print("Saved:", OUT)
