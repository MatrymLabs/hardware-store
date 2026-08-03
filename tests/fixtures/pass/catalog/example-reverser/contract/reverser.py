"""The machine-readable contract every implementation of this Part must satisfy.

Language-agnostic in spirit: any implementation (Python today, another language
tomorrow) must honor this shape and pass the contract suite in ../tests.
"""

from __future__ import annotations

from typing import Protocol


class Reverser(Protocol):
    """Reverse a string; raise TypeError on non-string input."""

    def __call__(self, text: str) -> str: ...
