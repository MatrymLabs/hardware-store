"""Contract conformance for example_reverser. Acceptance AND refusal cases.

store_check runs this suite as-is (CMD: pytest) against the listed implementation.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "impl" / "python"))

from example_reverser import reverse  # noqa: E402


def test_reverses_plain_text() -> None:
    assert reverse("abc") == "cba"


def test_empty_string_is_identity() -> None:
    assert reverse("") == ""


def test_hostile_mixed_case_and_symbols() -> None:
    # Fleet law: test data must include hostile cases.
    assert reverse("Ab!9_Z") == "Z_9!bA"


def test_refuses_non_string() -> None:
    for bad in (None, 123, ["a"]):
        try:
            reverse(bad)  # type: ignore[arg-type]
        except TypeError:
            continue
        raise AssertionError(f"reverse should refuse {bad!r}")
