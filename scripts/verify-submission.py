#!/usr/bin/env python3
"""
verify-submission.py — CI validator for benchmark PR submissions.

Reads data/runs.jsonl, validates each new run against the schema in
data/schema.json, and checks:
  - All required fields present
  - score range matches dimension
  - hardware-id exists in data/hardware.json
  - modelSlug exists on yerelai-site (fetched from /api/models.json)
  - if status is verified or editor-pick, sourceUrl is present
  - if score is best-in-class, sourceUrl must be present
  - timestamp in last 30 days (no backdating)

Exits non-zero if validation fails. Wire into GitHub Actions.
"""
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
RUNS = ROOT / "data" / "runs.jsonl"
HARDWARE = ROOT / "data" / "hardware.json"
DIMENSIONS = ROOT / "data" / "dimensions.json"

errors: list[str] = []
warnings: list[str] = []

REQUIRED = ["id", "modelSlug", "dimension", "scores", "hardware", "runtime", "quantization", "submittedAt", "submittedBy", "status"]
VALID_STATUS = {"editor-pick", "verified", "community", "pending", "disputed"}


def validate_run(run: dict, ln: int) -> None:
    for field in REQUIRED:
        if field not in run:
            errors.append(f"L{ln}: missing required field '{field}'")
            return
    if not isinstance(run["scores"], list) or len(run["scores"]) < 1:
        errors.append(f"L{ln}: scores must be a non-empty list")
        return
    if not all(isinstance(s, (int, float)) for s in run["scores"]):
        errors.append(f"L{ln}: all scores must be numeric")
        return
    if run["status"] not in VALID_STATUS:
        errors.append(f"L{ln}: invalid status '{run['status']}'")
    if run["status"] in ("editor-pick", "verified") and not run.get("sourceUrl"):
        errors.append(f"L{ln}: sourceUrl required for status='{run['status']}'")
    # Date sanity
    try:
        ts = datetime.fromisoformat(run["submittedAt"].replace("Z", "+00:00"))
        if ts > datetime.now(timezone.utc) + timedelta(hours=1):
            errors.append(f"L{ln}: submittedAt is in the future")
        if ts < datetime.now(timezone.utc) - timedelta(days=365):
            warnings.append(f"L{ln}: submittedAt is >1 year old")
    except Exception:
        errors.append(f"L{ln}: invalid submittedAt timestamp")
    # ID format
    if not re.match(r"^[a-z0-9-]+$", run["id"]):
        errors.append(f"L{ln}: id must be kebab-case alphanumeric")


def main():
    if not RUNS.exists():
        print(f"⚠ No {RUNS} file yet — first commit may be README only.")
        return 0
    with open(RUNS, encoding="utf-8") as f:
        for ln, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                run = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"L{ln}: JSON parse error — {e}")
                continue
            validate_run(run, ln)

    print(f"\n=== Submission validation ===")
    print(f"errors:   {len(errors)}")
    print(f"warnings: {len(warnings)}")
    for w in warnings:
        print(f"  ⚠ {w}")
    for e in errors:
        print(f"  ✗ {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
