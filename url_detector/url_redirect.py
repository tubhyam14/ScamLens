import requests
from urllib.parse import urlparse


def resolve_url(url, timeout=8):
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={
                "User-Agent": "ScamLens/1.0"
            }
        )

        chain = [r.url for r in response.history]
        chain.append(response.url)

        return {
            "success": True,
            "chain": chain,
            "final_url": response.url,
            "status": response.status_code
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "chain": [url],
            "final_url": url,
            "status": None,
            "error": str(e)
        }


def domain(url):
    return (urlparse(url).hostname or "").lower()


def analyze_redirect(url):
    result = resolve_url(url)

    original_domain = domain(url)
    final_domain = domain(result["final_url"])

    result["original_domain"] = original_domain
    result["final_domain"] = final_domain
    result["domain_changed"] = (
        original_domain != final_domain
    )
    result["redirect_count"] = max(
        0,
        len(result["chain"]) - 1
    )

    return result
