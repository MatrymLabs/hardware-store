"""Contract: retry -- the interface every implementation of the retry Part honors.

Language-agnostic in intent (stated here as Python Protocols/signatures). An implementation in any
language provides the same surfaces with the same semantics: one retry POLICY (attempt budget +
exponential backoff) driving two RUNNERS, one for each way a boundary signals a transient failure.

  RetryPolicy(max_attempts, base_delay, factor, max_delay)
      A frozen, validated schedule. FAILS LOUD (RetryError) on max_attempts < 1, a non-finite or
      negative delay, or factor < 1.
      delay_for(attempt) -> float: seconds after the 1-indexed `attempt` = base_delay *
      factor**(attempt-1), capped at max_delay. Pure; holds no clock and no I/O.

  run_with_retries(fn, policy, *, retry_on=(Exception,), sleep, on_retry=None) -> T
      The EXCEPTION-triggered runner: call `fn()`; if it raises an instance of `retry_on`, retry
      after the policy's delay; re-raise any OTHER (permanent) exception immediately; after the last
      attempt, re-raise the final transient failure (never swallowed). Returns fn()'s value on the
      first success. `sleep` is injected so a caller/test pins the schedule without waiting.

  retry_result(produce, policy, *, transient, sleep, on_retry=None) -> R
      The RESULT-triggered runner: call `produce()`; while `transient(result)` is true and attempts
      remain, wait and call `produce()` again; return the LAST result, transient or not. It NEVER
      raises for a transient result -- a boundary that returns a result object (a dead link, a bad
      status) is data the caller acts on, not an exception.

  Attempt: a frozen record of one retried try -- .number (1-indexed), .delay (seconds waited),
           .reason (why it was judged transient). Passed to the optional `on_retry` hook so each
           retry is observable (log it, count it) for evidence.
  RetryError(ValueError): raised on an invalid policy, at construction.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
R = TypeVar("R")


@runtime_checkable
class AttemptContract(Protocol):
    number: int
    delay: float
    reason: str


class RetryPolicyContract(Protocol):
    max_attempts: int
    base_delay: float
    factor: float
    max_delay: float

    def delay_for(self, attempt: int) -> float: ...


class RunWithRetries(Protocol):
    def __call__(
        self,
        fn: Callable[[], T],
        policy: RetryPolicyContract,
        *,
        retry_on: tuple[type[BaseException], ...] = ...,
        sleep: Callable[[float], None] = ...,
        on_retry: Callable[[AttemptContract], None] | None = ...,
    ) -> T: ...


class RetryResult(Protocol):
    def __call__(
        self,
        produce: Callable[[], R],
        policy: RetryPolicyContract,
        *,
        transient: Callable[[R], bool],
        sleep: Callable[[float], None] = ...,
        on_retry: Callable[[AttemptContract], None] | None = ...,
    ) -> R: ...
