#!/usr/bin/env python3
"""
PromptGuard Evaluation Runner

Default behaviour:
  - Tests attack_testing.jsonl + benign_testing.jsonl
  - Uses /analyse endpoint
  - Saves JSONL + CSV results
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests


# ---------------------------------------------------
# Utility helpers
# ---------------------------------------------------

def timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def read_jsonl(path: str) -> List[Dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if not line.strip():
                continue
            obj = json.loads(line)
            obj["_file"] = os.path.basename(path)
            obj["_line"] = i
            rows.append(obj)
    return rows


def normalize(label: Optional[str]) -> Optional[str]:
    if not label:
        return None
    label = label.strip().upper()
    if label in {"SAFE", "ALLOW", "PERMIT"}:
        return "ALLOW"
    if label in {"BLOCK", "DENY", "REJECT"}:
        return "BLOCK"
    if label in {"SANITIZE", "SANITISE"}:
        return "SANITISE"
    return label


def extract_verdict(resp: Dict) -> Optional[str]:
    """
    Expected ideal response:
        { "verdict": "BLOCK" }
    """

    # Direct field
    if "verdict" in resp:
        return normalize(resp["verdict"])

    # Common nested structures
    for key in ["result", "analysis", "firewall"]:
        if key in resp and isinstance(resp[key], dict):
            if "verdict" in resp[key]:
                return normalize(resp[key]["verdict"])

    return None


# ---------------------------------------------------
# Metrics
# ---------------------------------------------------

@dataclass
class Metrics:
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0


def compute_binary_metrics(rows: List[Dict], positive="BLOCK") -> Metrics:
    m = Metrics()
    for r in rows:
        exp = normalize(r.get("expected"))
        pred = normalize(r.get("predicted"))

        if exp is None or pred is None:
            continue

        if exp == positive and pred == positive:
            m.tp += 1
        elif exp != positive and pred == positive:
            m.fp += 1
        elif exp == positive and pred != positive:
            m.fn += 1
        else:
            m.tn += 1
    return m


def precision_recall_f1(m: Metrics) -> Tuple[float, float, float]:
    precision = m.tp / (m.tp + m.fp) if (m.tp + m.fp) else 0
    recall = m.tp / (m.tp + m.fn) if (m.tp + m.fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0
    return precision, recall, f1


# ---------------------------------------------------
# Runner
# ---------------------------------------------------

def run(base_url: str, endpoint: str, inputs: List[str], timeout: float):
    url = base_url.rstrip("/") + f"/{endpoint}"

    prompts = []
    for file in inputs:
        prompts.extend(read_jsonl(file))

    if not prompts:
        print("No prompts found.")
        sys.exit(1)

    print(f"\nTesting {len(prompts)} prompts against {url}\n")

    results = []
    passed = 0

    for i, row in enumerate(prompts, start=1):
        if "prompt" not in row or not isinstance(row["prompt"], str) or not row["prompt"].strip():
            print(f"[{i:03}] ❌ Missing/empty 'prompt' field in {row.get('_file')}:{row.get('_line')}")
            results.append({**row, "predicted": None, "pass": False, "error": "Missing/empty prompt"})
            continue

        payload = {"prompt": row["prompt"]}

        start = time.time()
        try:
            r = requests.post(url, json=payload, timeout=timeout)
            latency = int((time.time() - start) * 1000)

            # NEW: show non-200 responses clearly
            if r.status_code != 200:
                body_preview = (r.text or "")[:200].replace("\n", " ")
                print(f"[{i:03}] ❌ Non-200 status: {r.status_code} body={body_preview!r}")

            # Try to parse JSON even if non-200 (helps debug)
            try:
                data = r.json()
            except Exception:
                data = {}
                print(f"[{i:03}] ❌ Response was not JSON. body={(r.text or '')[:200]!r}")

            predicted = extract_verdict(data)
            expected = normalize(row.get("expected"))

            # NEW: fail fast / visibility if verdict is missing
            if predicted is None:
                print(f"[{i:03}] ❓ Could not extract verdict. Response keys: {list(data.keys())}")

            success = (predicted is not None and expected is not None and predicted == expected)
            if success:
                passed += 1

            results.append({
                **row,
                "predicted": predicted,
                "latency_ms": latency,
                "status_code": r.status_code,
                "pass": success,
            })

            icon = "✅" if success else ("❓" if predicted is None else "❌")
            print(f"[{i:03}/{len(prompts)}] {icon} "
                  f"exp={expected} pred={predicted} "
                  f"({latency}ms)")

        except Exception as e:
            print(f"[{i:03}] ❌ ERROR: {e}")
            results.append({**row, "predicted": None, "pass": False, "error": str(e)})

    if not results:
        print("No results produced.")
        sys.exit(1)

    accuracy = passed / len(results)

    # Metrics
    block_metrics = compute_binary_metrics(results, positive="BLOCK")
    p, r, f1 = precision_recall_f1(block_metrics)

    print("\n--- RESULTS ---")
    print(f"Accuracy:        {accuracy:.3f}")
    print(f"BLOCK Precision: {p:.3f}")
    print(f"BLOCK Recall:    {r:.3f}")
    print(f"BLOCK F1:        {f1:.3f}")

    # Save results
    os.makedirs("eval_results", exist_ok=True)
    stamp = timestamp()

    json_path = f"eval_results/results_{stamp}.jsonl"
    csv_path = f"eval_results/results_{stamp}.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row) + "\n")

    # CSV: use a stable superset of fields so missing keys don't break writing
    fieldnames = set()
    for rrow in results:
        fieldnames.update(rrow.keys())
    fieldnames = sorted(fieldnames)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved to:")
    print(f"  {json_path}")
    print(f"  {csv_path}")


# ---------------------------------------------------
# CLI
# ---------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--endpoint", default="analyse", choices=["analyse", "chat"])
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--inputs",
        nargs="+",
        default=["eval/attacks_testing.jsonl", "eval/benign_testing.jsonl"],
    )
    args = parser.parse_args()

    run(args.base_url, args.endpoint, args.inputs, args.timeout)


if __name__ == "__main__":
    main()