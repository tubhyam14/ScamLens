import joblib

MODEL = "model/scamlens_text_v7_svm_calibrated.joblib"

model = joblib.load(MODEL)

messages = [
    "Dear Customer, Acct XXXX1313 Dr. INR 6.00 on 21/08/26 to MEDICINE HOU; UPI: 659972994061; Bal INR 457.11.Not you?SMS BLOCKUPI to 9901771222-CanaraBank",

    "Your IOCL one time password is :7357. It would be valid for 10 mins. INDANE",

    "<#> Hi, 2093 is your OTP for Airtel Xstream Play App. Enjoy unlimited entertainment, anytime, anywhere! /Jx+fMTKpkw",

    "Recharge of INR 299.00 is successful for your Airtel Mobile on 02-07-2026 10:52, Transaction ID 33616569.",

    "Hi, Your Prepaid recharge of Rs. 299.0 is success against Order Id 7478316882133004288.",

    "Can you send me the notes from today's class?",

    "Your Amazon order has been shipped and will arrive tomorrow.",

    "dearyourholidaywillbefro Account: (8981627008) Received: Rs.10293 Balance: Rs.31821 Date: 29-Jul 15:35 View details bit.ly/4hC33g7 allen",

    "Trade Confirmation Dear Patient VIP Gift : F.A.Bal You got 2888 bonus in ur account 627008 ?@Day Obligation Click cutt.ly/ByadsUnc?7008 ZUARIMONEY",

    "Your bank account has been blocked. Verify your KYC immediately at https://bit.ly/verify123",

    "Congratulations! You won Rs.25 lakh in the lottery. Pay Rs.2500 to claim it.",

    "URGENT: Your electricity connection will be disconnected today. Pay immediately at https://bit.ly/pay123",

    "Your UPI cashback of Rs.5000 is waiting. Click here to claim: http://example-scam.in",

    "Your parcel is held at customs. Pay Rs.49 immediately to release it: https://bit.ly/parcel123",

    "You have been selected for a work-from-home job earning Rs.50000 per month. Contact us on WhatsApp."
]

print("========== SCAMLENS V7 CALIBRATED SVM ==========")

for message in messages:

    probability = model.predict_proba([message])[0][1] * 100
    prediction = "SCAM" if probability >= 50 else "LEGITIMATE"

    print("\nMessage:")
    print(message)
    print(f"Scam probability : {probability:.2f}%")
    print(f"Prediction       : {prediction}")
    print("-" * 60)
