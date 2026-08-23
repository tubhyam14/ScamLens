# ScamLens

ScamLens is an SMS scam detection system designed to identify potentially fraudulent messages and estimate their scam probability.

The current version, ScamLens V7, uses a Word TF-IDF + Support Vector Machine (SVM) pipeline with probability calibration.

## Features

- Scam / legitimate SMS classification
- Word-level TF-IDF features
- Linear SVM classifier
- Calibrated scam probability
- Indian SMS and fraud-focused training data
- Detection of KYC, UPI, electricity, courier, job, lottery, tax and digital-arrest scams

## V7 Pipeline

SMS
  ↓
Text preprocessing
  ↓
Word-level TF-IDF
  ↓
Linear SVM
  ↓
Probability calibration
  ↓
Scam probability + prediction

## Algorithm Benchmark

| Model | Accuracy | Precision | Recall | F1 | PR-AUC |
|---|---:|---:|---:|---:|---:|
| Word + SVM | 99.74% | 99.88% | 99.71% | 99.79% | 1.0000 |
| Char + SVM | 99.72% | 99.94% | 99.61% | 99.77% | 1.0000 |
| Word + Logistic | 99.18% | 99.87% | 98.80% | 99.33% | 0.9998 |
| Char + Logistic | 99.18% | 99.92% | 98.75% | 99.33% | 0.9999 |

Word + SVM was selected as the primary classifier.

## Dataset

V7 contains 38,877 messages:

- 24,075 scam messages
- 14,802 legitimate messages

The dataset combines multiple SMS/fraud sources and additional hard examples.

Raw datasets are not included in this repository because they may contain sensitive or third-party SMS content.

## External Testing

A separate test set containing 31 messages was evaluated after training.

- Legitimate: 15
- Scam: 16

Word + SVM correctly classified all 31 messages in this test.

Because the external test set is small, this should not be interpreted as proof of perfect real-world accuracy.

## Probability Calibration

SVM decision scores are not naturally probabilities.

ScamLens uses probability calibration to convert the classifier output into an approximate scam probability.

Example:

Scam probability: 99.98%
Prediction: SCAM

The probability is a model confidence estimate, not a guarantee.

## Example

Legitimate message:

Your IOCL one time password is 7357.
It would be valid for 10 mins. INDANE

Prediction:

Scam probability: 2.69%
Prediction: LEGITIMATE

Scam message:

Your bank account has been blocked.
Verify your KYC immediately at https://bit.ly/verify123

Prediction:

Scam probability: 99.98%
Prediction: SCAM

## Project Structure

ScamLens/
├── benchmark_algorithms.py
├── build_v7.py
├── calibrate_v7.py
├── external_test.py
├── save_v7_svm.py
├── test_calibrated.py
├── test_svm.py
├── test_text.py
├── train_text.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
└── model/

Datasets and trained model files are excluded from Git.

## Installation

Clone the repository:

git clone <YOUR_REPOSITORY_URL>
cd ScamLens

Create a virtual environment:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

## Training

Build the V7 dataset:

python build_v7.py

Train the SVM:

python save_v7_svm.py

Calibrate the model:

python calibrate_v7.py

## Testing

Run the calibrated model:

python test_calibrated.py

Run the external evaluation:

python external_test.py

## Limitations

ScamLens is a machine-learning classifier and should not be treated as a definitive fraud detector.

- Legitimate messages can resemble scams.
- New scam patterns may not be recognized.
- Attackers can modify wording to evade detection.
- Probabilities are confidence estimates.
- Dataset quality affects performance.
- The current external test set is small.

Users should still avoid clicking suspicious links or sharing OTPs, passwords, banking credentials or other sensitive information.

## Future Improvements

- Larger real-world Indian SMS dataset
- Better URL and obfuscation detection
- Character + word feature fusion
- Multilingual support
- URL reputation analysis
- Sender and metadata signals
- Adversarial testing
- Larger independent evaluation datasets
- Real-time Android SMS integration

## License

Add an appropriate open-source license before publishing the project.
