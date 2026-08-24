import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from urllib.parse import urlparse


INPUT = "data/url_dataset_v3.csv"

TRAIN = "data/url_train.csv"
TEST = "data/url_test.csv"


df = pd.read_csv(INPUT)

# Extract hostname
df["domain"] = df["url"].apply(
    lambda x: (urlparse(x).hostname or "").lower()
)

# Group split by domain
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(
        df,
        groups=df["domain"]
    )
)

train = df.iloc[train_idx].copy()
test = df.iloc[test_idx].copy()

# Remove helper column
train.drop(columns=["domain"], inplace=True)
test.drop(columns=["domain"], inplace=True)

train.to_csv(TRAIN, index=False)
test.to_csv(TEST, index=False)


print("=" * 60)
print("SCAMLENS URL DOMAIN-GROUPED SPLIT")
print("=" * 60)

print("Total :", len(df))
print("Train :", len(train))
print("Test  :", len(test))

print("\nTrain labels:")
print(train["label"].value_counts())

print("\nTest labels:")
print(test["label"].value_counts())


# Verify no domain leakage
train_domains = set(
    df.iloc[train_idx]["domain"]
)

test_domains = set(
    df.iloc[test_idx]["domain"]
)

overlap = train_domains & test_domains

print("\nDomain overlap:", len(overlap))

if overlap:
    print("WARNING: domains leaked!")
else:
    print("✓ No domain leakage")


print("\nSaved:")
print(TRAIN)
print(TEST)
