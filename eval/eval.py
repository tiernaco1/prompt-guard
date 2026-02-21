#!/usr/bin/env python3
"""
PromptGuard test runner

Usage examples:
  python test_promptguard.py --base-url http://localhost:8000 --inputs attack.jsonl bengin.jsonl
  python test_promptguard.py --base-url http://localhost:8000 --inputs data/labelled/attack.jsonl --endpoint analyse
  python test_promptguard.py --base-url http://localhost:8000 --inputs attack.jsonl bengin.jsonl --endpoint chat

Outputs:
  - results_<timestamp>.jsonl
  - results_<timestamp>.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests


# ----------------------------
# Utilities
# ----------------------------

def now_stamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    raise ValueError("JSONL line is not an object")
                obj["_source_file"] = os.path.basename(path)
                obj["_source_line"] = i
                rows.append(obj)
            except Exception as e:
                raise ValueError(f"Failed to parse {path}:{i}: {e}") from e
    return rows


def normalize_label(x: Optional[str]) -> Optional[str]:
    if x is None:
        return None
    x = str(x).strip().upper()
    # tolerate minor variants
    if x in {"SAFE", "ALLOW", "PERMIT", "ACCEPT"}:
        return "ALLOW"
    if x in {"BLOCK", "DENY", "REJECT"}:
        return "BLOCK"
    if x in {"SANITIZE", "SANITISE"}:
        return "SANITISE"
    if x in {"SUSPICIOUS", "ATTACK"}:
        # tier1-style labels; not final verdict, but treat as "BLOCK-ish" if used
        return x
    return x


def first_present(d: Dict[str, Any], keys: Iterable[str]) -> Any:
    for k in keys:
        if k in d:
            return d[k]
    return None


def extract_verdict(resp_json: Dict[str, Any]) -> Optional[str]:
    """
    Try to extract the final firewall decision from different plausible response shapes.

    Expected ideal: {"verdict":"BLOCK"/"ALLOW"/"SANITISE", ...}
    But we also handle: {"decision":...}, {"action":...}, {"result":{"verdict":...}}, etc.
    """
    # direct keys
    verdict = first_present(resp_json, ["verdict", "decision", "action", "final", "label"])
    if isinstance(verdict, str):
        return normalize_label(verdict)

    # nested common shapes
    for container_key in ["result", "analysis", "data", "firewall", "output"]:
        container = resp_json.get(container_key)
        if isinstance(container, dict):
            verdict = first_present(container, ["verdict", "decision", "action", "final", "label"])
            if isinstance(verdict, str):
                return normalize_label(verdict)

    # list of messages / steps
    steps = resp_json.get("steps")
    if isinstance(steps, list) and steps:
        # try last step
        last = steps[-1]
        if isinstance(last, dict):
            verdict = first_present(last, ["verdict", "decision", "action", "final", "label"])
            if isinstance(verdict, str):
                return normalize_label(verdict)

    return None


def extract_reason(resp_json: Dict[str, Any]) -> str:
    reason = first_present(resp_json, ["explanation", "reason", "message", "detail"])
    if isinstance(reason, str):
        return reason.strip()
    # nested
    for container_key in ["result", "analysis", "data", "firewall", "output"]:
        container = resp_json.get(container_key)
        if isinstance(container, dict):
            reason = first_present(container, ["explanation", "reason", "message", "detail"])
            if isinstance(reason, str):
                return reason.strip()
    return ""


def safe_preview(text: str, n: int = 140) -> str:
    t = " ".join(str(text).split())
    return t[:n] + ("…" if len(t) > n else "")


# ----------------------------
# Metrics
# ----------------------------

@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0


def confusion_matrix(rows: List[Dict[str, Any]]) -> Dict[Tuple[str, str], int]:
    """
    Matrix indexed by (expected, predicted).
    """
    m: Dict[Tuple[str, str], int] = {}
    for r in rows:
        exp = normalize_label(r.get("expected"))
        pred = normalize_label(r.get("predicted"))
        key = (exp or "UNKNOWN", pred or "UNKNOWN")
        m[key] = m.get(key, 0) + 1
    return m


def binary_counts(rows: List[Dict[str, Any]], positive_label: str) -> Counts:
    """
    Treat `positive_label` as the "positive" class.
    Example: positive_label="BLOCK" to compute precision/recall for BLOCK.
    """
    c = Counts()
    for r in rows:
        exp = normalize_label(r.get("expected"))
        pred = normalize_label(r.get("predicted"))
        if exp is None or pred is None:
            continue

        exp_pos = exp == positive_label
        pred_pos = pred == positive_label

        if exp_pos and pred_pos:
            c.tp += 1
        elif (not exp_pos) and pred_pos:
            c.fp += 1
        elif exp_pos and (not pred_pos):
            c.fn += 1
        else:
            c.tn += 1
    return c


def prf(c: Counts) -> Tuple[float, float, float]:
    precision = c.tp / (c.tp + c.fp) if (c.tp + c.fp) else 0.0
    recall = c.tp / (c.tp + c.fn) if (c.tp + c.fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1


# ----------------------------
# HTTP client
# ----------------------------

def post_json(url: str, payload: Dict[str, Any], timeout_s: float) -> Tuple[int, Dict[str, Any], str]:
    """
    Returns: (status_code, json_dict_or_empty, raw_text)
    """
    r = requests.post(url, json=payload, timeout=timeout_s)
    raw = r.text or ""
    try:
        data = r.json()
        if isinstance(data, dict):
            return r.status_code, data, raw
        # if backend returns a list or something else, wrap it
        return r.status_code, {"_non_dict_json": data}, raw
    except Exception:
        return r.status_code, {}, raw


# ----------------------------
# Runner
# ----------------------------

def run_tests(
    base_url: str,
    endpoint: str,
    inputs: List[str],
    out_dir: str,
    timeout_s: float,
    max_prompts: Optional[int],
    sleep_ms: int,
) -> None:
    if endpoint not in {"analyse", "chat"}:
        raise ValueError("--endpoint must be one of: analyse, chat")

    url = base_url.rstrip("/") + ("/analyse" if endpoint == "analyse" else "/chat")

    # Load prompts
    all_rows: List[Dict[str, Any]] = []
    for p in inputs:
        all_rows.extend(read_jsonl(p))

    if max_prompts is not None:
        all_rows = all_rows[: max_prompts]

    if not all_rows:
        print("No prompts found. Check your .jsonl files.", file=sys.stderr)
        sys.exit(2)

    stamp = now_stamp()
    os.makedirs(out_dir, exist_ok=True)
    out_jsonl = os.path.join(out_dir, f"results_{stamp}.jsonl")
    out_csv = os.path.join(out_dir, f"results_{stamp}.csv")

    print(f"Endpoint: {url}")
    print(f"Loaded {len(all_rows)} prompts from {len(inputs)} file(s)")
    print(f"Writing: {out_jsonl}")
    print(f"Writing: {out_csv}")
    print("Running…\n")

    results: List[Dict[str, Any]] = []
    ok = 0
    bad = 0
    unknown = 0

    for idx, row in enumerate(all_rows, start=1):
        prompt = row.get("prompt")
        expected = normalize_label(row.get("expected"))
        category = row.get("category")

        if not isinstance(prompt, str) or not prompt.strip():
            result = {
                **row,
                "predicted": None,
                "status_code": None,
                "pass": False,
                "error": "Missing/empty prompt field",
            }
            results.append(result)
            bad += 1
            continue

        # Payloads: keep it minimal and compatible
        # /analyse typically expects {"prompt": "..."} or {"input": "..."}
        # /chat might expect {"message": "..."} or {"prompt": "..."}
        payload: Dict[str, Any] = {"prompt": prompt}
        if endpoint == "chat":
            payload = {"message": prompt}

        t0 = time.time()
        try:
            status, data, raw = post_json(url, payload, timeout_s=timeout_s)
            dt_ms = int((time.time() - t0) * 1000)

            predicted = extract_verdict(data)
            reason = extract_reason(data)

            passed = (predicted is not None and expected is not None and predicted == expected)

            if predicted is None:
                unknown += 1

            if passed:
                ok += 1
            else:
                bad += 1

            result = {
                **row,
                "expected": expected,
                "predicted": predicted,
                "pass": passed,
                "latency_ms": dt_ms,
                "status_code": status,
                "reason": reason,
                # keep compact but useful for debugging
                "response_preview": safe_preview(raw, 200),
            }
            results.append(result)

            status_icon = "✅" if passed else ("❓" if predicted is None else "❌")
            print(
                f"[{idx:>3}/{len(all_rows)}] {status_icon} "
                f"exp={expected} pred={predicted} "
                f"cat={category} file={row.get('_source_file')}:{row.get('_source_line')} "
                f"({dt_ms}ms)"
            )

        except requests.RequestException as e:
            dt_ms = int((time.time() - t0) * 1000)
            result = {
                **row,
                "expected": expected,
                "predicted": None,
                "pass": False,
                "latency_ms": dt_ms,
                "status_code": None,
                "error": str(e),
            }
            results.append(result)
            bad += 1
            print(
                f"[{idx:>3}/{len(all_rows)}] ❌ HTTP error ({dt_ms}ms): {e} "
                f"file={row.get('_source_file')}:{row.get('_source_line')}"
            )

        if sleep_ms > 0:
            time.sleep(sleep_ms / 1000.0)

    # Write JSONL
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Write CSV
    csv_fields = [
        "_source_file", "_source_line",
        "category",
        "expected", "predicted", "pass",
        "status_code", "latency_ms",
        "prompt",
        "reason",
        "response_preview",
        "error",
    ]
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for r in results:
            w.writerow({k: r.get(k) for k in csv_fields})

    # Summary
    total = len(results)
    accuracy = ok / total if total else 0.0

    print("\n--- Summary ---")
    print(f"Total:     {total}")
    print(f"Passed:    {ok}")
    print(f"Failed:    {bad}")
    print(f"Unknown:   {unknown}  (no verdict extracted)")
    print(f"Accuracy:  {accuracy:.3f}")

    # Per-label PRF (for BLOCK, ALLOW, SANITISE if present)
    labels_present = sorted({normalize_label(r.get("expected")) for r in results if r.get("expected")})
    for label in ["BLOCK", "ALLOW", "SANITISE"]:
        if label in labels_present:
            c = binary_counts(results, positive_label=label)
            precision, recall, f1 = prf(c)
            print(f"\n{label} metrics (one-vs-rest):")
            print(f"  precision: {precision:.3f}")
            print(f"  recall:    {recall:.3f}")
            print(f"  f1:        {f1:.3f}")
            print(f"  tp/fp/tn/fn: {c.tp}/{c.fp}/{c.tn}/{c.fn}")

    # Confusion matrix (compact)
    m = confusion_matrix(results)
    exp_labels = sorted({k[0] for k in m.keys()})
    pred_labels = sorted({k[1] for k in m.keys()})

    print("\nConfusion matrix (expected x predicted):")
    # header
    header = ["expected\\pred"] + pred_labels
    colw = max(12, max(len(x) for x in header) + 2)
    print("".join(h.ljust(colw) for h in header))
    for e in exp_labels:
        row_cells = [e]
        for p in pred_labels:
            row_cells.append(str(m.get((e, p), 0)))
        print("".join(cell.ljust(colw) for cell in row_cells))

    print(f"\nDone. Results saved to:\n  {out_jsonl}\n  {out_csv}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="PromptGuard backend base URL (default: http://localhost:8000)",
    )
    ap.add_argument(
        "--endpoint",
        choices=["analyse", "chat"],
        default="analyse",
        help="Which endpoint to test (default: analyse)",
    )
    ap.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Input .jsonl files (e.g., attack.jsonl bengin.jsonl)",
    )
    ap.add_argument(
        "--out-dir",
        default="eval_results",
        help="Output directory (default: eval_results)",
    )
    ap.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout seconds per request (default: 20)",
    )
    ap.add_argument(
        "--max-prompts",
        type=int,
        default=None,
        help="Optional cap on number of prompts (for quick smoke tests)",
    )
    ap.add_argument(
        "--sleep-ms",
        type=int,
        default=0,
        help="Optional delay between requests in ms (default: 0)",
    )
    args = ap.parse_args()

    run_tests(
        base_url=args.base_url,
        endpoint=args.endpoint,
        inputs=args.inputs,
        out_dir=args.out_dir,
        timeout_s=args.timeout,
        max_prompts=args.max_prompts,
        sleep_ms=args.sleep_ms,
    )


if __name__ == "__main__":
    main()