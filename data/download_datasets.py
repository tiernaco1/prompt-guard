import json
import os
from datasets import load_dataset

# Create folders
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/labelled", exist_ok=True)
os.makedirs("data/prompts", exist_ok=True)

# --- ATTACKS: deepset/prompt-injections ---
# label: 1 = injection, 0 = safe
# column: "text"
print("Downloading deepset/prompt-injections...")
ds_injections = load_dataset("deepset/prompt-injections", split="train")

attack_count = 0
with open("data/labelled/attacks.jsonl", "w", encoding="utf-8") as f:
    for row in ds_injections:
        if row["label"] == 1:
            entry = {
                "prompt": row["text"],
                "category": "uncategorised",
                "source": "deepset/prompt-injections",
                "expected": "BLOCK"
            }
            f.write(json.dumps(entry) + "\n")
            attack_count += 1

print(f"Attacks written: {attack_count}")

# --- BENIGN: fka/awesome-chatgpt-prompts ---
# column: "prompt" (all legitimate use cases)
print("Downloading fka/awesome-chatgpt-prompts...")
ds_benign = load_dataset("fka/awesome-chatgpt-prompts", split="train")

benign_count = 0
with open("data/labelled/benign.jsonl", "w", encoding="utf-8") as f:
    for row in ds_benign:
        entry = {
            "prompt": row["prompt"],
            "category": "benign",
            "source": "fka/awesome-chatgpt-prompts",
            "expected": "ALLOW"
        }
        f.write(json.dumps(entry) + "\n")
        benign_count += 1

print(f"Benign written: {benign_count}")
print("data/prompts/ folder created.")
print("\nDone!")
