"""Contract for a durable record that an opaque operation has been applied once.

``seen(key)`` is an advisory read. ``claim(key)`` is the atomic guard: it returns True for the
caller that first records the key, and False for every later caller. Implementations must retain
that record beyond the lifetime of an individual store object.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class KeyRefused(ValueError):
    """Raised when a key cannot name a record that can later be looked up."""


@runtime_checkable
class AppliedOnce(Protocol):
    """The minimal durable exactly-once record surface."""

    def seen(self, key: str) -> bool:
        """Return whether ``key`` has already been claimed.

        This read is not a guard and may be stale under a race. It raises ``KeyRefused`` for an
        empty key.
        """
        ...

    def claim(self, key: str) -> bool:
        """Atomically record ``key`` if absent.

        Return True only for the caller that created the durable record. Return False when the
        record already exists. It raises ``KeyRefused`` for an empty key.
        """
        ...
