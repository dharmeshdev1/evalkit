from __future__ import annotations

import json
from pathlib import Path

from evalkit.graders import GRADERS
from evalkit.passk import pass_at_k
from evalkit.stats import bootstrap_ci


def load_samples(path: str | Path) -> dict[str, list[bool]]:
    """Read JSONL rows of ``{"task_id", "passed"}`` into per-task sample outcomes."""
    samples: dict[str, list[bool]] = {}
    for lineno, line in enumerate(Path(path).read_text().splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row.get("passed"), bool) or "task_id" not in row:
            raise ValueError(f"{path}:{lineno}: need a task_id and a boolean passed")
        samples.setdefault(str(row["task_id"]), []).append(row["passed"])
    if not samples:
        raise ValueError(f"{path}: no samples found")
    return samples


def per_task_pass_at_k(samples: dict[str, list[bool]], k: int) -> dict[str, float]:
    out: dict[str, float] = {}
    for task, outcomes in samples.items():
        if len(outcomes) < k:
            raise ValueError(f"task {task!r} has {len(outcomes)} samples, fewer than k={k}")
        out[task] = pass_at_k(len(outcomes), sum(outcomes), k)
    return out


def summarize(
    samples: dict[str, list[bool]], ks: list[int], seed: int = 0
) -> dict[int, tuple[float, tuple[float, float]]]:
    """Mean pass@k over tasks with a bootstrap interval, for each k."""
    summary = {}
    for k in ks:
        values = list(per_task_pass_at_k(samples, k).values())
        summary[k] = (sum(values) / len(values), bootstrap_ci(values, seed=seed))
    return summary


def grade_rows(rows: list[dict], grader: str) -> list[dict]:
    """Attach a ``passed`` field to each ``{"task_id", "output", "expected"}`` row."""
    if grader not in GRADERS:
        raise ValueError(f"unknown grader {grader!r}; choose from {sorted(GRADERS)}")
    fn = GRADERS[grader]
    return [
        {"task_id": r["task_id"], "passed": fn(str(r["output"]), str(r["expected"]))} for r in rows
    ]
