from fastapi import FastAPI
from pydantic import BaseModel

from detection.crusoe_tier import PromptFirewall

app = FastAPI(title="PromptGuard")
firewall = PromptFirewall()


class CheckRequest(BaseModel):
    prompt: str


@app.post("/check")
def check(body: CheckRequest) -> dict:
    return firewall.process(body.prompt)
