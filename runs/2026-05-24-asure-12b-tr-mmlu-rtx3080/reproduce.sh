#!/usr/bin/env bash
# Reproduce: Trendyol-LLM-Asure-12B on RTX 3080 10GB, Q4_K_M, TR-MMLU.
# Time: ~12 minutes per seed × 3 seeds = ~36 minutes total.

set -euo pipefail

# 1) Ensure Ollama 0.5+
ollama --version | grep -E "0\.[5-9]|[1-9]\." || { echo "Ollama 0.5+ required"; exit 1; }

# 2) Pull model
ollama pull alibayram/Trendyol-LLM-Asure-12B

# 3) Run
cd "$(dirname "$0")/../.."
python scripts/run-tr-mmlu.py \
    --model "alibayram/Trendyol-LLM-Asure-12B" \
    --runtime ollama-0.6 \
    --quant q4_k_m \
    --hardware rtx-3080-10gb \
    --seed 42 \
    --repetitions 3 \
    --output "runs/$(date +%Y-%m-%d)-asure-12b-tr-mmlu-rtx3080/results.json"

echo
echo "✓ Done. Compare your results to: data/runs.jsonl"
echo "  Editor result: scores=[61.8, 62.6, 62.8], mean=62.4, ci95=[60.1, 64.7]"
echo "  Acceptable variance: ±5 points (mean)"
