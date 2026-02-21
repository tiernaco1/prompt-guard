# PromptGuard — AI Prompt Injection Firewall

> Defending AI with AI. Real-time two-tier firewall that detects and blocks prompt injection attacks before they reach the model.

## Architecture

```
User Input
    │
    ▼
┌──────────────────────────────┐
│  TIER 1: Crusoe / Qwen3-235B │  <500ms — classifies every prompt
│  SAFE / SUSPICIOUS / ATTACK  │
└──────────┬───────────────────┘
           │ suspicious / obvious attack
           ▼
┌──────────────────────────────┐
│  TIER 2: Claude Haiku        │  deep analysis — JSON verdict
│  BLOCK / SANITISE / ALLOW    │  attack_type, confidence, reason
└──────────────────────────────┘
```

**6-category attack taxonomy:** Direct Jailbreak, Indirect Injection, Role Hijacking, Payload Smuggling, Context Manipulation, Information Extraction.

## Quick Start (Docker — recommended)

```bash
# 1. Add your API keys to .env
#    CRUSOE_API_KEY=...
#    CLAUDE_API_KEY=...

# 2. Start everything
docker compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

The backend healthcheck runs automatically — the frontend container will start once the backend is healthy (~15s).

## Quick Start (local, no Docker)

```bash
# Terminal 1 — Backend
cd proxy
pip install -r requirements.txt
uvicorn api:app --reload

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```

## Project Structure

```
prompt-guard/
├── proxy/                        # FastAPI backend
│   ├── api.py                    # /check and /health endpoints
│   ├── requirements.txt
│   ├── Dockerfile
│   └── detection/
│       └── crusoe_tier.py        # Two-tier firewall logic
├── frontend/                     # React + Vite UI
│   ├── Dockerfile
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       └── widget/               # Firewall widget components
├── data/
│   ├── prompts/                  # Tier 1 & Tier 2 prompt templates
│   ├── labelled/                 # HuggingFace labelled datasets
│   └── spot_test.py              # Evaluation harness
├── eval/
│   ├── attacks_testing.jsonl     # Hand-written attack test cases (60)
│   └── benign_testing.jsonl      # Hand-written benign test cases (33)
├── docker-compose.yml
└── .env                          # API keys (not committed)
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/check` | Run prompt through firewall — returns `action`, `tier`, `analysis` |
| GET | `/health` | Health check — returns `{"status": "ok"}` |
| GET | `/docs` | Auto-generated Swagger UI |
 GET | `/session/stats` | Dashboard statistics |
| GET | `/session/history` | Prompt history |
| POST | `/report` | Generate threat report |
| POST | `/session/reset` | Reset session |
| GET | `/health` | Health check |

### POST /check

Request:
```json
{ "prompt": "Ignore all previous instructions..." }
```

Response (Tier 1 SAFE — fast path):
```json
{ "action": "allow", "tier": 1 }
```

Response (Tier 2 — attack detected):
```json
{
  "action": "block",
  "tier": 2,
  "analysis": {
    "verdict": "BLOCK",
    "attack_type": "direct_jailbreak",
    "confidence": 0.97,
    "reason": "Explicit instruction override attempt"
  }
}
```

## Running Evaluation

```bash
# Quick run — 93 hand-written prompts, no extra API spend
python data/spot_test.py --quick

# Full run — adds English-only HuggingFace samples (~113 prompts)
python data/spot_test.py

# Test Tier 2 (Claude) prompt in isolation
python data/spot_test.py --quick --tier2-only

# Latency check — times 20 Tier 1 calls vs <500ms target
python data/latency_check.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CRUSOE_API_KEY` | Crusoe hackathon API key |
| `CLAUDE_API_KEY` | Anthropic API key |

## Challenge Alignment

| Prize | How |
|-------|-----|
| Security Track | OWASP LLM01 — the #1 AI-enabled threat |
| Best Use of Claude | Deep analysis engine + structured JSON verdicts |
| Best Use of Crusoe | High-throughput Tier 1 triage at <500ms using Qwen3-235B |
| Best Use of Data | 4+ sources, 6-category taxonomy, 98% accuracy |
| Best Adaptable Agent | Session-level attack pattern tracking |
