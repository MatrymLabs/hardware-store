+++
part_id = "PRT-0004"
canonical_name = "retry"
capability = "Retry a flaky operation with exponential backoff, for either boundary shape: retry-on-exception (re-raise the final failure) or retry-on-result (return the last result, never raise). One validated policy (attempt budget + backoff) drives both runners."
category = "Operations"
maturity = "CERTIFIED"
contract = "contract/retry.py"
inputs = "a RetryPolicy (max_attempts, base_delay, factor, max_delay); a zero-arg operation (a callable that may raise, or a producer that returns a result); the transient signal (an exception-type tuple, or a result predicate); an injected sleep and an optional on_retry hook"
outputs = "the operation's successful value (exception shape) or the last result (result shape); each retry is reported to on_retry as an Attempt(number, delay, reason)"
permissions = "none (pure of I/O; the caller injects sleep and supplies the operation; no clock, no network)"
security = "no I/O of its own to exploit; fail-loud on an invalid policy stops a mis-configured (e.g. zero-attempt) retry loop from silently passing; never swallows the final exception in the exception shape, so a permanent failure is not hidden as a success"
accessibility = "n/a (library primitive)"
performance = "run_with_retries / retry_result add ~0.45 us to the success path (no retries); delay_for ~0.28 us; NEUTRAL - a resilience wrapper, the cost is the injected sleep between real retries, not the runner"
failure_modes = [
  "RetryError at construction on max_attempts < 1, a non-finite/negative/bool delay, or factor < 1 (a mis-configured policy fails loud, never silently never-retries)",
  "run_with_retries re-raises a permanent exception (not in retry_on) immediately, without a retry",
  "run_with_retries re-raises the FINAL transient exception after the last attempt (never swallowed)",
  "run_with_retries raises RetryError on an empty retry_on (a runner that can never retry is a bug)",
  "retry_result returns the LAST result even if still transient - a caller that needs an error must inspect the result (by design: a bad status is data, not an exception)",
]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 88
mutation_tool = "mutmut"

[provenance]
origin = "clean-room reconstruction of the standard retry / exponential-backoff pattern (AWS Prescriptive Guidance, 'retry with backoff'); NO code copied. The capability is currently re-implemented in TWO fleet repos - ai-log-triage (run_with_retries, exception shape) and federal-guidance-library (RetryingFetcher, result shape) - plus codeforge kernel/shelf; this Part unifies both shapes so those repos can consume one Part"
ai_generated = "implementation and tests are AI-assisted (Claude), human-reviewed and gated"
verified_by = "17 contract tests (100% line+branch coverage of the impl), both consumer shapes reproduced; mutmut 88% kill rate (5 survivors are equivalent mutants: an unreachable pragma line, a message-string wrap a match= still accepts, and a loop bound made redundant by the internal exhaustion guard)"

[rd_certification]
rd_id = "RD-2026-0009"
verdict = "HARDWARE_STORE_PART"

[[implementations]]
language = "python"
path = "impl/python/retry.py"
version = "0.1.0"
benchmark = "success path ~0.45 us/call (run_with_retries and retry_result); delay_for ~0.28 us"

[[current_consumers]]
repo = "ai-log-triage"
path = "ai-log-triage/src/triage/retry.py"
version = "0.1.0"
adopted = "2026-08-04"

[[current_consumers]]
repo = "federal-guidance-library"
path = "federal-guidance-library/src/fgl/resilience.py"
version = "0.1.0"
adopted = "2026-08-04"
+++

# retry (CARD)

Retry a flaky operation with **exponential backoff**. One validated `RetryPolicy` (attempt budget +
backoff schedule) drives **two runners**, because a boundary signals a transient failure in one of
two ways and real fleet consumers use both:

- `run_with_retries(fn, policy, *, retry_on=...)` - the boundary **raises**. Retry a transient
  exception, re-raise a permanent one immediately, and re-raise the **final** transient after the
  last attempt (never swallowed). This is ai-log-triage's LLM-boundary shape.
- `retry_result(produce, policy, *, transient=...)` - the boundary **returns** a result whose shape
  says "transient" (a status 0/429/5xx). Retry while it looks transient and attempts remain, then
  return the **last** result - never raise. This is federal-guidance-library's fetch-boundary shape.

The `sleep` is injected (default `time.sleep`) so tests pin the exact schedule without waiting, and
an optional `on_retry` hook makes each retry observable (an `Attempt` carrying number, delay, and
reason) for evidence. Pure of I/O otherwise; stdlib only.

- **Contract:** `contract/retry.py` (RetryPolicy, run_with_retries, retry_result, Attempt,
  RetryError).
- **Implementation:** `impl/python/retry.py` (Python 3.13, stdlib only).
- **Tests:** `tests/test_contract.py` - acceptance (both runner shapes, exact backoff schedule,
  observable Attempts) + refusal/hostile (invalid policy, permanent-error passthrough, exhausted
  transient, empty retry_on, permanently-transient result); 100% coverage, 88% mutation kill rate.

Maturity: **CERTIFIED** (R&D verdict RD-2026-0009 HARDWARE_STORE_PART; two real consumers; mutation
>= threshold). This Part unified a capability that was reimplemented in ai-log-triage AND
federal-guidance-library; both now consume it and deleted their local dups: ai-log-triage
(`src/triage/llm.py`) uses the exception-triggered runner, federal-guidance-library
(`src/fgl/resilience.py`) uses the result-triggered runner, so both runners are exercised by a real
consumer. The Rule-of-Three / second-consumer pull gate is met by two independent repos.
