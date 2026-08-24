import pandas as pd
import joblib

from url_detector.url_features import extract_features
from url_detector.url_redirect import analyze_redirect
from url_detector.trusted_domains import is_trusted_domain


MODEL = "model/scamlens_url_svm.joblib"

model = joblib.load(MODEL)


def ml_score(url):
    features = extract_features(url)
    X = pd.DataFrame([features])

    return model.predict_proba(X)[0][1]


def analyze_url(url):

    original_score = ml_score(url)

    features = extract_features(url)

    result = analyze_redirect(url)

    final_url = result["final_url"]

    # Analyze final destination separately
    final_score = ml_score(final_url)

    reasons = []

    # =====================================
    # TRUSTED DOMAIN
    # =====================================

    original_trusted = is_trusted_domain(url)
    final_trusted = is_trusted_domain(final_url)

    if original_trusted:
        reasons.append("Original domain is trusted")

    if final_trusted:
        reasons.append("Final destination is a trusted domain")

    # =====================================
    # ML SCORE
    # =====================================

    if original_score >= 0.80:
        reasons.append("Original URL has high ML risk")

    elif original_score >= 0.50:
        reasons.append("Original URL has moderate ML risk")

    # =====================================
    # SHORTENER
    # =====================================

    if features.get("is_shortener", 0):
        reasons.append("URL shortener")

    # =====================================
    # REDIRECT
    # =====================================

    if result["redirect_count"] > 0:
        reasons.append(
            f"{result['redirect_count']} redirect(s)"
        )

    if result["domain_changed"]:
        reasons.append(
            "Final domain differs from original"
        )

    # =====================================
    # FINAL DESTINATION ML
    # =====================================

    if final_score >= 0.80:
        reasons.append(
            "Final destination has high ML risk"
        )

    elif final_score >= 0.50:
        reasons.append(
            "Final destination has moderate ML risk"
        )

    # =====================================
    # COMBINED SCORE
    # =====================================

    score = max(
        original_score,
        final_score
    ) * 100

    # =====================================
    # TRUSTED DOMAIN ADJUSTMENT
    # =====================================

    # A trusted final destination is strong
    # legitimate evidence.
    if final_trusted:

        score *= 0.10

    elif original_trusted and not result["domain_changed"]:

        score *= 0.15

    # =====================================
    # REDIRECT PENALTY
    # =====================================

    if result["domain_changed"]:

        score += 15

    if features.get("is_shortener", 0):

        score += 5

    score = min(score, 100)

    # =====================================
    # RISK LEVEL
    # =====================================

    if score >= 70:
        risk = "HIGH"

    elif score >= 40:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    return {
        "score": score,
        "risk": risk,
        "original_score": original_score * 100,
        "final_score": final_score * 100,
        "original_url": url,
        "final_url": final_url,
        "redirect_count": result["redirect_count"],
        "domain_changed": result["domain_changed"],
        "reasons": reasons,
    }
