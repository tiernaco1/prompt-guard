import json
import os
import re
from collections import deque
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import anthropic

load_dotenv(Path(__file__).parent.parent.parent / ".env")

crusoe = OpenAI(
    base_url="https://hackeurope.crusoecloud.com/v1/",
    api_key=os.environ["CRUSOE_API_KEY"],
)
claude = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])


class SessionState:
    def __init__(self):
        self.total_processed: int = 0
        self.total_blocked: int = 0
        self.blocked_last_5: deque = deque(maxlen=5)
        self.attack_type_counts: dict = {}

    def record_final(self, verdict: str, attack_type: str | None = None) -> None:
        self.total_processed += 1
        blocked = verdict == "BLOCK"
        if blocked:
            self.total_blocked += 1
        self.blocked_last_5.append(blocked)
        if attack_type and attack_type != "none":
            self.attack_type_counts[attack_type] = (
                self.attack_type_counts.get(attack_type, 0) + 1
            )

    def blocked_recent_count(self) -> int:
        return sum(self.blocked_last_5)

    @property
    def session_alert(self) -> bool:
        return self.blocked_recent_count() >= 3


class PromptFirewall:
    def tier1_classify(self, prompt: str) -> str:
        """Crusoe — fast classification, <500ms"""
        _prompt_path = Path(__file__).parent.parent.parent / "data" / "prompts" / "tier1_v1.txt"
        content = _prompt_path.read_text().format(prompt=prompt)
        response = crusoe.chat.completions.create(
            model="NVFP4/Qwen3-235B-A22B-Instruct-2507-FP4",
            messages=[{"role": "user", "content": content}],
            max_tokens=10,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        return response.choices[0].message.content

    def tier2_analyse(self, prompt: str, session: "SessionState") -> dict:
        """Claude — deep analysis of flagged prompts"""
        _prompt_path = Path(__file__).parent.parent.parent / "data" / "prompts" / "tier2_v1.txt"
        content = _prompt_path.read_text().format(
            total_processed=session.total_processed,
            attack_patterns=session.attack_type_counts,
            recent_history=[],
            prompt=prompt,
        )
        response = claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=350,
            messages=[{"role": "user", "content": content}],
        )
        raw = response.content[0].text
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            raise ValueError(f"No JSON in Claude response: {raw[:200]}")
        return json.loads(match.group())

    def _parse_t1_label(self, raw: str) -> str:
        """Extract label from Tier 1 response. Falls back to SUSPICIOUS on failure."""
        raw_upper = raw.strip().upper()
        for label in ("OBVIOUS_ATTACK", "SUSPICIOUS", "SAFE"):
            if label in raw_upper:
                return label
        return "SUSPICIOUS"

    def process(self, prompt: str, session: SessionState) -> dict:
        """Main pipeline — routes through tiers based on session state.

        Routing rules:
          OBVIOUS_ATTACK  → BLOCK  (no Tier 2)
          SAFE + no alert → ALLOW  (no Tier 2)
          SAFE + alert    → Tier 2 verdict
          SUSPICIOUS      → Tier 2 verdict (always)
        """
        # Step 1: Tier 1 classification (parse failures treated as SUSPICIOUS)
        try:
            t1_raw = self.tier1_classify(prompt)
            t1_label = self._parse_t1_label(t1_raw)
        except Exception:
            t1_label = "SUSPICIOUS"

        # Steps 2–4: routing
        if t1_label == "OBVIOUS_ATTACK":
            final_verdict = "BLOCK"
            attack_type = "obvious_attack"
            result = {"action": "block", "tier": 1, "t1_label": t1_label}

        elif t1_label == "SAFE":
            if session.session_alert:
                analysis = self.tier2_analyse(prompt, session)
                final_verdict = analysis["verdict"]
                attack_type = analysis.get("attack_type")
                result = {
                    "action": final_verdict.lower(),
                    "tier": 2,
                    "t1_label": t1_label,
                    "analysis": analysis,
                    "escalation_reason": "session_alert",
                }
            else:
                final_verdict = "ALLOW"
                attack_type = None
                result = {"action": "allow", "tier": 1, "t1_label": t1_label}

        else:  # SUSPICIOUS
            analysis = self.tier2_analyse(prompt, session)
            final_verdict = analysis["verdict"]
            attack_type = analysis.get("attack_type")
            result = {
                "action": final_verdict.lower(),
                "tier": 2,
                "t1_label": t1_label,
                "analysis": analysis,
            }

        # Step 5: record final verdict exactly once
        session.record_final(final_verdict, attack_type)
        return result
