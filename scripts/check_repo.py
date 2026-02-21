#!/usr/bin/env python3
import json
from pathlib import Path
import sys

def check_jsonl(p):
    p = Path(p)
    if not p.exists():
        print(f"MISSING: {p}")
        return 1
    malformed = 0
    missing_prompt = 0
    missing_expected = 0
    total = 0
    with p.open('r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                obj = json.loads(line)
            except Exception as e:
                malformed += 1
                print(f"{p}:{i} MALFORMED JSON ({e})")
                continue
            if 'prompt' not in obj or not isinstance(obj.get('prompt'), str) or not obj.get('prompt').strip():
                missing_prompt += 1
                print(f"{p}:{i} MISSING/EMPTY 'prompt'")
            if 'expected' not in obj:
                missing_expected += 1
                print(f"{p}:{i} MISSING 'expected'")
    print(f"Checked {p}: total={total} malformed={malformed} missing_prompt={missing_prompt} missing_expected={missing_expected}")
    return 1 if (malformed or missing_prompt) else 0


def main():
    base = Path('.').resolve()
    files = [
        base / 'data' / 'labelled' / 'attacks.jsonl',
        base / 'data' / 'labelled' / 'benign.jsonl',
        base / 'eval' / 'attacks_testing.jsonl',
        base / 'eval' / 'benign_testing.jsonl',
    ]
    errors = 0
    for f in files:
        errors += check_jsonl(f)

    for t in ['data/prompts/tier1_v1.txt', 'data/prompts/tier2_v1.txt']:
        p = Path(t)
        if not p.exists():
            print(f"MISSING: {p}")
            errors += 1
        else:
            s = p.read_text(encoding='utf-8').strip()
            print(f"Checked {p}: size={len(s)} chars")
            if not s:
                print(f"{p} is empty")
                errors += 1

    if errors:
        print('\nJSONL/PROMPTS check completed with issues.')
        sys.exit(2)
    print('\nAll JSONL and prompt files parsed OK.')
    sys.exit(0)

if __name__ == '__main__':
    main()
