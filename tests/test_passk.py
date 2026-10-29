import pytest

from evalkit.passk import pass_at_k


def test_pass_at_one_equals_empirical_rate():
    assert pass_at_k(10, 3, 1) == pytest.approx(0.3)


def test_known_value():
    assert pass_at_k(5, 2, 3) == pytest.approx(0.9)  # 1 - C(3,3) / C(5,3)


def test_all_pass_and_none_pass():
    assert pass_at_k(5, 5, 3) == 1.0
    assert pass_at_k(5, 0, 3) == 0.0


def test_k_equal_n_is_one_if_any_pass():
    assert pass_at_k(4, 1, 4) == 1.0


def test_monotonic_in_k():
    values = [pass_at_k(20, 4, k) for k in range(1, 21)]
    assert values == sorted(values)


def test_more_passes_never_hurts():
    assert pass_at_k(10, 5, 3) > pass_at_k(10, 2, 3)


@pytest.mark.parametrize("n,c,k", [(0, 0, 1), (5, 2, 0), (5, 2, 6), (5, 6, 1), (5, -1, 1)])
def test_invalid_arguments(n, c, k):
    with pytest.raises(ValueError):
        pass_at_k(n, c, k)


def test_unbiased_by_simulation():
    """Averaging over random subsets of size k recovers the closed form."""
    import random

    rng = random.Random(1)
    outcomes = [True] * 3 + [False] * 7
    trials = 20000
    hits = sum(any(rng.sample(outcomes, 4)) for _ in range(trials))
    assert hits / trials == pytest.approx(pass_at_k(10, 3, 4), abs=0.01)
