# evalkit

[![ci](https://github.com/dharmeshdev1/evalkit/actions/workflows/ci.yml/badge.svg)](https://github.com/dharmeshdev1/evalkit/actions/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

A small toolkit for reporting model evaluation results honestly. It grades
outputs, computes the unbiased pass@k estimator, puts bootstrap confidence
intervals on every number and compares two systems with paired tests. There are
no runtime dependencies.

## Why this exists

A benchmark score without an interval invites over-reading. Two systems that
differ by three points on sixty tasks may be indistinguishable, and "best of the
first k samples" quietly biases pass@k upward. This project turns the careful
version into one command, so the careful version is also the easy version.

## What is inside

| Piece | What it does |
| --- | --- |
| `pass_at_k(n, c, k)` | Unbiased estimator from Chen et al. (2021), `1 - C(n-c, k) / C(n, k)`, using all `n` samples |
| `bootstrap_ci` | Seeded percentile bootstrap over tasks, so every reported interval is reproducible |
| `paired_bootstrap_diff` | Interval on the per-task difference between two systems on the same tasks |
| `sign_test` | Exact two-sided sign test on the tasks where the systems differ (McNemar's exact test for binary outcomes) |
| Graders | `exact`, `contains`, `regex` and `numeric` (last number in the output, tolerant of thousands separators) |

## Quickstart

```bash
git clone https://github.com/dharmeshdev1/evalkit
cd evalkit
pip install -e ".[dev]"
pytest -q
evalkit report data/system_a.jsonl -k 1 5
```

Input is JSONL with one row per sample, `{"task_id": "t01", "passed": true}`. Tasks
may have different sample counts, but each needs at least `k` samples.

```bash
# pass@k with 95% bootstrap intervals
evalkit report runs.jsonl -k 1 5 10

# paired comparison of two systems on their shared tasks
evalkit compare system_b.jsonl system_a.jsonl -k 1

# turn raw outputs into pass/fail rows
evalkit grade outputs.jsonl --grader numeric
```

## Example: two systems, 60 tasks, 10 samples each

The bundled runs are synthetic and reproducible. `scripts/make_sample_data.py`
regenerates them byte for byte, and a test checks that. system_b is system_a plus a
small uneven improvement.

```
data/system_a.jsonl: 60 tasks, samples per task [10]
  pass@1   0.543  95% CI [0.475, 0.617]
  pass@5   0.908  95% CI [0.860, 0.951]
data/system_b.jsonl: 60 tasks, samples per task [10]
  pass@1   0.585  95% CI [0.518, 0.657]
  pass@5   0.928  95% CI [0.880, 0.967]

$ evalkit compare data/system_b.jsonl data/system_a.jsonl
pass@1 over 60 shared tasks
  system_b 0.585   system_a 0.543
  system_b - system_a = +0.042  95% paired CI [-0.018, +0.097]
  tasks won: system_b 33, system_a 16, tied 11
  sign test p = 0.0213
```

Notice what the two tests say. The unpaired intervals for the two systems overlap heavily,
and the paired interval on the mean gain still includes zero. The sign test is
significant, because system_b wins 33 of the 49 tasks where the systems differ. These
answer different questions. The interval asks how large the average gain is, and it
is sensitive to a few large losses. The sign test asks whether system_b is the better
system on a typical task, and it ignores magnitude. Report both, and say which
claim you are making.

## Design notes

- **Pairing is the main lever.** Both systems face the same tasks, so task
  difficulty cancels in the difference. The paired interval is much narrower than
  comparing two independent ones.
- **The bootstrap resamples tasks, not samples.** Samples of one task are not
  independent draws about the benchmark, so tasks are the unit of replication.
- **Seeds are explicit.** The same file and the same seed give the same interval.
- **Ties are dropped from the sign test.** They carry no information about which
  system is better, and keeping them would inflate the apparent evidence.
- **Graders fail loudly on bad specs.** An invalid regex or a non-numeric expected
  value raises instead of silently scoring zero.
- **The pass@k estimator is checked by simulation.** A test averages random
  subsets and confirms the closed form, in addition to hand-computed cases.

## Limitations and next steps

- Outcomes are binary. Graded scores would need a different per-task statistic.
- The percentile bootstrap can undercover for very small task counts. A BCa
  interval would be a better default below about 30 tasks.
- No multiple-comparison correction when comparing many systems.
- Add a power calculation: how many tasks are needed to detect a given gain.

## Development

```bash
ruff check .
pytest -q
```

CI runs lint, tests and a sample report on Python 3.10 to 3.13.

## License

MIT
