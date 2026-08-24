import csv
from pathlib import Path

import pandas as pd

from url_features import extract_features


INPUT = Path("data/url_raw/urlhaus_recent.csv")
OUTPUT = Path("data/url_dataset_v2.csv")

rows = []

with INPUT.open(
    "r",
    encoding="utf-8",
    errors="ignore",
    newline=""
) as f:

    reader = csv.reader(f)

    for row in reader:

        # Skip comments
        if not row or row[0].startswith("#"):
            continue

        # URLhaus URL is column 3
        if len(row) < 3:
            continue

        url = row[2].strip()

        if not (
            url.startswith("http://")
            or url.startswith("https://")
        ):
            continue

        try:
            features = extract_features(url)

            # Make absolutely sure URL is retained
            features["url"] = url
            features["label"] = 1
            features["source"] = "urlhaus"

            rows.append(features)

        except Exception:
            continue


print("Rows collected:", len(rows))

if not rows:
    raise RuntimeError(
        "No URLs were extracted from URLhaus feed."
    )


df = pd.DataFrame(rows)

df = df.drop_duplicates(
    subset=["url"]
)

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT,
    index=False
)


print("=" * 60)
print("URLHAUS IMPORT")
print("=" * 60)

print("URLs imported :", len(df))
print("Malicious     :", int((df["label"] == 1).sum()))

print("\nFirst URLs:")

print(
    df[
        ["url", "label", "source"]
    ].head()
)

print("\nSaved:", OUTPUT)
