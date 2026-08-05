"""Contract tests for token_bucket: deny-style and pacing-style consumers."""

from __future__ import annotations

import math

import pytest
from token_bucket import PerTenantRateLimiter, RateLimitError, TokenBucket


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


def test_a_fresh_bucket_starts_full_and_allows_a_burst() -> None:
    bucket = TokenBucket(rate=1.0, capacity=3.0, clock=_Clock())
    assert bucket.consume().allowed
    assert bucket.consume().allowed
    last = bucket.consume()
    assert last.allowed and last.tokens_left == 0.0
    denied = bucket.consume()
    assert not denied.allowed
    assert denied.retry_after == pytest.approx(1.0)
    assert "rate limit" in denied.reason


def test_it_refills_over_injected_time_without_exceeding_capacity() -> None:
    clock = _Clock()
    bucket = TokenBucket(rate=2.0, capacity=2.0, clock=clock)
    bucket.consume()
    bucket.consume()
    assert not bucket.consume().allowed
    clock.advance(0.5)
    assert bucket.consume().allowed
    clock.advance(100.0)
    assert bucket.tokens_left == 2.0


def test_check_peeks_without_consuming() -> None:
    bucket = TokenBucket(rate=1.0, capacity=1.0, clock=_Clock())
    assert bucket.check().allowed
    assert bucket.check().allowed
    assert bucket.consume().allowed
    assert not bucket.check().allowed


def test_try_consume_is_the_boolean_consumer_shape() -> None:
    bucket = TokenBucket(rate=0.0, capacity=1.0, clock=_Clock())
    assert bucket.try_consume() is True
    assert bucket.try_consume() is False


def test_zero_refill_denies_forever_with_an_infinite_retry_after() -> None:
    bucket = TokenBucket(rate=0.0, capacity=1.0, clock=_Clock())
    bucket.consume()
    denied = bucket.check()
    assert not denied.allowed
    assert math.isinf(denied.retry_after)
    assert bucket.retry_after_seconds() == 3600


def test_reserve_returns_wait_seconds_and_models_backlog() -> None:
    clock = _Clock()
    bucket = TokenBucket(rate=2.0, capacity=1.0, clock=clock)
    assert bucket.reserve() == 0.0
    assert bucket.reserve() == pytest.approx(0.5)
    clock.advance(0.25)
    assert bucket.take() == pytest.approx(0.75)


def test_reserve_can_pace_an_action_larger_than_capacity() -> None:
    bucket = TokenBucket(rate=2.0, capacity=1.0, clock=_Clock())
    assert bucket.reserve(3.0) == pytest.approx(1.0)


def test_reserve_with_no_refill_fails_loud_when_tokens_are_unavailable() -> None:
    bucket = TokenBucket(rate=0.0, capacity=1.0, clock=_Clock())
    bucket.reserve()
    with pytest.raises(RateLimitError, match="rate is zero"):
        bucket.reserve()


@pytest.mark.parametrize("bad", [-1, float("nan"), float("inf"), True])
def test_a_bad_rate_fails_loud(bad: object) -> None:
    with pytest.raises(RateLimitError, match="rate"):
        TokenBucket(rate=bad, capacity=1.0, clock=_Clock())  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True])
def test_a_bad_capacity_fails_loud(bad: object) -> None:
    with pytest.raises(RateLimitError, match="capacity"):
        TokenBucket(rate=1.0, capacity=bad, clock=_Clock())  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [-1.0, float("nan"), float("inf"), True])
def test_a_bad_cost_fails_loud(bad: object) -> None:
    bucket = TokenBucket(rate=1.0, capacity=3.0, clock=_Clock())
    with pytest.raises(RateLimitError, match="cost"):
        bucket.consume(bad)  # type: ignore[arg-type]


def test_consume_refuses_a_cost_that_can_never_fit() -> None:
    bucket = TokenBucket(rate=10.0, capacity=3.0, clock=_Clock())
    with pytest.raises(RateLimitError, match="exceeds capacity"):
        bucket.consume(4.0)


def test_per_tenant_buckets_are_independent_and_resettable() -> None:
    limiter = PerTenantRateLimiter(capacity=1.0, refill_per_second=0.0, clock=_Clock())
    assert limiter.check("tenant-a") == (True, 0)
    assert limiter.check("tenant-a") == (False, 3600)
    assert limiter.check("tenant-b") == (True, 0)
    assert limiter.tenants_tracked == 2
    limiter.reset()
    assert limiter.tenants_tracked == 0
    assert limiter.check("tenant-a") == (True, 0)


def test_per_tenant_retry_after_rounds_up_to_whole_seconds() -> None:
    limiter = PerTenantRateLimiter(capacity=1.0, refill_per_second=0.5, clock=_Clock())
    assert limiter.check("tenant") == (True, 0)
    assert limiter.check("tenant") == (False, 2)
