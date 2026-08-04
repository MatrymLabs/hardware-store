"""Contract tests for the retry Part: one policy, two runners, BOTH real consumer shapes.

Acceptance: the exception-triggered runner (ai-log-triage's shape) retries a transient exception and
succeeds; the result-triggered runner (federal-guidance-library's shape) retries a transient result
and returns the last one without raising; the backoff schedule is exact and observable.

Refusal / hostile: an invalid policy fails loud; a permanent exception is re-raised without a retry;
an exhausted transient is re-raised (exception shape); a permanently-transient result is returned,
never raised (result shape); an empty retry_on fails loud.
"""

from __future__ import annotations

import pytest
from retry import (
    Attempt,
    RetryError,
    RetryPolicy,
    retry_result,
    run_with_retries,
)


class _Transient(Exception):
    """A retryable failure (stands in for a rate limit / 5xx / connection blip)."""


class _Permanent(Exception):
    """A non-retryable failure (stands in for a bad request / auth error)."""


def _recorder() -> tuple[list[float], object]:
    waited: list[float] = []
    return waited, waited.append  # (log, sleep)


# --- RetryPolicy: validation + schedule ----------------------------------------------------------


def test_delay_for_is_exponential_and_capped() -> None:
    policy = RetryPolicy(max_attempts=5, base_delay=1.0, factor=2.0, max_delay=5.0)
    assert [policy.delay_for(n) for n in (1, 2, 3, 4)] == [1.0, 2.0, 4.0, 5.0]  # 8.0 capped to 5.0


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"max_attempts": 0}, "max_attempts"),
        ({"max_attempts": 1.5}, "max_attempts"),  # a float is not an int
        ({"max_attempts": True}, "max_attempts"),  # a bool is not an int
        ({"max_attempts": 3, "base_delay": -1.0}, "base_delay"),
        ({"max_attempts": 3, "base_delay": True}, "base_delay"),  # a bool is not a real delay
        ({"max_attempts": 3, "base_delay": float("inf")}, "base_delay"),
        ({"max_attempts": 3, "max_delay": -0.1}, "max_delay"),
        ({"max_attempts": 3, "factor": 0.5}, "factor"),
    ],
)
def test_an_invalid_policy_fails_loud(kwargs: dict, match: str) -> None:
    with pytest.raises(RetryError, match=match):
        RetryPolicy(**kwargs)


def test_a_zero_base_delay_is_valid() -> None:
    # zero backoff is allowed (retry immediately); the boundary is < 0, not <= 0.
    assert RetryPolicy(max_attempts=2, base_delay=0.0).delay_for(1) == 0.0


# --- run_with_retries: the EXCEPTION shape (ai-log-triage) ---------------------------------------


def test_run_with_retries_succeeds_after_transient_failures() -> None:
    waited, sleep = _recorder()
    seen: list[Attempt] = []
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise _Transient(f"blip {calls['n']}")
        return "ok"

    policy = RetryPolicy(max_attempts=5, base_delay=1.0, factor=2.0, max_delay=10.0)
    result = run_with_retries(
        flaky, policy, retry_on=(_Transient,), sleep=sleep, on_retry=seen.append
    )
    assert result == "ok" and calls["n"] == 3
    assert waited == [1.0, 2.0]  # slept before each of the 2 retries, on the exact schedule
    assert [a.number for a in seen] == [1, 2]
    assert seen[0].delay == 1.0 and "blip 1" in seen[0].reason  # the Attempt carries the real delay


def test_run_with_retries_reraises_a_permanent_error_without_retrying() -> None:
    waited, sleep = _recorder()
    calls = {"n": 0}

    def boom() -> str:
        calls["n"] += 1
        raise _Permanent("bad request")

    policy = RetryPolicy(max_attempts=5)
    with pytest.raises(_Permanent):
        run_with_retries(boom, policy, retry_on=(_Transient,), sleep=sleep)
    assert calls["n"] == 1 and waited == []  # not retried, never slept


def test_run_with_retries_reraises_the_final_transient_after_exhaustion() -> None:
    waited, sleep = _recorder()
    calls = {"n": 0}

    def always_transient() -> str:
        calls["n"] += 1
        raise _Transient(f"still down {calls['n']}")

    policy = RetryPolicy(max_attempts=3, base_delay=1.0)
    with pytest.raises(_Transient, match="still down 3"):  # the LAST failure, unswallowed
        run_with_retries(always_transient, policy, retry_on=(_Transient,), sleep=sleep)
    assert calls["n"] == 3 and waited == [1.0, 2.0]  # all attempts used, slept between them


def test_run_with_retries_refuses_an_empty_retry_on() -> None:
    with pytest.raises(RetryError, match="retry_on"):
        run_with_retries(
            lambda: "x", RetryPolicy(max_attempts=2), retry_on=(), sleep=lambda _d: None
        )


# --- retry_result: the RESULT shape (federal-guidance-library) -----------------------------------


def _is_transient(status: int) -> bool:
    return status == 0 or status == 429 or 500 <= status < 600


def test_retry_result_retries_a_transient_result_then_returns_the_success() -> None:
    waited, sleep = _recorder()
    seen: list[Attempt] = []
    statuses = iter([503, 429, 200])  # two transient, then a success

    policy = RetryPolicy(max_attempts=5, base_delay=1.0, factor=2.0, max_delay=10.0)
    result = retry_result(
        lambda: next(statuses),
        policy,
        transient=_is_transient,
        sleep=sleep,
        on_retry=seen.append,
    )
    assert result == 200
    assert waited == [1.0, 2.0] and [a.number for a in seen] == [1, 2]
    assert seen[0].delay == 1.0 and "503" in seen[0].reason  # the Attempt carries delay + reason


def test_retry_result_returns_the_last_result_without_raising() -> None:
    waited, sleep = _recorder()
    calls = {"n": 0}

    def always_down() -> int:
        calls["n"] += 1
        return 503  # every attempt is transient

    policy = RetryPolicy(max_attempts=3, base_delay=1.0)
    result = retry_result(always_down, policy, transient=_is_transient, sleep=sleep)
    assert result == 503  # the LAST result, transient or not -- never raised
    assert calls["n"] == 3 and waited == [1.0, 2.0]


def test_retry_result_returns_a_first_success_without_sleeping() -> None:
    waited, sleep = _recorder()
    result = retry_result(
        lambda: 200, RetryPolicy(max_attempts=5), transient=_is_transient, sleep=sleep
    )
    assert result == 200 and waited == []  # a good result on the first try never retries
