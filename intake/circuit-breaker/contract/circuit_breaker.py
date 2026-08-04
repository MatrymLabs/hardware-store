"""Contract: circuit_breaker -- the interface every implementation of the breaker Part honors.

Language-agnostic in intent (stated here as Python Protocols/signatures). An implementation provides
a three-state breaker (CLOSED -> OPEN -> HALF_OPEN) with the same semantics:

  CircuitBreaker(failure_threshold, reset_timeout, clock=None)
      FAILS LOUD (CircuitBreakerError) on a non-int/bool or < 1 threshold, or a non-finite/negative
      reset_timeout. CLOSED passes and counts consecutive failures; at `failure_threshold` it trips
      to OPEN; after `reset_timeout` (by the injected clock) it becomes HALF_OPEN and allows one
      probe; a probe success closes it, a probe failure re-opens it.

      state() -> "closed"|"open"|"half_open"   the current state (accounts for an elapsed timeout)
      allow() -> bool                          whether a call may proceed now (OPEN rejects)
      record_success() -> None                 a success (closes a HALF_OPEN probe; clears failures)
      record_failure() -> None                 a failure (trips CLOSED->OPEN at the threshold; a
                                               HALF_OPEN probe failure re-opens)
      call(fn) -> T                            run fn if allowed, else raise CircuitOpen; record the
                                               outcome (the exception is recorded, then re-raised)

  CircuitBreakerError(ValueError): raised on invalid construction settings.
  CircuitOpen(RuntimeError): raised by call() when the breaker is open (the operation never ran).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypeVar

T = TypeVar("T")


class CircuitBreakerContract(Protocol):
    failure_threshold: int
    reset_timeout: float

    def state(self) -> str: ...

    def allow(self) -> bool: ...

    def record_success(self) -> None: ...

    def record_failure(self) -> None: ...

    def call(self, fn: Callable[[], T]) -> T: ...
