"""Generate the bundled sample runs. Deterministic: rerunning reproduces data/ exactly.

Each task has its own difficulty. System B is system A with a small, uneven
improvement, so the comparison has a real but modest effect to detect.
"""

import json
import random
from pathlib import Path

N_TASKS = 60
N_SAMPLES = 10
OUT = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    rng = random.Random(7)
    base = [rng.betavariate(2.0, 2.0) for _ in range(N_TASKS)]
    boost = [max(0.0, rng.gauss(0.06, 0.08)) for _ in range(N_TASKS)]
    improved = [min(1.0, p + d) for p, d in zip(base, boost, strict=True)]
    systems = {"system_a": base, "system_b": improved}
    for name, probs in systems.items():
        lines = []
        for t, p in enumerate(probs):
            for _ in range(N_SAMPLES):
                lines.append(json.dumps({"task_id": f"t{t:02d}", "passed": rng.random() < p}))
        (OUT / f"{name}.jsonl").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
