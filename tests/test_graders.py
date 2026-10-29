import pytest

from evalkit.graders import GRADERS, contains, exact_match, numeric_close, regex_match


def test_exact_match_normalizes_case_space_and_final_period():
    assert exact_match("  The  Answer. ", "the answer")
    assert not exact_match("the answers", "the answer")


def test_contains():
    assert contains("Final answer: Paris, France", "paris")
    assert not contains("London", "paris")


def test_regex_match_and_invalid_pattern():
    assert regex_match("order #4521 shipped", r"#\d{4}")
    with pytest.raises(ValueError):
        regex_match("x", "(")


@pytest.mark.parametrize(
    "output,expected,ok",
    [
        ("3 * 4 = 12, so the answer is 12.", "12", True),
        ("The total is 1,250 dollars", "1250", True),
        ("about 7", "8", False),
        ("no digits at all", "5", False),
        ("-3.5", "-3.5", True),
        ("result 0.30000000000000004", "0.3", True),
    ],
)
def test_numeric_close(output, expected, ok):
    assert numeric_close(output, expected) is ok


def test_numeric_uses_the_last_number_not_the_first():
    assert not numeric_close("12 apples became 13", "12")


def test_numeric_bad_expected_value_is_an_error():
    with pytest.raises(ValueError):
        numeric_close("5", "five")


def test_registry_contains_every_grader():
    assert set(GRADERS) == {"exact", "contains", "regex", "numeric"}
