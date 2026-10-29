from __future__ import annotations

import random
from collections.abc import Sequence
from math import comb


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def bootstrap_ci(
    values: Sequence[float],
    n_resamples: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile bootstrap confidence interval for the mean.

    Resample the per-task values with replacement and take the ``alpha / 2`` and
    ``1 - alpha / 2`` quantiles of the resampled means. The seed makes the
    interval reproducible, so a reported number can be regenerated exactly.
    """
    if not values:
        raise ValueError("values must not be empty")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    rng = random.Random(seed)
    size = len(values)
    means = sorted(_mean(rng.choices(values, k=size)) for _ in range(n_resamples))
    lo = means[int(alpha / 2 * n_resamples)]
    hi = means[min(n_resamples - 1, int((1 - alpha / 2) * n_resamples))]
    return lo, hi


def paired_bootstrap_diff(
    a: Sequence[float],
    b: Sequence[float],
    n_resamples: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, tuple[float, float]]:
    """Mean per-task difference ``a - b`` with a bootstrap interval.

    Pairing matters: both systems are scored on the same tasks, so task
    difficulty cancels in the difference. The paired interval is much narrower
    than comparing two independent intervals.
    """
    if len(a) != len(b):
        raise ValueError("a and b must be the same length")
    diffs = [x - y for x, y in zip(a, b, strict=True)]
    return _mean(diffs), bootstrap_ci(diffs, n_resamples, alpha, seed)


def sign_test(wins_a: int, wins_b: int) -> float:
    """Exact two-sided sign test on tasks where the systems differ.

    Ties carry no information and are excluded. Under the null both systems are
    equally likely to win a task, so the win count is Binomial(n, 0.5). With
    binary outcomes this is McNemar's exact test.
    """
    if wins_a < 0 or wins_b < 0:
        raise ValueError("win counts must be non-negative")
    n = wins_a + wins_b
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(min(wins_a, wins_b) + 1))
    return min(1.0, 2.0 * tail / 2**n)
