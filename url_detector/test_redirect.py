import sys
from url_redirect import analyze_redirect


if len(sys.argv) < 2:
    print('Usage: python url_detector/test_redirect.py "URL"')
    sys.exit(1)


url = sys.argv[1]

result = analyze_redirect(url)

print()
print("=" * 60)
print("SCAMLENS REDIRECT ANALYZER")
print("=" * 60)

if not result["success"]:
    print("Redirect check failed")
    print("Error:", result["error"])
    sys.exit(1)

print("Original domain :", result["original_domain"])
print("Final domain    :", result["final_domain"])
print("Redirects       :", result["redirect_count"])
print("HTTP status     :", result["status"])

print()
print("Redirect chain:")

for i, item in enumerate(result["chain"]):
    print(f"{i}: {item}")

print()

if result["domain_changed"]:
    print("⚠ DOMAIN CHANGED")
else:
    print("✓ Domain unchanged")

