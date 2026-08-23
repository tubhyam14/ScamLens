import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    classification_report,
    confusion_matrix
)

DATA = "data/scamlens_text_v7.csv"
RANDOM_STATE = 42

print("========== SCAMLENS ALGORITHM BENCHMARK ==========")

df = pd.read_csv(DATA)

X = df["text"].astype(str)
y = df["label"].astype(int)

print("Dataset:", len(df))
print("\nLabels:")
print(y.value_counts())

# Same split for every algorithm
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=RANDOM_STATE
)

models = {

    "WORD + LOGISTIC": Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_features=100000,
            sublinear_tf=True
        )),
        ("model", LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ))
    ]),

    "WORD + SVM": Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_features=100000,
            sublinear_tf=True
        )),
        ("model", LinearSVC(
            class_weight="balanced"
        ))
    ]),

    "CHAR + LOGISTIC": Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char",
            ngram_range=(3, 5),
            min_df=2,
            max_features=150000,
            sublinear_tf=True
        )),
        ("model", LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ))
    ]),

    "CHAR + SVM": Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char",
            ngram_range=(3, 5),
            min_df=2,
            max_features=150000,
            sublinear_tf=True
        )),
        ("model", LinearSVC(
            class_weight="balanced"
        ))
    ])
}

results = []

for name, model in models.items():

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    # Probability-like score
    if hasattr(model, "predict_proba"):
        score = model.predict_proba(X_test)[:, 1]
    else:
        score = model.decision_function(X_test)

    accuracy = accuracy_score(y_test, pred)
    precision = precision_score(y_test, pred)
    recall = recall_score(y_test, pred)
    f1 = f1_score(y_test, pred)
    pr_auc = average_precision_score(y_test, score)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1       : {f1:.4f}")
    print(f"PR-AUC   : {pr_auc:.4f}")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, pred))

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "PR-AUC": pr_auc
    })

print("\n\n========== FINAL COMPARISON ==========")

result_df = pd.DataFrame(results)

print(
    result_df
    .sort_values("PR-AUC", ascending=False)
    .to_string(index=False)
)

result_df.to_csv(
    "data/algorithm_benchmark_v1.csv",
    index=False
)

print("\nSaved:")
print("data/algorithm_benchmark_v1.csv")
