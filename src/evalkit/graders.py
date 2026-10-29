from __future__ import annotations

import math
import re
from collections.abc import Callable

_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split()).rstrip(".")


def exact_match(output: str, expected: str) -> bool:
    """Equal after case folding, whitespace collapsing and dropping a final period."""
    return _normalize(output) == _normalize(expected)


def contains(output: str, expected: str) -> bool:
    return _normalize(expected) in _normalize(output)


def regex_match(output: str, expected: str) -> bool:
    """``expected`` is a regular expression searched anywhere in the output."""
    try:
        return re.search(expected, output) is not None
    except re.error as exc:
        raise ValueError(f"invalid regex {expected!r}: {exc}") from exc


def numeric_close(output: str, expected: str, rel_tol: float = 1e-6) -> bool:
    """Compare the last number in the output to the expected number.

    The last number is used because answers usually follow the working, as in
    "3 * 4 = 12, so the answer is 12". Thousands separators are ignored.
    """
    found = _NUMBER.findall(output)
    if not found:
        return False
    try:
        want = float(expected.replace(",", ""))
    except ValueError as exc:
        raise ValueError(f"expected value {expected!r} is not a number") from exc
    return math.isclose(float(found[-1].replace(",", "")), want, rel_tol=rel_tol, abs_tol=1e-9)


GRADERS: dict[str, Callable[[str, str], bool]] = {
    "exact": exact_match,
    "contains": contains,
    "regex": regex_match,
    "numeric": numeric_close,
}
