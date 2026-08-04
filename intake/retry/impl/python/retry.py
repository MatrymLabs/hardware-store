"""retry -- retry a flaky operation with exponential backoff, for either kind of boundary.

A transient failure (a rate limit, a connection blip, a 5xx / overloaded response) usually clears
on a second try; a permanent one (a bad request, an auth error) does not. This Part is one validated
`RetryPolicy` (attempt budget + exponential backoff) driving two runners, because a boundary signals
transience in one of two ways, and real consumers use both:

  * `run_with_retries(fn, policy, *, retry_on=...)` -- the boundary RAISES. Retry when the exception
    is transient (an instance of `retry_on`), re-raise a permanent one immediately, and re-raise the
    final transient failure after the last attempt (never swallowed). Returns fn()'s value.
  * `retry_result(produce, policy, *, transient=...)` -- the boundary RETURNS a result object whose
    shape says "transient" (a status 0/429/5xx). Retry while `transient(result)` holds and attempts
    remain, then return the LAST result. It never raises for transience: the result is data.

The SLEEP is injected (default `time.sleep`) so tests pin the exact schedule and attempt count
without waiting, and an optional `on_retry` hook makes each retry observable (log it, count it) for
evidence. Pure of I/O otherwise, and stdlib only.

Provenance: clean-room reconstruction of the standard retry / exponential-backoff pattern (AWS
Prescriptive Guidance, "retry with backoff"). The capability is currently re-implemented in two
fleet repos -- ai-log-triage's `run_with_retries` (exception shape) and federal-guidance-library's
`RetryingFetcher` (result shape) -- and in codeforge's kernel/shelf; this Part unifies both shapes.
No code from any of them was copied.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")

Sleep = Callable[[float], None]
OnRetry = Callable[["Attempt"], None]


class RetryError(ValueError):
    """A retry policy built with invalid settings. Fails loud at construction."""


@dataclass(frozen=True)
class Attempt:
    """One try that failed transiently and will be retried after `delay` seconds."""

    number: int  # 1-indexed attempt that just failed
    delay: float  # seconds waited before the next attempt
    reason: str  # why it was judged transient (an exception repr, or a status)


def _finite_nonneg(name: str, value: float) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise RetryError(f"{name} must be a finite number, got {value!r}")
    if value < 0:
        raise RetryError(f"{name} must be non-negative, got {value}")
    return float(value)


@dataclass(frozen=True)
class RetryPolicy:
    """How to retry: the attempt budget and the exponential-backoff schedule.

    Which failures count as transient is the RUNNER's decision (an exception type or a result
    predicate), not the policy's -- so one policy serves both boundary shapes."""

    max_attempts: int
    base_delay: float = 0.5
    factor: float = 2.0
    max_delay: float = 30.0

    def __post_init__(self) -> None:
        if not isinstance(self.max_attempts, int) or isinstance(self.max_attempts, bool):
            raise RetryError(f"max_attempts must be an int, got {self.max_attempts!r}")
        if self.max_attempts < 1:
            raise RetryError(f"max_attempts must be >= 1, got {self.max_attempts}")
        _finite_nonneg("base_delay", self.base_delay)
        _finite_nonneg("max_delay", self.max_delay)
        if not math.isfinite(self.factor) or self.factor < 1:
            raise RetryError(f"factor must be >= 1, got {self.factor}")

    def delay_for(self, attempt: int) -> float:
        """Seconds to wait after the 1-indexed `attempt`: base * factor**(attempt-1), capped."""
        raw = self.base_delay * (self.factor ** (attempt - 1))
        return min(self.max_delay, raw)


def run_with_retries(
    fn: Callable[[], T],
    policy: RetryPolicy,
    *,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
    sleep: Sleep = time.sleep,
    on_retry: OnRetry | None = None,
) -> T:
    """Run `fn` under `policy`, retrying a transient (an instance of `retry_on`) failure. Re-raise a
    permanent exception immediately, and re-raise the final transient failure after the last attempt
    (never swallowed). Returns fn()'s value on the first success."""
    if not retry_on:
        raise RetryError("retry_on must name at least one exception type")
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return fn()
        except BaseException as exc:
            if not isinstance(exc, retry_on):
                raise  # permanent (or KeyboardInterrupt/SystemExit): do not retry, do not swallow
            if attempt >= policy.max_attempts:
                raise  # attempts exhausted: re-raise the last transient failure, unswallowed
            delay = policy.delay_for(attempt)
            if on_retry is not None:
                on_retry(Attempt(attempt, delay, repr(exc)))
            sleep(delay)
    raise RetryError(  # pragma: no cover
        "unreachable: max_attempts >= 1 guarantees a return or raise above"
    )


def retry_result(
    produce: Callable[[], R],
    policy: RetryPolicy,
    *,
    transient: Callable[[R], bool],
    sleep: Sleep = time.sleep,
    on_retry: OnRetry | None = None,
) -> R:
    """Call `produce`; while its result looks `transient` and attempts remain, wait and call again.
    Return the LAST result, transient or not -- never raise for a transient result. `transient`
    decides what a retry-worthy result looks like (e.g. a status 0/429/5xx)."""
    result = produce()
    attempt = 1
    while attempt < policy.max_attempts and transient(result):
        delay = policy.delay_for(attempt)
        if on_retry is not None:
            on_retry(Attempt(attempt, delay, f"transient result: {result!r}"))
        sleep(delay)
        result = produce()
        attempt += 1
    return result
