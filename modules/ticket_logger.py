"""
ticket_logger.py
------------------
Writes every diagnostic run to a CSV "ticket log", mimicking a
helpdesk ticket history. Makes the tool's output auditable, which
matters in a real IT support environment.
"""

import csv
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_output")
LOG_PATH = os.path.join(LOG_DIR, "ticket_log.csv")
FIELDNAMES = ["timestamp", "check_type", "target", "summary"]


def _summarize(result: dict) -> str:
    parts = []
    for key, value in result.items():
        if key in ("raw_output", "hops"):
            continue
        parts.append(f"{key}={value}")
    return "; ".join(parts)[:200]


def log_result(check_type: str, target: str, result: dict) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)

    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "check_type": check_type,
            "target": target,
            "summary": _summarize(result),
        })
