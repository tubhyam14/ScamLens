import sys
import pandas as pd
import joblib
from url_features import extract_features


MODEL = "model/scamlens_url_svm.joblib"

model = joblib.load(MODEL)


if len(sys.argv) < 2:
    print('Usage: python url_detector/test_url_model.py "URL"')
    sys.exit(1)


url = sys.argv[1]

features = extract_features(url)

X = pd.DataFrame([features])

prob = model.predict_proba(X)[0][1]

prediction = "SCAM" if prob >= 0.5 else "LEGITIMATE"


print()
print("========== SCAMLENS URL DETECTOR ==========")
print("URL              :", url)
print(f"Scam probability : {prob * 100:.2f}%")
print("Prediction       :", prediction)
