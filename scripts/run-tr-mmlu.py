#!/usr/bin/env python3
"""
run-tr-mmlu.py — Standalone TR-MMLU runner for YerelAI Benchmark.

Wraps lm-evaluation-harness (EleutherAI) with our env conventions and
emits a JSON record that fits the YerelAI runs schema.

Usage:
    python scripts/run-tr-mmlu.py \\
        --model "alibayram/Trendyol-LLM-Asure-12B" \\
        --runtime ollama-0.6 \\
        --quant q4_k_m \\
        --hardware rtx-3080-10gb \\
        --seed 42 \\
        --output runs/2026-05-24-asure-12b-rtx3080.json

The output JSON is what you paste into your PR (or upload as a gist
and reference via sourceUrl on the YerelAI submission form).

Requirements: see scripts/requirements.txt.

NOTE: lm-eval does not yet support all multi-choice tasks via
chat-completion endpoints (needs logprobs). For Ollama, use the
/v1/completions endpoint (Ollama 0.5+) and the local-completions
backend. This script handles that wiring.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPEATS = 3
SEED_OFFSETS = [0, 17, 41]  # 3 seeds for repetitions


def parse_args():
    p = argparse.ArgumentParser(description="YerelAI TR-MMLU runner")
    p.add_argument("--model", required=True, help="Ollama model tag (e.g. alibayram/Trendyol-LLM-Asure-12B)")
    p.add_argument("--runtime", required=True, choices=["ollama-0.5", "ollama-0.6", "llama-cpp-b4500", "llama-cpp-b4700", "vllm-0.6", "mlx-0.20", "api-direct"])
    p.add_argument("--quant", required=True, choices=["fp16", "fp8", "q8_0", "q6_k", "q5_k_m", "q4_k_m", "q3_k_m", "q2_k", "iq4_xs", "iq3_xs", "api"])
    p.add_argument("--hardware", required=True, help="hardware-id from data/hardware.json (e.g. rtx-3080-10gb)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--repetitions", type=int, default=REPEATS)
    p.add_argument("--endpoint", default="http://localhost:11434/v1")
    p.add_argument("--output", required=True)
    p.add_argument("--submitted-by", default=os.environ.get("USER", "anonymous"))
    p.add_argument("--dataset-version", default="tr-mmlu-2025.05")
    return p.parse_args()


def run_one_seed(args, seed: int) -> float:
    """Run lm-eval once with the given seed. Returns accuracy %."""
    cmd = [
        "lm_eval",
        "--model", "local-completions",
        "--model_args", f"model={args.model},base_url={args.endpoint}/completions,tokenizer_backend=huggingface,num_concurrent=1",
        "--tasks", "turkishmmlu",
        "--num_fewshot", "5",
        "--apply_chat_template", "true",
        "--seed", str(seed),
        "--output_path", f"results-tmp/seed-{seed}.json",
    ]
    print(f"→ run seed={seed} ({args.model})")
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"  ✗ lm_eval failed ({elapsed:.0f}s)")
        print(result.stderr[-2000:])
        sys.exit(1)
    # Parse score from output file
    res_path = Path(f"results-tmp/seed-{seed}.json")
    if not res_path.exists():
        print(f"  ✗ no results file at {res_path}")
        sys.exit(1)
    with open(res_path) as f:
        results = json.load(f)
    # Average across all turkishmmlu subjects (9 dersler)
    subjects = [k for k in results.get("results", {}) if k.startswith("turkishmmlu_")]
    scores = [results["results"][s].get("acc,none", 0) * 100 for s in subjects]
    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"  ✓ accuracy: {avg:.2f}% ({elapsed:.0f}s)")
    return round(avg, 2)


def main():
    args = parse_args()
    os.makedirs("results-tmp", exist_ok=True)
    scores = []
    for i in range(args.repetitions):
        seed = args.seed + SEED_OFFSETS[i % len(SEED_OFFSETS)]
        s = run_one_seed(args, seed)
        scores.append(s)

    record = {
        "id": f"{args.model.split('/')[-1].lower()}-tr-mmlu-{args.hardware}-{args.quant}-{uuid.uuid4().hex[:8]}",
        "modelSlug": args.model.split("/")[-1].lower().replace(".", "-"),
        "dimension": "tr-mmlu",
        "scores": scores,
        "sampleCount": 900,
        "hardware": args.hardware,
        "runtime": args.runtime,
        "quantization": args.quant,
        "contextLength": 4096,
        "seed": args.seed,
        "datasetVersion": args.dataset_version,
        "submittedAt": datetime.now(timezone.utc).isoformat(),
        "submittedBy": args.submitted_by,
        "status": "community",
        "verifications": 0,
        "notes": f"lm-eval 0.4.4, fewshot=5, apply_chat_template=true, seeds={SEED_OFFSETS[:args.repetitions]}",
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Output → {args.output}")
    print(f"  Mean: {sum(scores)/len(scores):.2f}%  (n={len(scores)})")
    print(f"\nNext: open PR or paste into https://yerelai-site.vercel.app/benchmark/gonder")


if __name__ == "__main__":
    main()
