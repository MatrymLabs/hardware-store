"""circuit_breaker -- fail fast when a dependency is sustainedly broken.

Retry handles a transient blip; a circuit breaker handles a SUSTAINED outage. CLOSED, the breaker
passes calls and counts consecutive failures; at `failure_threshold` it trips to OPEN and rejects at
once, so callers fail fast instead of paying a full retry-and-backoff on every request while the
dependency is down. After `reset_timeout` seconds it moves to HALF_OPEN and lets ONE probe through:
a success closes it, a failure re-opens it.

The Part is the three-state machine plus one convenience runner, so a consumer uses whichever shape
fits its boundary:

  * the raw state machine -- `allow()` / `record_success()` / `record_failure()` / `state()` --
    for a boundary that decides success/failure itself (e.g. a per-host, result-driven fetcher).
  * `call(fn)` -- the exception-shaped runner: run `fn` if allowed, else raise `CircuitOpen`;
    record the outcome (a raised exception is recorded then re-raised, never swallowed).

The CLOCK is injected (default `time.monotonic`) so tests drive the reset timeout without waiting.
Not thread-safe by design: a single-worker guard for one boundary. Stdlib only.

Provenance: clean-room reconstruction of the standard circuit-breaker pattern (Azure resilience
guidance). The capability is currently re-implemented in two fleet repos -- ai-log-triage
(`triage/circuit.py`, using `call`) and federal-guidance-library (`fgl/circuit.py`, whose per-host
`BreakeredFetcher` uses the raw state machine) -- with a byte-identical state machine; this Part
unifies it. No code from either was copied.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeVar

T = TypeVar("T")
Clock = Callable[[], float]

CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"


class CircuitBreakerError(ValueError):
    """A circuit breaker built with invalid settings. Fails loud at construction."""


class CircuitOpen(RuntimeError):
    """A call was rejected because the breaker is open (fail fast; the operation never ran)."""


@dataclass
class CircuitBreaker:
    """Trip to OPEN after `failure_threshold` consecutive failures; probe again after
    `reset_timeout` seconds. Driven by explicit record_success / record_failure, or via `call`."""

    failure_threshold: int
    reset_timeout: float
    clock: Clock | None = None
    _state: str = field(init=False, default=CLOSED)
    _failures: int = field(init=False, default=0)
    _opened_at: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        threshold = self.failure_threshold
        if not isinstance(threshold, int) or isinstance(threshold, bool):
            raise CircuitBreakerError(f"failure_threshold must be an int, got {threshold!r}")
        if threshold < 1:
            raise CircuitBreakerError(f"failure_threshold must be >= 1, got {threshold}")
        if not math.isfinite(self.reset_timeout) or self.reset_timeout < 0:
            raise CircuitBreakerError("reset_timeout must be a finite, non-negative number")
        self._clock: Clock = self.clock or time.monotonic

    def _maybe_recover(self) -> None:
        if self._state == OPEN and (self._clock() - self._opened_at) >= self.reset_timeout:
            self._state = HALF_OPEN  # reset window elapsed; allow one probe

    def state(self) -> str:
        """The current state, accounting for a reset timeout that may have elapsed."""
        self._maybe_recover()
        return self._state

    def allow(self) -> bool:
        """Whether a call may proceed now (open rejects; closed and half-open allow)."""
        return self.state() != OPEN

    def record_success(self) -> None:
        if self._state == HALF_OPEN:
            self._state = CLOSED  # the probe worked; resume normal service
        self._failures = 0

    def record_failure(self) -> None:
        self._maybe_recover()
        if self._state == HALF_OPEN:
            self._state = OPEN  # the probe failed; re-open
            self._opened_at = self._clock()
        elif self._state == CLOSED:
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._state = OPEN  # too many consecutive failures; trip
                self._opened_at = self._clock()

    def call(self, fn: Callable[[], T]) -> T:
        """Run `fn` if the breaker allows; else raise CircuitOpen. Records the outcome."""
        if not self.allow():
            raise CircuitOpen("circuit is open; call rejected")
        try:
            result = fn()
        except Exception:
            self.record_failure()  # recorded, then re-raised (never swallowed)
            raise
        self.record_success()
        return result
