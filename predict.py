import sys
import pandas as pd
import joblib

from url_detector.url_extract import extract_urls
from url_detector.url_risk import analyze_url


MODEL = "model/scamlens_text_v7_svm_calibrated.joblib"

model = joblib.load(MODEL)


def predict_text(text):

  

    probability = model.predict_proba([text])[0][1]

    prediction = (
        "SCAM"
        if probability >= 0.5
        else "LEGITIMATE"
    )

    if probability >= 0.70:
        risk = "HIGH"

    elif probability >= 0.40:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    return probability, prediction, risk


def analyze_sms(text):

    urls = extract_urls(text)

    text_without_urls = text
    for url in urls:
        text_without_urls = text_without_urls.replace(url, " ")

    text_probability, text_prediction, text_risk = predict_text(
      text_without_urls
     )
    url_results = []

    for url in urls:

        try:
            result = analyze_url(url)
            url_results.append(result)

        except Exception as e:

            print(
                f"\nURL analysis failed for {url}: {e}"
            )

    return (
        text_probability,
        text_prediction,
        text_risk,
        url_results
    )


def main():

    if len(sys.argv) > 1:

        # Command-line mode
        text = " ".join(sys.argv[1:])

        analyze_and_print(text)

        return

    # Interactive mode
    print("========== SCAMLENS ==========")
    print("Paste an SMS.")
    print("You can use multiple lines.")
    print("Type END on a new line to analyze.")
    print("Type exit to quit.")
    print()

    while True:

        lines = []

        while True:

            try:
                line = input()

            except EOFError:
                return

            if line.strip().lower() == "exit":

                print(
                    "\nExiting ScamLens."
                )

                return

            if line.strip() == "END":
                break

            lines.append(line)

        text = "\n".join(lines)

        if not text.strip():
            continue

        analyze_and_print(text)


def analyze_and_print(text):

    (
        text_probability,
        text_prediction,
        text_risk,
        url_results
    ) = analyze_sms(text)

    # =====================================
    # TEXT ANALYSIS
    # =====================================

    print()
    print("=" * 60)
    print("SCAMLENS TEXT ANALYSIS")
    print("=" * 60)

    print(
        f"Scam probability : "
        f"{text_probability * 100:.2f}%"
    )

    print(
        f"Prediction       : {text_prediction}"
    )

    print(
        f"Risk level       : {text_risk}"
    )

    # =====================================
    # URL ANALYSIS
    # =====================================

    print()
    print("=" * 60)
    print("SCAMLENS URL ANALYSIS")
    print("=" * 60)

    print(
        f"URLs detected    : {len(url_results)}"
    )

    for i, result in enumerate(
        url_results,
        1
    ):

        print()
        print(f"URL #{i}")
        print("-" * 40)

        print(
            "Original :",
            result["original_url"]
        )

        print(
            "Final    :",
            result["final_url"]
        )

        print(
            f"URL score : "
            f"{result['score']:.2f}/100"
        )

        print(
            "URL risk  :",
            result["risk"]
        )

        if result["reasons"]:

            print("Reasons:")

            for reason in result["reasons"]:

                print(
                    " -",
                    reason
                )

    # =====================================
    # COMBINED VERDICT
    # =====================================

    text_score = text_probability * 100
    

    if not url_results:

        # No URL:
        # reduce the influence of the text model.
        final_score = text_score * 0.75

    else:

        # URL exists:
        # combine text and URL evidence.
        url_score = max(
            r["score"]
            for r in url_results
        )

        final_score = max(
            text_score * 0.60
            + url_score * 0.40,
            url_score
        )

    # =====================================
    # FINAL RISK
    # =====================================

    if final_score >= 70:

        final_prediction = "SCAM"
        final_risk = "HIGH"

    elif final_score >= 40:

        final_prediction = "REVIEW"
        final_risk = "MEDIUM"

    else:

        final_prediction = "LEGITIMATE"
        final_risk = "LOW"

    # =====================================
    # FINAL OUTPUT
    # =====================================

    print()
    print("=" * 60)
    print("FINAL SCAMLENS VERDICT")
    print("=" * 60)

    print(
        f"Combined score : "
        f"{final_score:.2f}/100"
    )

    print(
        f"Prediction     : "
        f"{final_prediction}"
    )

    print(
        f"Risk level     : "
        f"{final_risk}"
    )

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
