"""token_bucket -- sustained-rate limiting with burst capacity.

One bucket starts full, holds at most `capacity` tokens, and refills at `rate` tokens per second.
The implementation supports both fleet shapes: `consume` for deny-style rate limits and `reserve`
for pacing boundaries that should wait rather than drop work.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field

Clock = Callable[[], float]


class RateLimitError(ValueError):
    """A token bucket was built or used with impossible settings."""


@dataclass(frozen=True)
class ThrottleDecision:
    """The verdict for one throttled action."""

    allowed: bool
    tokens_left: float
    retry_after: float
    reason: str = ""


def _finite_number(name: str, value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise RateLimitError(f"{name} must be a finite number, got {value!r}")
    number = float(value)
    if not math.isfinite(number):
        raise RateLimitError(f"{name} must be a finite number, got {value!r}")
    return number


def _positive(name: str, value: object) -> float:
    number = _finite_number(name, value)
    if number <= 0:
        raise RateLimitError(f"{name} must be positive, got {value!r}")
    return number


def _non_negative(name: str, value: object) -> float:
    number = _finite_number(name, value)
    if number < 0:
        raise RateLimitError(f"{name} must be non-negative, got {value!r}")
    return number


@dataclass
class TokenBucket:
    """A refilling token bucket. In-memory and not thread-safe by design."""

    rate: float
    capacity: float
    clock: Clock | None = None
    _tokens: float = field(init=False, default=0.0)
    _last: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        self.rate = _non_negative("rate", self.rate)
        self.capacity = _positive("capacity", self.capacity)
        self._clock: Clock = self.clock or time.monotonic
        self._tokens = self.capacity
        self._last = self._clock()

    def _refill(self) -> None:
        now = self._clock()
        elapsed = max(0.0, now - self._last)
        if self.rate > 0 and elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last = now

    def _validate_cost(self, cost: object, *, allow_zero: bool, allow_over_capacity: bool) -> float:
        amount = _finite_number("cost", cost)
        if amount < 0 or (amount == 0 and not allow_zero):
            boundary = "non-negative" if allow_zero else "positive"
            raise RateLimitError(f"cost must be a finite, {boundary} number, got {cost!r}")
        if not allow_over_capacity and amount > self.capacity:
            raise RateLimitError(
                f"cost {amount:g} exceeds capacity {self.capacity:g}; it could never fit"
            )
        return amount

    def check(self, cost: float = 1.0) -> ThrottleDecision:
        """Peek without consuming tokens."""
        amount = self._validate_cost(cost, allow_zero=True, allow_over_capacity=False)
        self._refill()
        if self._tokens >= amount:
            return ThrottleDecision(True, self._tokens, 0.0)
        deficit = amount - self._tokens
        retry_after = math.inf if self.rate == 0 else deficit / self.rate
        return ThrottleDecision(False, self._tokens, retry_after, "rate limit exceeded")

    def consume(self, cost: float = 1.0) -> ThrottleDecision:
        """Take tokens if available; otherwise deny without making the bucket negative."""
        decision = self.check(cost)
        if decision.allowed:
            self._tokens -= cost
            return ThrottleDecision(True, self._tokens, 0.0)
        return decision

    def try_consume(self, cost: float = 1.0) -> bool:
        """Boolean convenience wrapper for boundaries that only need allow/deny."""
        return self.consume(cost).allowed

    def retry_after_seconds(self, cost: float = 1.0, *, no_refill_seconds: int = 3600) -> int:
        """Whole seconds until `cost` tokens are available, suitable for Retry-After."""
        decision = self.check(cost)
        if decision.allowed:
            return 0
        if not math.isfinite(decision.retry_after):
            return no_refill_seconds
        return max(1, math.ceil(decision.retry_after))

    def reserve(self, cost: float = 1.0) -> float:
        """Reserve tokens and return how long the caller should wait before doing the work."""
        amount = self._validate_cost(cost, allow_zero=False, allow_over_capacity=True)
        self._refill()
        if self._tokens >= amount:
            self._tokens -= amount
            return 0.0
        if self.rate == 0:
            raise RateLimitError("cannot reserve unavailable tokens when rate is zero")
        self._tokens -= amount
        return -self._tokens / self.rate

    def take(self, cost: float = 1.0) -> float:
        """Alias for reserve, matching fetch-pacing consumers."""
        return self.reserve(cost)

    @property
    def tokens_left(self) -> float:
        """Current tokens after applying refill."""
        self._refill()
        return self._tokens


@dataclass
class PerTenantRateLimiter:
    """One token bucket per tenant key."""

    capacity: float
    refill_per_second: float
    clock: Clock = time.monotonic
    _buckets: dict[str, TokenBucket] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.capacity = _positive("capacity", self.capacity)
        self.refill_per_second = _non_negative("refill_per_second", self.refill_per_second)

    def _bucket(self, key: str) -> TokenBucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = TokenBucket(
                rate=self.refill_per_second,
                capacity=self.capacity,
                clock=self.clock,
            )
            self._buckets[key] = bucket
        return bucket

    def check(self, key: str, cost: float = 1.0) -> tuple[bool, int]:
        """Consume tokens for `key`; return (allowed, retry_after_seconds)."""
        bucket = self._bucket(key)
        decision = bucket.consume(cost)
        if decision.allowed:
            return True, 0
        return False, bucket.retry_after_seconds(cost)

    def reset(self) -> None:
        """Forget all buckets."""
        self._buckets.clear()

    @property
    def tenants_tracked(self) -> int:
        """How many tenant buckets currently exist."""
        return len(self._buckets)
