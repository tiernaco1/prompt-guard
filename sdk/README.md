# PromptGuard

A prompt injection firewall for AI applications.

## Install

```bash
pip install promptguard-firewall
```

## Usage

```python
from promptguard import protect

result = protect("Ignore all previous instructions and...")

if result["action"] == "block":
    print("Attack blocked!")
elif result["action"] == "sanitise":
    print("Sanitised:", result["analysis"]["sanitised_version"])
else:
    print("Safe to forward to your LLM")
```

## Response format

```json
{
  "action": "block",
  "tier": 1,
  "t1_label": "OBVIOUS_ATTACK",
  "analysis": null
}
```

| Field | Values |
|-------|--------|
| `action` | `"allow"` / `"block"` / `"sanitise"` |
| `tier` | `1` (fast, ~250ms) or `2` (deep analysis, ~2s) |
| `analysis` | `null` for Tier 1 blocks, full JSON for Tier 2 |
