import re
import ipaddress
from urllib.parse import urlparse


HTTP_URL_PATTERN = re.compile(
    r'https?://[^\s<>"\']+',
    re.IGNORECASE
)

BARE_DOMAIN_PATTERN = re.compile(
    r'(?<![@\w.-])'
    r'[a-zA-Z0-9][a-zA-Z0-9-]*'
    r'(?:\.[a-zA-Z0-9][a-zA-Z0-9-]*)+'
    r'(?:/[^\s<>"\']*)?',
    re.IGNORECASE
)


def clean_url(url):
    return url.strip().rstrip(
        ".,!?;:)]}>\"'"
    )


def valid_domain(url):

    try:

        parsed = urlparse(url)
        domain = parsed.hostname

        if not domain:
            return False

        domain = domain.lower().rstrip(".")

        # Real IP addresses are valid.
        try:
            ipaddress.ip_address(domain)
            return True
        except ValueError:
            pass

        parts = domain.split(".")

        if len(parts) < 2:
            return False

        # TLD must contain letters only.
        tld = parts[-1]

        if not re.fullmatch(
            r"[a-zA-Z]{2,63}",
            tld
        ):
            return False

        for part in parts:

            if not re.fullmatch(
                r"[a-zA-Z0-9-]+",
                part
            ):
                return False

            if part.startswith("-"):
                return False

            if part.endswith("-"):
                return False

        return True

    except Exception:

        return False


def extract_urls(text):

    if not text:
        return []

    found = []

    # =====================================
    # EXPLICIT HTTP/HTTPS URLS
    # =====================================

    for match in HTTP_URL_PATTERN.findall(text):

        url = clean_url(match)

        if valid_domain(url):

            if url not in found:
                found.append(url)

    # =====================================
    # BARE DOMAINS
    # =====================================

    for match in BARE_DOMAIN_PATTERN.findall(text):

        url = clean_url(match)

        

        # Ignore domains already detected.
        if any(
            url in existing
            or existing.endswith(url)
            for existing in found
        ):
            continue

        full_url = "https://" + url

        parsed = urlparse(full_url)
        domain = parsed.hostname or ""

# Numeric-leading domains need a path.
# This prevents things like "457.11.Not"
# from being detected as URLs.
        if domain.split(".")[0].isdigit():

            if not parsed.path or parsed.path == "/":
                    continue

        if valid_domain(full_url):

             if full_url not in found:
                found.append(full_url)

    return found
