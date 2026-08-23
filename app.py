import re
import os
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="ScamLens Intelligence API",
    description="Explainable Financial Fraud & SMS Threat Analysis Engine",
    version="1.0.0"
)

# Enable CORS for React/Web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "model/scamlens_text_v7_svm_calibrated.joblib"

# Load the trained ML model
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✓ Model loaded successfully!")
else:
    model = None
    print(f"! Warning: Model not found at {MODEL_PATH}")

# --- Pydantic Data Models ---
class MessagePayload(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    text: str
    scam_probability: float
    prediction: str
    risk_level: str
    extracted_amount: Optional[str]
    detected_triggers: List[str]
    ai_explanation: str
    recommended_action: str


# --- Heuristic & Explainability Engine ---
def analyze_risk_factors(text: str, probability: float):
    lower_text = text.lower()
    triggers = []
    
    # 1. URL Shorteners & Phishing Links
    url_pattern = r"(https?://\S+|bit\.ly/\S+|cutt\.ly/\S+|tinyurl\.com/\S+|t\.co/\S+)"
    urls = re.findall(url_pattern, text)
    if urls:
        if any(short in lower_text for short in ["bit.ly", "cutt.ly", "tinyurl", "t.co"]):
            triggers.append("Obfuscated/Shortened URL detected (hides actual destination)")
        else:
            triggers.append("External hyperlink detected")

    # 2. Urgency & Account Threat Triggers
    urgency_keywords = ["urgent", "immediately", "today", "blocked", "suspended", "disconnected", "deactivated", "24 hours"]
    found_urgency = [w for w in urgency_keywords if w in lower_text]
    if found_urgency:
        triggers.append(f"High-pressure urgency tactics ('{', '.join(found_urgency[:2])}')")

    # 3. Credential & Verification Lures
    credential_keywords = ["kyc", "pan card", "aadhaar", "otp", "one time password", "pin", "verify account", "update details"]
    found_credentials = [w for w in credential_keywords if w in lower_text]
    if found_credentials:
        triggers.append(f"Requests sensitive identity/banking actions ('{', '.join(found_credentials[:2])}')")

    # 4. Reward & Unrealistic Incentive Lures
    lottery_keywords = ["congratulations", "lottery", "won", "bonus", "cashback", "gift", "work-from-home", "wfh", "earn per month"]
    found_lottery = [w for w in lottery_keywords if w in lower_text]
    if found_lottery:
        triggers.append("Unrealistic financial incentives or lottery lures")

    # 5. Extract Financial Figures
    amount_match = re.search(r"(?:rs\.?|inr|₹)\s?([\d,]+(?:\.\d{2})?)", lower_text)
    extracted_amount = amount_match.group(0).upper() if amount_match else None

    # --- Generate Human-Readable AI Explanations ---
    if probability >= 80:
        risk_level = "HIGH"
        explanation = (
            "This message shows severe indicators of financial fraud. It combines artificial urgency "
            "with requests for sensitive actions or unverified external links to compromise your account."
        )
        action = "DO NOT click any links, share OTPs, or transfer money. Block and report this sender immediately."
    elif probability >= 50:
        risk_level = "MEDIUM"
        explanation = (
            "This message contains ambiguous or suspicious elements that match known phishing templates, "
            "though some legitimate notifications share similar language."
        )
        action = "Verify the request directly through the official bank app or merchant portal. Avoid using contact details from this message."
    else:
        risk_level = "LOW"
        explanation = (
            "The message matches standard transaction notifications or routine communication. "
            "No common fraudulent patterns were identified."
        )
        action = "No immediate security risk detected. Standard caution is always recommended."

    return risk_level, extracted_amount, triggers, explanation, action


# --- API Endpoints ---
@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "ScamLens Intelligence API",
        "model_loaded": model is not None
    }

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_message(payload: MessagePayload):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model file missing. Ensure model/scamlens_text_v7_svm_calibrated.joblib exists."
        )

    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Text field cannot be empty.")

    # Model inference
    prob_scam = float(model.predict_proba([clean_text])[0][1]) * 100.0
    is_scam = prob_scam >= 50.0

    # Risk factor extraction
    risk_level, extracted_amount, triggers, explanation, action = analyze_risk_factors(
        clean_text, prob_scam
    )

    return {
        "text": clean_text,
        "scam_probability": round(prob_scam, 2),
        "prediction": "SCAM" if is_scam else "LEGITIMATE",
        "risk_level": risk_level,
        "extracted_amount": extracted_amount,
        "detected_triggers": triggers,
        "ai_explanation": explanation,
        "recommended_action": action
    }
