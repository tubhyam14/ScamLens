from url_extract import extract_urls


sms = """URGENT!

Your bank account is blocked.

Verify here:
https://bit.ly/verify123

If you did not request this, visit https://www.airtel.in/

Reference:
317.buzz/U9a-8981627008
"""


urls = extract_urls(sms)

print("URLs detected:", len(urls))

for i, url in enumerate(urls, 1):
    print(f"{i}: {url}")
