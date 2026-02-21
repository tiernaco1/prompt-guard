import uuid
from typing import Optional

from fastapi import Cookie, FastAPI, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from detection.crusoe_tier import PromptFirewall, SessionState

app = FastAPI(title="PromptGuard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

firewall = PromptFirewall()
sessions: dict[str, SessionState] = {}


def _get_or_create_session(session_id: Optional[str]) -> tuple[str, SessionState]:
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]
    sid = session_id or str(uuid.uuid4())
    sessions[sid] = SessionState()
    return sid, sessions[sid]


class CheckRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check")
def check(
    body: CheckRequest,
    response: Response,
    x_session_id: Optional[str] = Header(None),
    session_id: Optional[str] = Cookie(None),
):
    sid, session = _get_or_create_session(x_session_id or session_id)
    response.headers["X-Session-Id"] = sid
    response.set_cookie("session_id", sid)
    return firewall.process(body.prompt, session)


@app.get("/session/stats")
def session_stats(
    x_session_id: Optional[str] = Header(None),
    session_id: Optional[str] = Cookie(None),
):
    sid = x_session_id or session_id
    if not sid or sid not in sessions:
        return JSONResponse(status_code=404, content={"error": "session not found"})
    s = sessions[sid]
    return {
        "total_processed": s.total_processed,
        "total_blocked": s.total_blocked,
        "blocked_last_5": list(s.blocked_last_5),
        "blocked_recent_count": s.blocked_recent_count(),
        "session_alert": s.session_alert,
    }
