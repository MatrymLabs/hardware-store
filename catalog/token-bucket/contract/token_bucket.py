"""Contract: token_bucket -- rate limiting by token budget and refill rate.

Language-agnostic in intent, stated here as Python Protocols/signatures. An implementation provides
one validated bucket engine and two consumer shapes:

  check(cost) / consume(cost) -> ThrottleDecision
      The refusal shape. `check` peeks, `consume` takes tokens only when enough are present.
      Denials do not drive the bucket negative; they report `retry_after`.

  reserve(cost) / take(cost) -> float
      The pacing shape. It reserves future tokens and returns the wait seconds before work should
      proceed. A caller that sleeps the returned wait remains at the sustained rate.

  PerTenantRateLimiter.check(key) -> tuple[bool, int]
      A per-key wrapper for HTTP/API boundaries that need an integer Retry-After value.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable

Clock = Callable[[], float]


@runtime_checkable
class ThrottleDecisionContract(Protocol):
    allowed: bool
    tokens_left: float
    retry_after: float
    reason: str


class TokenBucketContract(Protocol):
    rate: float
    capacity: float

    def check(self, cost: float = 1.0) -> ThrottleDecisionContract: ...

    def consume(self, cost: float = 1.0) -> ThrottleDecisionContract: ...

    def try_consume(self, cost: float = 1.0) -> bool: ...

    def reserve(self, cost: float = 1.0) -> float: ...

    def take(self, cost: float = 1.0) -> float: ...

    def retry_after_seconds(self, cost: float = 1.0) -> int: ...


class PerTenantRateLimiterContract(Protocol):
    capacity: float
    refill_per_second: float

    def check(self, key: str, cost: float = 1.0) -> tuple[bool, int]: ...

    def reset(self) -> None: ...
