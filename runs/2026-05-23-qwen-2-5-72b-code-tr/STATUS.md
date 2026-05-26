# Status: results.json pending

Aggregated scores for this configuration live in [`data/runs.jsonl`](../../data/runs.jsonl).

Raw per-seed log will be committed to `results.json` when a maintainer
re-runs this configuration on the listed hardware. Until then:

- The aggregate is editor-attested but not byte-replayable.
- To accelerate, run `./reproduce.sh` (fill in placeholders) and open a PR.
- We accept any matching run within ±5 points (mean) as cross-verification.
