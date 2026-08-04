+++
part_id = "PRT-0005"
canonical_name = "circuit_breaker"
capability = "Fail fast when a dependency is sustainedly broken: a three-state (closed/open/half-open) circuit breaker that trips after consecutive failures, fast-fails while open, then probes once after a reset timeout. Usable as a raw state machine or via a call(fn) runner."
category = "Operations"
maturity = "CANDIDATE"
contract = "contract/circuit_breaker.py"
inputs = "a failure_threshold (int >= 1), a reset_timeout (finite, non-negative seconds), an optional injected clock; then success/failure signals via record_success/record_failure or a callable via call(fn)"
outputs = "state() (closed|open|half_open), allow() (bool); call(fn) returns fn()'s value or raises CircuitOpen when the breaker is open"
permissions = "none (pure of I/O; the caller injects the clock and supplies the operation; no network)"
security = "no I/O of its own to exploit; fail-loud on an invalid threshold/timeout stops a mis-configured (never-tripping or always-open) breaker from silently passing; call() records a failure then re-raises (never swallows), so a broken dependency is not hidden as a success"
accessibility = "n/a (library primitive)"
performance = "allow() ~0.16 us/call; call() ~0.39 us on the closed/success path; NEUTRAL - a resilience guard, not a hot loop"
failure_modes = [
  "CircuitBreakerError at construction on a non-int/bool or < 1 failure_threshold, or a non-finite/negative reset_timeout (a mis-configured breaker fails loud)",
  "call() raises CircuitOpen when the breaker is open, WITHOUT running fn (fast-fail; the operation never ran)",
  "call() records a failure and RE-RAISES the exception (never swallowed), so a broken dependency is not counted as a success",
  "not thread-safe by design: a single-worker guard for one boundary (documented, not a silent hazard)",
]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 78
mutation_tool = "cosmic-ray"

[provenance]
origin = "clean-room reconstruction of the standard circuit-breaker pattern (Azure resilience guidance); NO code copied. The state machine was re-implemented BYTE-IDENTICALLY in two fleet repos - ai-log-triage (triage/circuit.py, using call) and federal-guidance-library (fgl/circuit.py, whose per-host BreakeredFetcher uses the raw state machine) - plus codeforge kernel/shelf; this Part unifies it"
ai_generated = "implementation and tests are AI-assisted (Claude), human-reviewed and gated"
verified_by = "14 contract tests (100% line+branch coverage of the impl): the full state machine (closed->open->half_open->closed/open), the reset-timeout boundary, and the call runner + hostile construction; cosmic-ray 78% kill rate (102 mutants, 22 survivors dominated by EQUIVALENT comparison-operator mutants: == vs `is` on interned string-state constants, == vs >= on the state enum, and NumberReplacer mutants on dataclass default fields overwritten before use). cosmic-ray, not mutmut, because mutmut cannot map class-method mutants to tests (the fleet-legit alternative, established by HC-29)"

[[implementations]]
language = "python"
path = "impl/python/circuit_breaker.py"
version = "0.1.0"
benchmark = "allow() ~0.16 us/call; call() ~0.39 us on the closed/success path"
+++

# circuit_breaker (CARD)

**Fail fast when a dependency is sustainedly broken.** Retry (see the `retry` Part) recovers a
transient blip; a circuit breaker handles a **sustained outage**. CLOSED, it passes calls and counts
consecutive failures; at `failure_threshold` it trips to **OPEN** and rejects at once, so callers
fail fast instead of paying a full retry-and-backoff on every request while the dependency is down.
After `reset_timeout` seconds it goes **HALF_OPEN** and lets one probe through: a success closes it,
a failure re-opens it.

One Part, two shapes, because real fleet consumers use both:

- the raw state machine (`allow` / `record_success` / `record_failure` / `state`) for a boundary
  that decides success/failure itself - e.g. federal-guidance-library's per-host, result-driven
  `BreakeredFetcher`.
- `call(fn)` - the exception-shaped runner: run `fn` if allowed, else raise `CircuitOpen`; record
  the outcome (a raised exception is recorded then re-raised) - e.g. ai-log-triage's LLM boundary.

The CLOCK is injected (default `time.monotonic`) so tests drive the reset timeout without waiting.
Not thread-safe by design: a single-worker guard for one boundary. Stdlib only.

- **Contract:** `contract/circuit_breaker.py` (CircuitBreaker, CircuitBreakerError, CircuitOpen).
- **Implementation:** `impl/python/circuit_breaker.py` (Python 3.13, stdlib only).
- **Tests:** `tests/test_contract.py` - the full state machine + reset-timeout boundary + call runner
  + hostile construction; 100% coverage, cosmic-ray 78% kill rate.

Maturity: **CANDIDATE**. This Part unifies a capability whose state machine is reimplemented
byte-identically in ai-log-triage and federal-guidance-library; certifying it (with both consumers
wired and an R&D verdict) is the founder-gated next step. It completes the resilience pair with
`retry` (PRT-0004).
