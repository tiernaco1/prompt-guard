# PromptGuard — AI Prompt Injection Firewall

> Defending AI with AI. Real-time two-tier firewall that detects and blocks prompt injection attacks before they reach the model.

## Architecture

```
User Input
    │
    ▼
┌──────────────────────────────┐
│  TIER 1: Crusoe / Llama 3   │  <500ms — classifies every prompt
│  SAFE / SUSPICIOUS / ATTACK  │
└──────────┬───────────────────┘
           │ suspicious / obvious attack
           ▼
┌──────────────────────────────┐
│  TIER 2: Claude (Sonnet)    │  deep analysis — JSON verdict
│  BLOCK / SANITISE / ALLOW   │  attack_type, severity, explanation
└──────────────────────────────┘
```

**6-category attack taxonomy:** Direct Jailbreak, Indirect Injection, Role Hijacking, Payload Smuggling, Context Manipulation, Information Extraction.

## Quick Start (Docker — recommended)

```bash
# 1. Fill in your API keys
# edit .env with your CRUSOE_API_KEY and CLAUDE_API_KEY

# 2. Start everything
docker compose up

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API docs: http://localhost:8000/docs
```

## Quick Start (local)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Or use `./start.sh` to launch both together.

## Project Structure

```
promptguard/
├── backend/
│   ├── main.py          # FastAPI endpoints
│   ├── firewall.py      # Two-tier routing logic
│   ├── crusoe_client.py # Tier 1 — Crusoe/Llama wrapper
│   ├── claude_client.py # Tier 2 — Claude wrapper
│   ├── state.py         # Session state & adaptive logic
│   ├── prompts.py       # All prompt templates (Person B owns this)
│   ├── models.py        # Pydantic schemas
│   ├── report.py        # Threat report generator
│   └── config.py        # Config from env vars
├── frontend/
│   └── src/
│       ├── App.jsx              # Root layout
│       ├── components/
│       │   ├── ChatPanel.jsx    # Chat interface
│       │   ├── ChatMessage.jsx  # Message card
│       │   ├── Dashboard.jsx    # Right panel
│       │   ├── StatsBar.jsx     # Top stats
│       │   ├── AttackChart.jsx  # Pie chart
│       │   ├── BlockFeed.jsx    # Recent blocks
│       │   └── ReportModal.jsx  # Threat report overlay
│       ├── api.js       # Backend API calls
│       ├── mockApi.js   # Mock responses for UI dev
│       └── constants.js # Colours, labels
├── data/
│   ├── labelled/        # Curated test cases
│   └── synthetic/       # Claude-generated attacks
├── eval/
│   ├── eval.py               # Automated evaluation
│   └── generate_synthetic.py # Synthetic attack generator
└── docker-compose.yml
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyse` | Run prompt through firewall |
| POST | `/chat` | Chat (firewall + LLM reply) |
| GET | `/session/stats` | Dashboard statistics |
| GET | `/session/history` | Prompt history |
| POST | `/report` | Generate threat report |
| POST | `/session/reset` | Reset session |
| GET | `/health` | Health check |

## Generating Synthetic Attacks (Person B)

```bash
cd promptguard
python eval/generate_synthetic.py --per-category 15
# Outputs to data/synthetic/generated.jsonl
```

## Running Evaluation

```bash
# Ensure backend is running first
python eval/eval.py
# Results saved to eval/results/<timestamp>.json
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CRUSOE_API_KEY` | Crusoe Inference API key |
| `CLAUDE_API_KEY` | Anthropic API key |
| `CRUSOE_MODEL` | Llama model ID (default: Meta-Llama-3.1-8B-Instruct) |
| `CLAUDE_MODEL` | Claude model ID (default: claude-sonnet-4-6) |
| `ADAPTIVE_THRESHOLD` | Attack count before adaptive tightening (default: 3) |

## Using Mock API (Frontend dev without backend)

Import from `mockApi.js` instead of `api.js` in the components — pre-wired mock responses let Person C build UI independently before the backend is ready.

## Challenge Alignment

| Prize | How |
|-------|-----|
| Security Track | OWASP LLM01 — the #1 AI-enabled threat |
| Best Use of Claude | Deep analysis engine + threat report generation |
| Best Use of Crusoe | High-throughput Tier 1 triage at <500ms |
| Best Use of Data | 4+ sources, 6-category taxonomy, synthetic generation |
| Best Adaptable Agent | Session-level adaptation + confidence recalibration |
| Best Consulting Agent | Consulting-grade threat report on demand |
