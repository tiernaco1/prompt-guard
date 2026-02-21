from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from detection.crusoe_tier import PromptFirewall

app = FastAPI(title="PromptGuard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

firewall = PromptFirewall()


class CheckRequest(BaseModel):
    prompt: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check")
def check(body: CheckRequest) -> dict:
    return firewall.process(body.prompt)
