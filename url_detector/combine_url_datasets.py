import pandas as pd

malicious = pd.read_csv(
    "data/url_dataset_v2.csv"
)

legitimate = pd.read_csv(
    "data/url_legitimate_v1.csv"
)

df = pd.concat(
    [malicious, legitimate],
    ignore_index=True
)

# Remove exact duplicate URLs
df = df.drop_duplicates(
    subset=["url"]
)

# Shuffle
df = df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

df.to_csv(
    "data/url_dataset_v3.csv",
    index=False
)

print("=" * 60)
print("SCAMLENS URL DATASET V3")
print("=" * 60)

print("Total:", len(df))

print("\nLabels:")
print(df["label"].value_counts())

print("\nSources:")
print(df["source"].value_counts())

print("\nDuplicate URLs:", df["url"].duplicated().sum())

print("\nSaved: data/url_dataset_v3.csv")
