import json
import os
import re
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


class PromptFirewall:
    def __init__(self):
        self.session_history = []
        self.attack_patterns = {}  # tracks frequency of attack types
        self.blocked_features = []  # features from confirmed attacks

    def tier1_classify(self, prompt: str) -> str:
        """Crusoe — fast classification, <500ms"""
        _prompt_path = Path(__file__).parent.parent.parent / "data" / "prompts" / "tier1_v1.txt"
        content = _prompt_path.read_text().format(prompt=prompt)
        response = crusoe.chat.completions.create(
            model="NVFP4/Qwen3-235B-A22B-Instruct-2507-FP4",
            messages=[{"role": "user", "content": content}],
            max_tokens=60,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        return response.choices[0].message.content

    def tier2_analyse(self, prompt: str) -> dict:
        """Claude — deep analysis of flagged prompts"""
        _prompt_path = Path(__file__).parent.parent.parent / "data" / "prompts" / "tier2_v1.txt"
        content = _prompt_path.read_text().format(
            total_processed=len(self.session_history),
            attack_patterns=self.attack_patterns,
            recent_history=self.session_history[-5:],
            prompt=prompt,
        )
        response = claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=350,
            messages=[{"role": "user", "content": content}]
        )
        raw = response.content[0].text
        match = re.search(r'\{[\s\S]*\}', raw)
        if not match:
            raise ValueError(f"No JSON in Claude response: {raw[:200]}")
        return json.loads(match.group())

    def process(self, prompt: str) -> dict:
        """Main pipeline — every prompt goes through here"""
        # Tier 1: Fast classification
        tier1_result = self.tier1_classify(prompt)

        if "SAFE" in tier1_result:
            self.session_history.append({"prompt": prompt, "result": "safe"})
            return {"action": "allow", "tier": 1}

        # Tier 2: Deep analysis for suspicious/obvious attacks
        analysis = self.tier2_analyse(prompt)

        # Adapt: update session pattern tracking
        if analysis["verdict"] == "BLOCK":
            attack_type = analysis["attack_type"]
            self.attack_patterns[attack_type] = self.attack_patterns.get(attack_type, 0) + 1

        self.session_history.append({"prompt": prompt, "result": analysis})
        return {"action": analysis["verdict"].lower(), "tier": 2, "analysis": analysis}
