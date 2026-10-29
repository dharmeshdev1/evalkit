from __future__ import annotations

from math import comb


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator from Chen et al. (2021).

    Given ``n`` samples of which ``c`` passed, this is the probability that at
    least one of ``k`` samples drawn without replacement passes:
    ``1 - C(n - c, k) / C(n, k)``. It is unbiased, unlike the common shortcut of
    taking the best of the first ``k`` samples, and it uses every sample.
    """
    if n < 1 or k < 1:
        raise ValueError("n and k must be at least 1")
    if k > n:
        raise ValueError(f"k={k} exceeds the number of samples n={n}")
    if not 0 <= c <= n:
        raise ValueError(f"c={c} must be between 0 and n={n}")
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)
