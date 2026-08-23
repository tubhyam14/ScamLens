import pandas as pd
from pathlib import Path
from urllib.parse import urlparse

from url_features import extract_features


MALICIOUS = Path("data/url_dataset_v2.csv")
TRANCO_DIR = Path("data/url_raw/tranco")
OUTPUT = Path("data/url_dataset_v3.csv")

N = 16000


# ==============================
# LOAD MALICIOUS
# ==============================

mal = pd.read_csv(MALICIOUS)

mal = mal.drop_duplicates("url")

mal = mal.sample(
    n=min(N, len(mal)),
    random_state=42
)

mal["label"] = 1
mal["source"] = "urlhaus"


# ==============================
# FIND TRANCO CSV
# ==============================

files = list(TRANCO_DIR.glob("*.csv"))

if not files:
    raise FileNotFoundError(
        "Tranco CSV not found"
    )

tranco = pd.read_csv(
    files[0],
    header=None,
    names=["rank", "domain"]
)

tranco = tranco.dropna()

tranco["domain"] = (
    tranco["domain"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# ==============================
# CREATE LEGITIMATE URLS
# ==============================

legit_rows = []

for domain in tranco["domain"]:

    if len(legit_rows) >= N:
        break

    url = "https://" + domain + "/"

    try:

        row = extract_features(url)

        row["url"] = url
        row["label"] = 0
        row["source"] = "tranco"

        legit_rows.append(row)

    except Exception:
        continue


legit = pd.DataFrame(legit_rows)


# ==============================
# COMBINE
# ==============================

df = pd.concat(
    [mal, legit],
    ignore_index=True
)

df = df.drop_duplicates("url")

df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ==============================
# SAVE
# ==============================

OUTPUT.parent.mkdir(exist_ok=True)

df.to_csv(
    OUTPUT,
    index=False
)


print("=" * 60)
print("SCAMLENS URL DATASET V3")
print("=" * 60)

print("Total :", len(df))

print("\nDistribution:")
print(df["label"].value_counts())

print("\nSources:")
print(df["source"].value_counts())

print("\nSaved:")
print(OUTPUT)

