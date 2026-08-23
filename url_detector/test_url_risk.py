import sys

from url_risk import analyze_url


if len(sys.argv) < 2:
    print('Usage: python url_detector/test_url_risk.py "URL"')
    sys.exit(1)


url = sys.argv[1]

result = analyze_url(url)

print()
print("=" * 60)
print("SCAMLENS URL RISK")
print("=" * 60)

print("Original URL :", result["original_url"])
print("Final URL    :", result["final_url"])

print()
print(f"Risk score   : {result['score']:.2f}/100")
print(f"Risk level   : {result['risk']}")

print()
print(
    f"Original ML  : {result['original_score']:.2f}%"
)

print(
    f"Final ML     : {result['final_score']:.2f}%"
)

print(
    f"Redirects    : {result['redirect_count']}"
)

print(
    f"Domain change: {result['domain_changed']}"
)

if result["reasons"]:
    print()
    print("Reasons:")

    for reason in result["reasons"]:
        print(" -", reason)
