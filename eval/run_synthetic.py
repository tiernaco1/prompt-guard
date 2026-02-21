#!/usr/bin/env python3
"""
Run synthetic attacks through the full firewall pipeline and report per-category detection rates.

Run from project root:
  python eval/run_synthetic.py              # all synthetic data
  python eval/run_synthetic.py --attacks-only   # skip benign edge cases
  python eval/run_synthetic.py --category payload_smuggling  # one category only
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "proxy"))

from detection.crusoe_tier import PromptFirewall

CATEGORIES = [
    "direct_jailbreak",
    "indirect_injection",
    "role_hijacking",
    "payload_smuggling",
    "context_manipulation",
    "information_extraction",
]


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def verdict_matches(expected: str, action: str) -> bool:
    expected_lower = expected.lower()
    if expected_lower == "allow":
        return action == "allow"
    elif expected_lower == "block":
        return action in ("block", "sanitise")
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attacks-only", action="store_true",
                        help="Skip benign edge cases")
    parser.add_argument("--category", type=str, default=None,
                        help="Test only one category (e.g. payload_smuggling)")
    args = parser.parse_args()

    out_dir = PROJECT_ROOT / "data" / "synthetic"

    # Load cases
    if args.category:
        path = out_dir / f"{args.category}.jsonl"
        all_cases = load_jsonl(path)
        if not all_cases:
            print(f"\nNo data found at {path}. Run eval/generate_synthetic.py first.\n")
            return
    else:
        all_cases = load_jsonl(out_dir / "all_attacks.jsonl")
        if not args.attacks_only:
            all_cases += load_jsonl(out_dir / "benign_edge_cases.jsonl")

    if not all_cases:
        print("\nNo synthetic data found. Run eval/generate_synthetic.py first.\n")
        return

    print(f"\nSynthetic Detection Test — {len(all_cases)} prompts")
    print("─" * 60)

    firewall = PromptFirewall()
    by_category: dict[str, dict] = {}
    total_prompts = len(all_cases)

    for i, case in enumerate(all_cases, 1):
        prompt = case["prompt"]
        category = case["category"]
        expected = case.get("expected", "BLOCK")

        print(f"  [{i:>3}/{total_prompts}] {prompt[:65]}", end="\r")

        try:
            result = firewall.process(prompt)
            action = result["action"]
        except Exception as e:
            action = "error"

        if category not in by_category:
            by_category[category] = {"correct": 0, "total": 0, "missed": [], "fp": []}

        by_category[category]["total"] += 1
        correct = verdict_matches(expected, action)

        if correct:
            by_category[category]["correct"] += 1
        else:
            entry = {"prompt": prompt[:100], "expected": expected, "got": action.upper()}
            if expected.upper() == "BLOCK":
                by_category[category]["missed"].append(entry)   # false negative
            else:
                by_category[category]["fp"].append(entry)       # false positive

    print(" " * 80, end="\r")

    # ── Results table ─────────────────────────────────────────────────────────
    print(f"\n{'Category':<28} {'Correct':>8}  {'Rate':>5}  Bar")
    print("═" * 65)

    total_correct = 0
    total_all = 0
    false_negatives = []
    false_positives = []

    for cat in CATEGORIES + ["benign_edge_case"]:
        if cat not in by_category:
            continue
        counts = by_category[cat]
        c, t = counts["correct"], counts["total"]
        total_correct += c
        total_all += t
        pct = 100 * c // t if t else 0
        bar_len = min(t, 20)
        filled = round(pct / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        flag = "  ⚠️" if pct < 85 and cat != "benign_edge_case" else ""
        print(f"  {cat:<26} {c:>4}/{t:<4}  {pct:>3}%  [{bar}]{flag}")
        false_negatives.extend(counts["missed"])
        false_positives.extend(counts["fp"])

    overall = 100 * total_correct // total_all if total_all else 0
    print("═" * 65)
    print(f"  {'OVERALL':<26} {total_correct:>4}/{total_all:<4}  {overall:>3}%")

    # ── Misses ─────────────────────────────────────────────────────────────────
    if false_negatives:
        print(f"\n  ⚠️  FALSE NEGATIVES — attacks that slipped through ({len(false_negatives)}):")
        for entry in false_negatives[:10]:
            print(f"    - {entry['prompt']}")
        if len(false_negatives) > 10:
            print(f"    ... and {len(false_negatives) - 10} more")

    if false_positives:
        print(f"\n  ⚠️  FALSE POSITIVES — benign prompts blocked ({len(false_positives)}):")
        for entry in false_positives[:5]:
            print(f"    - {entry['prompt']}")

    # ── Save results ───────────────────────────────────────────────────────────
    results_path = PROJECT_ROOT / "data" / "synthetic_results.json"
    summary = {
        "total": total_all,
        "correct": total_correct,
        "overall_pct": overall,
        "by_category": {
            cat: {
                "correct": d["correct"],
                "total": d["total"],
                "pct": 100 * d["correct"] // d["total"] if d["total"] else 0,
                "missed": d["missed"],
                "false_positives": d["fp"],
            }
            for cat, d in by_category.items()
        }
    }
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved → data/synthetic_results.json")
    print(f"  Use false negatives to identify prompt weaknesses and iterate.\n")


if __name__ == "__main__":
    main()
