#!/usr/bin/env bash
# Reproduce template for run: 2026-05-22-gemini-1-5-pro-tr-mmlu
# See ../README.md for full schema.
# Replace placeholders below with the actual model + hardware + suite for this run.
set -euo pipefail

cd "$(dirname "$0")/../.."
python scripts/run-tr-mmlu.py     --model "MODEL_TAG_HERE"     --runtime "RUNTIME_HERE"     --quant "QUANT_HERE"     --hardware "HARDWARE_ID_HERE"     --seed 42     --repetitions 3     --output "runs/2026-05-22-gemini-1-5-pro-tr-mmlu/results.json"

echo "✓ Compare to: data/runs.jsonl (look up id starting with model+dim)"
