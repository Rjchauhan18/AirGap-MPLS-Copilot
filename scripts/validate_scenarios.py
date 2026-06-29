#!/usr/bin/env python3
"""
Hackathon-friendly validation harness.

Goal
----
Produce a lightweight, reproducible artifact under output/validation/
showing:
- number of incidents generated
- presence of ground-truth labels file (if available)

This is intentionally minimal to avoid over-engineering during hackathon.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INCIDENTS_DIR = ROOT / "output" / "incidents"
VALIDATION_DIR = ROOT / "output" / "validation"
LABELS_FILE = ROOT / "Model" / "ml_ground_truth_labels_TEST.csv"


def main() -> int:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    incidents = []
    if INCIDENTS_DIR.exists():
        for p in sorted(INCIDENTS_DIR.glob("*.json")):
            try:
                incidents.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                continue

    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "incidents_count": len(incidents),
        "labels_file_present": LABELS_FILE.exists(),
        "labels_file_path": str(LABELS_FILE),
        "notes": [
            "This validation artifact is a hackathon baseline.",
            "Extend with precision/recall/lead-time scoring once labels+telemetry alignment is finalized.",
        ],
    }

    out = VALIDATION_DIR / "validation_summary.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

