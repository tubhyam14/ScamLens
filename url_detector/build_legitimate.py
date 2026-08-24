import pandas as pd
from pathlib import Path

from url_features import extract_features


TRANCO = Path("data/url_raw/tranco/top-1m.csv")
MALICIOUS = Path("data/url_dataset_v2.csv")
OUTPUT = Path("data/url_legitimate_v1.csv")


# Match malicious dataset size
N = len(pd.read_csv(MALICIOUS))


tranco = pd.read_csv(
    TRANCO,
    header=None,
    names=["rank", "domain"],
    nrows=N
)

rows = []

for domain in tranco["domain"]:

    domain = str(domain).strip().lower()

    if not domain:
        continue

    url = "https://" + domain + "/"

    try:
        features = extract_features(url)

        features["url"] = url
        features["label"] = 0
        features["source"] = "tranco"

        rows.append(features)

    except Exception:
        continue


df = pd.DataFrame(rows)

df = df.drop_duplicates(
    subset=["url"]
)

df.to_csv(
    OUTPUT,
    index=False
)


print("=" * 60)
print("LEGITIMATE URL DATASET")
print("=" * 60)

print("URLs:", len(df))
print("Label distribution:")
print(df["label"].value_counts())

print("\nFirst URLs:")
print(df[["url", "label", "source"]].head())

print("\nSaved:", OUTPUT)
