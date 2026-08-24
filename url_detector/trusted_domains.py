from pathlib import Path
from urllib.parse import urlparse


# Project root = ~/ScamLens/text_detector
PROJECT_ROOT = Path(__file__).resolve().parent.parent

TRUSTED_FILE = PROJECT_ROOT / "data" / "trusted_domains.txt"


def load_trusted_domains():

    if not TRUSTED_FILE.exists():
        print(f"WARNING: Trusted domain file not found: {TRUSTED_FILE}")
        return set()

    with open(TRUSTED_FILE, "r") as f:

        return {
            line.strip().lower()
            for line in f
            if line.strip()
            and not line.startswith("#")
        }


TRUSTED_DOMAINS = load_trusted_domains()


def get_hostname(url):

    try:
        return (
            urlparse(url).hostname
            or ""
        ).lower()

    except Exception:
        return ""


def is_trusted_domain(url):

    hostname = get_hostname(url)

    if not hostname:
        return False

    for trusted in TRUSTED_DOMAINS:

        if (
            hostname == trusted
            or hostname.endswith("." + trusted)
        ):
            return True

    return False
