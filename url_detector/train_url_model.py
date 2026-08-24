import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score
)


TRAIN = "data/url_train.csv"
TEST = "data/url_test.csv"


# ==============================
# LOAD DATA
# ==============================

train = pd.read_csv(TRAIN)
test = pd.read_csv(TEST)

DROP = ["url", "label", "source"]

X_train = train.drop(columns=DROP)
y_train = train["label"]

X_test = test.drop(columns=DROP)
y_test = test["label"]


print("=" * 60)
print("SCAMLENS URL MODEL")
print("=" * 60)

print("Training:", len(train))
print("Testing :", len(test))
print("Features:", X_train.shape[1])


# ==============================
# MODELS
# ==============================

models = {

    "LOGISTIC": Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        ))
    ]),

    "SVM": Pipeline([
        ("scale", StandardScaler()),
        ("model", SVC(
            kernel="rbf",
            probability=True,
            class_weight="balanced"
        ))
    ])
}


results = []


# ==============================
# TRAIN
# ==============================

for name, model in models.items():

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    model.fit(
        X_train,
        y_train
    )

    pred = model.predict(X_test)

    prob = model.predict_proba(
        X_test
    )[:, 1]

    acc = accuracy_score(
        y_test,
        pred
    )

    precision = precision_score(
        y_test,
        pred
    )

    recall = recall_score(
        y_test,
        pred
    )

    f1 = f1_score(
        y_test,
        pred
    )

    auc = roc_auc_score(
        y_test,
        prob
    )

    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1       : {f1:.4f}")
    print(f"ROC-AUC  : {auc:.4f}")

    print("\nConfusion Matrix:")
    print(confusion_matrix(
        y_test,
        pred
    ))

    results.append([
        name,
        acc,
        precision,
        recall,
        f1,
        auc
    ])

    # Save model
    filename = (
        "model/scamlens_url_"
        + name.lower()
        + ".joblib"
    )

    joblib.dump(
        model,
        filename
    )

    print("\nSaved:", filename)


# ==============================
# COMPARISON
# ==============================

results_df = pd.DataFrame(
    results,
    columns=[
        "Model",
        "Accuracy",
        "Precision",
        "Recall",
        "F1",
        "ROC-AUC"
    ]
)

print()
print("=" * 60)
print("FINAL COMPARISON")
print("=" * 60)

print(
    results_df
    .sort_values("F1", ascending=False)
    .to_string(index=False)
)
