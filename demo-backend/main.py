import os
from pathlib import Path
from typing import Optional

import anthropic
import httpx
from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI(title="PromptGuard Demo Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"],
)

PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:8000")
claude = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])


class ChatRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(
    body: ChatRequest,
    response: Response,
    x_session_id: Optional[str] = Header(None),
    session_id: Optional[str] = Cookie(None),
):
    sid = x_session_id or session_id

    # Forward existing session ID to proxy if we have one
    proxy_headers = {"X-Session-Id": sid} if sid else {}

    # Step 1: Run prompt through PromptGuard proxy
    async with httpx.AsyncClient() as client:
        try:
            proxy_resp = await client.post(
                f"{PROXY_URL}/check",
                json={"prompt": body.prompt},
                headers=proxy_headers,
                timeout=10.0,
            )
            proxy_resp.raise_for_status()
            result = proxy_resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Proxy unreachable: {e}")

    # Forward the session ID the proxy assigned back to the browser
    returned_sid = proxy_resp.headers.get("x-session-id")
    if returned_sid:
        response.headers["X-Session-Id"] = returned_sid
        result["session_id"] = returned_sid

    # Step 2: If allowed, forward to Claude and return its response
    if result["action"] == "allow":
        claude_resp = claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": body.prompt}],
        )
        result["response"] = claude_resp.content[0].text

    return result
