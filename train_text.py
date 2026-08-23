import pandas as pd
import numpy as np
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    average_precision_score
)

# ==========================================
# SETTINGS
# ==========================================

DATA = "data/scamlens_text_v7.csv"

MAX_WORDS = 10000
SEQUENCE_LENGTH = 150
EMBEDDING_DIM = 64

RANDOM_STATE = 42

# ==========================================
# LOAD DATA
# ==========================================

print("Loading dataset...")

df = pd.read_csv(DATA)

df["label"] = df["label"].astype("float32")
print("Dataset:", len(df))

print("\nClass distribution:")
print(df["label"].value_counts())

# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X = df["text"].astype(str).to_numpy()
y = df["label"].astype("float32").to_numpy()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=RANDOM_STATE
)
# Validation split

X_train, X_val, y_train, y_val = train_test_split(
    X_train,
    y_train,
    test_size=0.20,
    stratify=y_train,
    random_state=RANDOM_STATE
)

print("\nData split:")
print("Train:", len(X_train))
print("Validation:", len(X_val))
print("Test:", len(X_test))

# ==========================================
# TEXT VECTORIZATION
# ==========================================

print("\nBuilding text vectorizer...")

vectorizer = tf.keras.layers.TextVectorization(
    max_tokens=MAX_WORDS,
    output_mode="int",
    output_sequence_length=SEQUENCE_LENGTH
)

vectorizer.adapt(X_train)

print(
    "Vocabulary size:",
    len(vectorizer.get_vocabulary())
)

# ==========================================
# CLASS WEIGHTS
# ==========================================

negative = np.sum(y_train == 0)
positive = np.sum(y_train == 1)

class_weight = {
    0: 1.0,
    1: negative / positive
}

print("\nClass weights:")
print(class_weight)

# ==========================================
# MODEL
# ==========================================

print("\nBuilding neural network...")

model = tf.keras.Sequential([

    tf.keras.layers.Input(
        shape=(),
        dtype=tf.string
    ),

    vectorizer,

    tf.keras.layers.Embedding(
        input_dim=MAX_WORDS,
        output_dim=EMBEDDING_DIM,
        mask_zero=True
    ),

    tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM(64)
    ),

    tf.keras.layers.Dense(
        64,
        activation="relu"
    ),

    tf.keras.layers.Dropout(0.4),

    tf.keras.layers.Dense(
        1,
        activation="sigmoid"
    )
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),

    loss="binary_crossentropy",

    metrics=[
        tf.keras.metrics.BinaryAccuracy(
            name="accuracy"
        ),

        tf.keras.metrics.Precision(
            name="precision"
        ),

        tf.keras.metrics.Recall(
            name="recall"
        ),

        tf.keras.metrics.AUC(
            name="auc"
        ),

        tf.keras.metrics.AUC(
            name="pr_auc",
            curve="PR"
        )
    ]
)

model.summary()

# ==========================================
# CALLBACKS
# ==========================================

callbacks = [

    tf.keras.callbacks.EarlyStopping(
        monitor="val_pr_auc",
        mode="max",
        patience=3,
        restore_best_weights=True
    ),

    tf.keras.callbacks.ModelCheckpoint(
        "model/scamlens_text_v7.keras",
        monitor="val_pr_auc",
        mode="max",
        save_best_only=True
    )
]

# ==========================================
# TRAIN
# ==========================================

print("\nStarting training...")

history = model.fit(
    X_train,
    y_train,

    validation_data=(
        X_val,
        y_val
    ),

    epochs=15,

    batch_size=64,

    class_weight=class_weight,

    callbacks=callbacks,

    verbose=1
)

# ==========================================
# LOAD BEST MODEL
# ==========================================

model = tf.keras.models.load_model(
    "model/scamlens_text_v7.keras"
)

# ==========================================
# TEST
# ==========================================

print("\nEvaluating...")

probabilities = model.predict(
    X_test,
    batch_size=256,
    verbose=1
).ravel()

predictions = (
    probabilities >= 0.5
).astype(int)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "LEGITIMATE",
            "SCAM"
        ],
        digits=4
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)

# ==========================================
# PR-AUC
# ==========================================

pr_auc = average_precision_score(
    y_test,
    probabilities
)

print(
    f"\nPR-AUC: {pr_auc:.4f}"
)

print(
    "\nModel saved as:"
)

print(
    "model/scamlens_text_v7.keras"
)

print(
    "\nScamLens Text Model v1 complete!"
)
