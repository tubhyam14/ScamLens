import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

TRAIN = "data/scamlens_text_v7.csv"
MODEL = "model/scamlens_text_v7_svm.joblib"

print("========== SAVING SCAMLENS V7 SVM ==========")

df = pd.read_csv(TRAIN)

X = df["text"].astype(str)
y = df["label"].astype(int)

print("Training samples:", len(df))

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=100000,
        sublinear_tf=True
    )),
    ("svm", LinearSVC(
        class_weight="balanced"
    ))
])

print("Training Word TF-IDF + SVM...")

model.fit(X, y)

joblib.dump(model, MODEL)

print("\nModel saved:")
print(MODEL)

print("\nV7 SVM ready.")
