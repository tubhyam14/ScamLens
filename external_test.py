import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

TRAIN = "data/scamlens_text_v7.csv"
TEST = "data/scamlens_hard_external_v1.csv"

train = pd.read_csv(TRAIN)
test = pd.read_csv(TEST)

X_train = train["text"].astype(str)
y_train = train["label"].astype(int)

X_test = test["text"].astype(str)
y_test = test["label"].astype(int)

models = {

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

print("========== SCAMLENS EXTERNAL TEST ==========")
print("Training:", len(train))
print("External:", len(test))

for name, model in models.items():

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        pred,
        target_names=["LEGITIMATE", "SCAM"]
    ))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, pred))

print("\n========== INDIVIDUAL PREDICTIONS ==========")

model = models["WORD + SVM"]
model.fit(X_train, y_train)

pred = model.predict(X_test)

for text, actual, result in zip(X_test, y_test, pred):

    label = "SCAM" if result == 1 else "LEGITIMATE"
    actual_label = "SCAM" if actual == 1 else "LEGITIMATE"

    print("\nMessage:")
    print(text)
    print("Actual :", actual_label)
    print("Model  :", label)
