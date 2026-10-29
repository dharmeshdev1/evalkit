import pytest

from evalkit.stats import bootstrap_ci, paired_bootstrap_diff, sign_test


def test_constant_values_give_degenerate_interval():
    assert bootstrap_ci([1.0] * 20) == (1.0, 1.0)


def test_interval_brackets_the_mean_and_is_reasonably_tight():
    values = [0.0, 1.0] * 50
    lo, hi = bootstrap_ci(values)
    assert lo < 0.5 < hi
    assert hi - lo < 0.25


def test_same_seed_is_reproducible_and_different_seed_differs():
    values = [0.1, 0.9, 0.4, 0.6, 0.2, 0.8]
    assert bootstrap_ci(values, seed=3) == bootstrap_ci(values, seed=3)
    assert bootstrap_ci(values, seed=3) != bootstrap_ci(values, seed=4)


def test_fewer_tasks_give_wider_intervals():
    wide = bootstrap_ci([0.0, 1.0] * 5)
    narrow = bootstrap_ci([0.0, 1.0] * 200)
    assert wide[1] - wide[0] > narrow[1] - narrow[0]


def test_bootstrap_rejects_bad_input():
    with pytest.raises(ValueError):
        bootstrap_ci([])
    with pytest.raises(ValueError):
        bootstrap_ci([1.0], alpha=1.5)


def test_paired_diff_detects_consistent_gain():
    a = [0.5 + 0.01 * i for i in range(30)]
    b = [x - 0.1 for x in a]
    diff, (lo, hi) = paired_bootstrap_diff(a, b)
    assert diff == pytest.approx(0.1)
    assert lo > 0 and hi > 0


def test_paired_diff_straddles_zero_for_noise():
    a = [0.1, 0.9, 0.2, 0.8, 0.3, 0.7]
    b = [0.9, 0.1, 0.8, 0.2, 0.7, 0.3]
    _, (lo, hi) = paired_bootstrap_diff(a, b)
    assert lo < 0 < hi


def test_paired_diff_requires_equal_lengths():
    with pytest.raises(ValueError):
        paired_bootstrap_diff([1.0], [1.0, 2.0])


@pytest.mark.parametrize(
    "a,b,expected",
    [(8, 2, 0.109375), (5, 0, 0.0625), (5, 5, 1.0), (0, 0, 1.0), (1, 0, 1.0)],
)
def test_sign_test_known_values(a, b, expected):
    assert sign_test(a, b) == pytest.approx(expected)


def test_sign_test_is_symmetric():
    assert sign_test(9, 3) == sign_test(3, 9)


def test_sign_test_rejects_negative_counts():
    with pytest.raises(ValueError):
        sign_test(-1, 2)
