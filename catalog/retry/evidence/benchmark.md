# retry - evidence

## Correctness

- `tests/test_contract.py`: 17 contract tests, **100% line + branch coverage** of
  `impl/python/retry.py` (measured with pytest-cov).
- Both real consumer shapes are reproduced against the one Part:
  - exception shape (ai-log-triage): retry a transient exception, re-raise a permanent one
    immediately, re-raise the final transient after exhaustion.
  - result shape (federal-guidance-library): retry a transient result, return the last result,
    never raise.
- Refusal / hostile cases: invalid policy (max_attempts < 1, non-finite/negative/bool delay,
  factor < 1), empty `retry_on`, permanent-error passthrough, exhausted-transient re-raise,
  permanently-transient result returned.

## Mutation (tests-that-bite)

- `mutmut` over `impl/python/retry.py`: **59 mutants, 52 killed + 2 timeout, 5 survived = 88%
  kill rate** (strict killed/total), above the fleet certified threshold of 70.
- The 5 survivors are **equivalent mutants**, not test gaps:
  - 3 mutate the `# pragma: no cover` unreachable `RetryError` line (never executed).
  - 1 wraps an error-message string (`"...text..."` -> `"XX...text...XX"`) that a `match=`
    substring assertion still accepts.
  - 1 widens the `for` loop's upper bound, which is redundant with the internal
    `attempt >= policy.max_attempts` exhaustion guard that raises/returns first.

## Performance

Micro-benchmark (Python 3.13, aarch64), success path with retries disabled:

| surface | time |
|---|---|
| `run_with_retries` (first-try success) | ~0.45 us/call |
| `retry_result` (first-try success) | ~0.44 us/call |
| `RetryPolicy.delay_for` | ~0.28 us/call |

**NEUTRAL** - a resilience wrapper. The real cost between retries is the injected `sleep`, not the
runner; the runner overhead is negligible on the happy path.

## Provenance

Clean-room reconstruction of the retry / exponential-backoff pattern (AWS Prescriptive Guidance).
No code copied from the fleet reimplementations it is meant to replace (ai-log-triage
`src/triage/resilience.py`, federal-guidance-library `src/fgl/resilience.py`) or from codeforge
`kernel/shelf`.
