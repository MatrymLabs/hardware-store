"""Contract tests for the circuit_breaker Part: the three-state machine + the call runner.

Acceptance: CLOSED trips to OPEN at the failure threshold; OPEN fast-fails; after the reset timeout
it goes HALF_OPEN and allows one probe; a probe success closes it, a probe failure re-opens it;
call() runs/rejects and records the outcome.

Refusal / hostile: an invalid construction fails loud; call() on an open breaker raises CircuitOpen
without running fn; a failing fn is recorded then re-raised (never swallowed).
"""

from __future__ import annotations

import pytest
from circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitOpen,
)


class _Clock:
    """A hand-driven monotonic clock: tests advance time explicitly, no real waiting."""

    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


# --- construction: fail loud ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"failure_threshold": 0, "reset_timeout": 1.0}, "failure_threshold"),
        ({"failure_threshold": True, "reset_timeout": 1.0}, "failure_threshold"),  # bool != int
        ({"failure_threshold": 1.5, "reset_timeout": 1.0}, "failure_threshold"),  # float != int
        ({"failure_threshold": 2, "reset_timeout": -1.0}, "reset_timeout"),
        ({"failure_threshold": 2, "reset_timeout": float("inf")}, "reset_timeout"),
    ],
)
def test_an_invalid_breaker_fails_loud(kwargs: dict, match: str) -> None:
    with pytest.raises(CircuitBreakerError, match=match):
        CircuitBreaker(**kwargs)


# --- the state machine ---------------------------------------------------------------------------


def test_it_starts_closed_and_allows() -> None:
    cb = CircuitBreaker(failure_threshold=3, reset_timeout=5.0)
    assert cb.state() == "closed" and cb.allow() is True


def test_it_trips_to_open_after_the_threshold_of_consecutive_failures() -> None:
    cb = CircuitBreaker(failure_threshold=3, reset_timeout=5.0, clock=_Clock())
    cb.record_failure()
    cb.record_failure()
    assert cb.state() == "closed"  # 2 < 3, still closed
    cb.record_failure()
    assert cb.state() == "open" and cb.allow() is False  # the third trips it


def test_a_success_resets_the_consecutive_failure_count() -> None:
    cb = CircuitBreaker(failure_threshold=3, reset_timeout=5.0, clock=_Clock())
    cb.record_failure()
    cb.record_failure()
    cb.record_success()  # streak broken
    cb.record_failure()
    cb.record_failure()
    assert cb.state() == "closed"  # only 2 consecutive since the success


def test_after_the_reset_timeout_it_half_opens_and_a_probe_success_closes_it() -> None:
    clock = _Clock()
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=10.0, clock=clock)
    cb.record_failure()  # trips (threshold 1)
    assert cb.state() == "open"
    clock.t = 10.0  # the reset window elapses
    assert cb.state() == "half_open" and cb.allow() is True  # one probe allowed
    cb.record_success()
    assert cb.state() == "closed"  # the probe worked; back to normal


def test_recovery_happens_after_the_timeout_not_only_at_the_exact_boundary() -> None:
    clock = _Clock()
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=10.0, clock=clock)
    cb.record_failure()  # opens at t=0
    clock.t = 9.5
    assert cb.state() == "open"  # still inside the window
    clock.t = 25.0  # well PAST the window, not just exactly at it
    assert cb.state() == "half_open"  # recovers once the elapsed time is >= the timeout


def test_a_half_open_probe_failure_reopens_the_breaker() -> None:
    clock = _Clock()
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=10.0, clock=clock)
    cb.record_failure()
    clock.t = 10.0
    assert cb.state() == "half_open"
    cb.record_failure()  # the probe failed
    assert cb.state() == "open" and cb.allow() is False
    clock.t = 15.0  # not yet past the new open window (opened at t=10, +10 = 20)
    assert cb.state() == "open"
    clock.t = 20.0
    assert cb.state() == "half_open"  # probes again after another full timeout


# --- the call runner -----------------------------------------------------------------------------


def test_call_runs_and_records_a_success() -> None:
    cb = CircuitBreaker(failure_threshold=2, reset_timeout=5.0, clock=_Clock())
    assert cb.call(lambda: "ok") == "ok"
    assert cb.state() == "closed"


def test_call_records_a_failure_and_reraises_never_swallows() -> None:
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=5.0, clock=_Clock())

    def boom() -> str:
        raise ValueError("down")

    with pytest.raises(ValueError, match="down"):
        cb.call(boom)  # the exception is recorded, then re-raised
    assert cb.state() == "open"  # the failure tripped it (threshold 1)


def test_call_on_an_open_breaker_raises_circuit_open_without_running_fn() -> None:
    cb = CircuitBreaker(failure_threshold=1, reset_timeout=5.0, clock=_Clock())
    cb.record_failure()  # trip it
    ran = {"n": 0}

    def counted() -> str:
        ran["n"] += 1
        return "x"

    with pytest.raises(CircuitOpen):
        cb.call(counted)
    assert ran["n"] == 0  # fast-fail: fn never ran
