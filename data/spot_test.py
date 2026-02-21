#!/usr/bin/env python3
"""
Spot-test the PromptFirewall against labelled test prompts.

Sources:
  - eval/attacks_testing.jsonl   (hand-written attacks, 6 categories)
  - eval/benign_testing.jsonl    (hand-written benign)
  - data/labelled/attacks.jsonl  (HuggingFace deepset/prompt-injections, sampled)
  - data/labelled/benign.jsonl   (HuggingFace fka/awesome-chatgpt-prompts, sampled)

Run from project root:
  python data/spot_test.py
"""

import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "proxy"))

from detection.crusoe_tier import PromptFirewall


# ── Data loading ─────────────────────────────────────────────────────────────

def load_jsonl(path: Path) -> list[dict]:
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


# ── Verdict comparison ────────────────────────────────────────────────────────

def verdict_matches(expected: str, action: str) -> bool:
    """ALLOW → only 'allow' passes. BLOCK → 'block' or 'sanitise' both pass."""
    expected_lower = expected.lower()
    if expected_lower == "allow":
        return action == "allow"
    elif expected_lower == "block":
        return action in ("block", "sanitise")
    return False


# ── Test runner ───────────────────────────────────────────────────────────────

def run_tests(test_cases: list[dict], firewall: PromptFirewall) -> list[dict]:
    results = []
    total = len(test_cases)
    for i, case in enumerate(test_cases, 1):
        prompt = case["prompt"]
        expected = case.get("expected", "ALLOW")
        category = case.get("category", "unknown")

        print(f"  [{i:>3}/{total}] {prompt[:70]}", end="\r")

        try:
            result = firewall.process(prompt)
            action = result["action"]
            tier = result["tier"]
            correct = verdict_matches(expected, action)

            results.append({
                "prompt": prompt,
                "category": category,
                "expected": expected,
                "got": action.upper(),
                "tier": tier,
                "correct": correct,
                "analysis": result.get("analysis", {}),
            })
        except Exception as e:
            results.append({
                "prompt": prompt,
                "category": category,
                "expected": expected,
                "got": "ERROR",
                "tier": 0,
                "correct": False,
                "error": str(e),
            })

    print(" " * 90, end="\r")  # clear progress line
    return results


# ── Output ────────────────────────────────────────────────────────────────────

def print_results_table(results: list[dict]):
    col_prompt = 55
    col_cat = 26
    col_exp = 8
    col_got = 10
    width = col_prompt + col_cat + col_exp + col_got + 12

    print(f"\n{'─' * width}")
    print(
        f"{'Prompt':<{col_prompt}} {'Category':<{col_cat}} "
        f"{'Expect':<{col_exp}} {'Got':<{col_got}} {'T'}  {'OK?'}"
    )
    print(f"{'─' * width}")

    for r in results:
        short = r["prompt"][:col_prompt - 3] + "..." if len(r["prompt"]) > col_prompt else r["prompt"]
        ok = "✅" if r["correct"] else "❌"
        print(
            f"{short:<{col_prompt}} {r['category']:<{col_cat}} "
            f"{r['expected']:<{col_exp}} {r['got']:<{col_got}} {r['tier']}  {ok}"
        )

    print(f"{'─' * width}")


def print_summary(results: list[dict]):
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    errors = [r for r in results if r.get("got") == "ERROR"]
    misses = [r for r in results if not r["correct"] and r.get("got") != "ERROR"]
    false_negatives = [r for r in misses if r["expected"] == "BLOCK"]
    false_positives = [r for r in misses if r["expected"] == "ALLOW"]

    # Per-category breakdown
    by_category: dict[str, dict] = {}
    for r in results:
        cat = r["category"]
        if cat not in by_category:
            by_category[cat] = {"correct": 0, "total": 0}
        by_category[cat]["total"] += 1
        if r["correct"]:
            by_category[cat]["correct"] += 1

    pct = 100 * correct // total if total else 0
    print(f"\n{'═' * 60}")
    print(f"  RESULTS SUMMARY")
    print(f"{'═' * 60}")
    print(f"  Total:           {total}")
    print(f"  Correct:         {correct}  ({pct}%)")
    print(f"  Misses:          {len(misses)}")
    print(f"    ↳ False negatives (attacks missed): {len(false_negatives)}")
    print(f"    ↳ False positives (benign blocked): {len(false_positives)}")
    if errors:
        print(f"  Errors:          {len(errors)}")

    print(f"\n  By category:")
    for cat, counts in sorted(by_category.items()):
        c, t = counts["correct"], counts["total"]
        cat_pct = 100 * c // t if t else 0
        bar = "✅" * c + "❌" * (t - c)
        print(f"    {cat:<28} {c}/{t}  ({cat_pct:>3}%)  {bar}")

    if false_negatives:
        print(f"\n  ⚠️  FALSE NEGATIVES — attacks that slipped through:")
        for r in false_negatives:
            print(f"    [{r['category']}] {r['prompt'][:90]}")

    if false_positives:
        print(f"\n  ⚠️  FALSE POSITIVES — benign prompts that were blocked:")
        for r in false_positives:
            print(f"    [{r['category']}] {r['prompt'][:90]}")

    if errors:
        print(f"\n  ❗ ERRORS:")
        for r in errors:
            print(f"    [{r['category']}] {r['prompt'][:60]} → {r.get('error', '')}")

    print(f"{'═' * 60}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    random.seed(42)  # reproducible sampling

    # Hand-written test cases
    eval_attacks = load_jsonl(PROJECT_ROOT / "eval" / "attacks_testing.jsonl")
    eval_benign  = load_jsonl(PROJECT_ROOT / "eval" / "benign_testing.jsonl")

    # HuggingFace downloaded data (sampled to keep cost reasonable)
    hf_attacks = load_jsonl(PROJECT_ROOT / "data" / "labelled" / "attacks.jsonl")
    hf_benign  = load_jsonl(PROJECT_ROOT / "data" / "labelled" / "benign.jsonl")

    hf_attack_sample = random.sample(hf_attacks, min(20, len(hf_attacks)))
    hf_benign_sample = random.sample(hf_benign,  min(20, len(hf_benign)))

    all_cases = eval_attacks + eval_benign + hf_attack_sample + hf_benign_sample

    print(f"\nPromptGuard — Spot Test")
    print(f"{'─' * 60}")
    print(f"  Hand-written attacks : {len(eval_attacks)}")
    print(f"  Hand-written benign  : {len(eval_benign)}")
    print(f"  HuggingFace attacks  : {len(hf_attack_sample)}  (sampled from {len(hf_attacks)})")
    print(f"  HuggingFace benign   : {len(hf_benign_sample)}  (sampled from {len(hf_benign)})")
    print(f"  ─────────────────────")
    print(f"  Total                : {len(all_cases)}")
    print(f"{'─' * 60}")
    print(f"\nRunning... (each flagged prompt makes 2 API calls)\n")

    firewall = PromptFirewall()
    results = run_tests(all_cases, firewall)

    print_results_table(results)
    print_summary(results)

    # Save results for iteration tracking
    out_path = PROJECT_ROOT / "data" / "spot_test_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  Full results saved → data/spot_test_results.json")
    print(f"  Use these results to identify patterns in misses and iterate on prompts.\n")


if __name__ == "__main__":
    main()
