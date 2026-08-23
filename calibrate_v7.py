import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, average_precision_score

DATA = "data/scamlens_text_v7.csv"
MODEL = "model/scamlens_text_v7_svm_calibrated.joblib"

print("========== CALIBRATING SCAMLENS V7 ==========")

df = pd.read_csv(DATA)

X = df["text"].astype(str)
y = df["label"].astype(int)

print("Dataset:", len(df))

X_train, X_cal, y_train, y_cal = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

print("Training:", len(X_train))
print("Calibration:", len(X_cal))

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=100000,
        sublinear_tf=True
    )),
    ("svm", CalibratedClassifierCV(
        LinearSVC(class_weight="balanced"),
        method="sigmoid",
        cv=5
    ))
])

print("\nTraining calibrated SVM...")

pipeline.fit(X_train, y_train)

probabilities = pipeline.predict_proba(X_cal)[:, 1]
predictions = pipeline.predict(X_cal)

print("\nClassification Report:")
print(classification_report(
    y_cal,
    predictions,
    target_names=["LEGITIMATE", "SCAM"]
))

print(
    "PR-AUC:",
    average_precision_score(y_cal, probabilities)
)

joblib.dump(pipeline, MODEL)

print("\nSaved:")
print(MODEL)
