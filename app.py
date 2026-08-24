from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import the core analysis pipeline directly from predict.py
from predict import analyze_sms

app = FastAPI(title="ScamLens AI API", version="2.0.0")

# Enable CORS for the Vite React frontend (running on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    text: str

class URLDetail(BaseModel):
    original_url: str
    final_url: str
    score: float
    risk: str
    reasons: List[str]

class AnalyzeResponse(BaseModel):
    is_scam: bool
    risk_level: str
    score: float
    text_score: float
    ai_explanation: str
    detected_triggers: List[str]
    recommended_action: str
    urls_found: List[URLDetail]

def format_score(score: float) -> str:
    return str(int(score)) if score.is_integer() else f"{score:.2f}"

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_message(request: AnalyzeRequest):
    text = request.text.strip()
    if not text:
        return AnalyzeResponse(
            is_scam=False,
            risk_level="LOW",
            score=0.0,
            text_score=0.0,
            ai_explanation="No message content provided.",
            detected_triggers=[],
            recommended_action="Paste a suspicious SMS or email to scan.",
            urls_found=[]
        )

    # Run the machine learning pipeline
    text_prob, text_pred, text_risk, url_results = analyze_sms(text)
    text_score = round(text_prob * 100, 2)

    # Compute final combined scoring logic matching predict.py
    if not url_results:
        final_score = text_score * 0.75
    else:
        max_url_score = max(r.get("score", 0.0) for r in url_results)
        final_score = max(text_score * 0.60 + max_url_score * 0.40, max_url_score)

    final_score = round(final_score, 2)

    # Determine risk verdict
    if final_score >= 70:
        risk_level = "HIGH"
        is_scam = True
        recommended_action = "DO NOT click links, share OTPs, or transfer money. Block and report the sender."
    elif final_score >= 40:
        risk_level = "MEDIUM"
        is_scam = True
        recommended_action = "Proceed with caution. Verify the sender through official channels before responding."
    else:
        risk_level = "LOW"
        is_scam = False
        recommended_action = "No immediate threats detected. Maintain general security practices."

    # Aggregate triggers and reasons
    triggers = []
    if text_risk in ["HIGH", "MEDIUM"]:
        triggers.append(f"Text pattern flagged as suspicious ({text_score}% scam probability)")
    
    for url_res in url_results:
        for reason in url_res.get("reasons", []):
            if reason not in triggers:
                triggers.append(f"URL Flag: {reason}")

# Build human-readable explanation
    formatted_final = format_score(final_score)
    if is_scam:
        explanation = (
            f"Analysis completed with a risk score of {formatted_final}/100. "
            f"The message contains behavioral patterns or URL indicators commonly associated with fraud."
        )
    else:
        explanation = (
            f"Analysis completed with a low risk score of {formatted_final}/100. "
            f"No high-confidence phishing indicators or malicious URLs were detected."
        )

    formatted_urls = [
        URLDetail(
            original_url=r.get("original_url", ""),
            final_url=r.get("final_url", ""),
            score=round(r.get("score", 0.0), 2),
            risk=r.get("risk", "UNKNOWN"),
            reasons=r.get("reasons", [])
        )
        for r in url_results
    ]

    return AnalyzeResponse(
        is_scam=is_scam,
        risk_level=risk_level,
        score=final_score,
        text_score=text_score,
        ai_explanation=explanation,
        detected_triggers=triggers,
        recommended_action=recommended_action,
        urls_found=formatted_urls
    )
