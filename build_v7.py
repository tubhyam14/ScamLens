import pandas as pd
from pathlib import Path

print("========== BUILDING SCAMLENS V7 ==========")

datasets = []

# Existing V6 dataset
v6 = pd.read_csv("data/scamlens_text_v6.csv")
datasets.append(v6[["label", "text"]])
print("V6:", len(v6))

# Indian fraud dataset
india = pd.read_csv("data/india_fraud_detection_FINAL.csv")

india = india.rename(columns={
    "message_text": "text"
})

india = india[["label", "text"]]
datasets.append(india)

print("Indian fraud:", len(india))

# Hard examples
hard = pd.read_csv("data/scamlens_hard_v5.csv")
datasets.append(hard[["label", "text"]])

print("Hard examples:", len(hard))

# Combine
df = pd.concat(datasets, ignore_index=True)

# Normalize
df["text"] = (
    df["text"]
    .astype(str)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

df["label"] = df["label"].astype(int)

# Remove exact duplicates
before = len(df)
df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

print("\nDuplicates removed:", before - len(df))

print("\nFinal distribution:")
print(df["label"].value_counts())

print("\nFinal size:", len(df))

# Save
out = "data/scamlens_text_v7.csv"
df.to_csv(out, index=False)

print("\nSaved:")
print(out)
