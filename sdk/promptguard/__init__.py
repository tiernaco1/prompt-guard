import requests

_API_URL = "https://prompt-guard.fly.dev"


def protect(prompt: str, api_url: str = _API_URL) -> dict:
    """
    Check a prompt against the PromptGuard firewall.

    Args:
        prompt: The user prompt to check.
        api_url: Override the API base URL (default: hosted Fly.io instance).

    Returns:
        dict with keys:
            action  — "allow" | "block" | "sanitise"
            tier    — 1 or 2
            t1_label — Tier 1 classifier label
            analysis — dict with attack_type, severity, confidence,
                        explanation, sanitised_version (Tier 2 only, may be None)

    Raises:
        requests.HTTPError on non-2xx response.
        requests.Timeout  if API takes longer than 10 seconds.
    """
    resp = requests.post(
        f"{api_url}/check",
        json={"prompt": prompt},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
