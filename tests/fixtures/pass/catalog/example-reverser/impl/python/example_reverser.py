"""example_reverser -- a fixture implementation, not real catalog content.

It exists only so store_check has a well-formed CANDIDATE Part to pass, and a
target its sabotage tests can break. Real Parts arrive via R&D certification.
"""

from __future__ import annotations


def reverse(text: str) -> str:
    """Return ``text`` reversed. Fails loud and early on non-string input."""
    if not isinstance(text, str):
        raise TypeError("reverse expects a str")
    return text[::-1]
