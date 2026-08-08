# circuit_breaker - evidence

## Correctness

- `tests/test_contract.py`: 14 contract tests, **100% line + branch coverage** of
  `impl/python/circuit_breaker.py`.
- The full three-state machine is exercised: CLOSED trips to OPEN at the failure threshold; a
  success resets the consecutive-failure count; OPEN fast-fails; after the reset timeout it
  HALF_OPENs and allows one probe; a probe success closes it, a probe failure re-opens it (and the
  new open window is honored); recovery happens once elapsed >= the timeout (not only at the exact
  boundary).
- The `call` runner: runs and records a success; records a failure and **re-raises** (never
  swallows); on an open breaker raises `CircuitOpen` **without running fn**.
- Hostile construction fails loud: non-int/bool or < 1 threshold, non-finite/negative reset_timeout.

## Mutation (tests-that-bite)

- `cosmic-ray` 8.4.6 over `impl/python/circuit_breaker.py`: **102 mutants, 22 surviving = 78% kill
  rate** (78.43%), above the fleet certified threshold of 70.
- The 22 survivors are dominated by **equivalent comparison-operator mutants**, not test gaps:
  - `Eq_Is` (`==` -> `is`) on interned string-state constants (`"open"`, `"closed"`,
    `"half_open"`) - identity and equality are indistinguishable for interned string literals.
  - `Eq_GtE` / `Eq_LtE` (`==` -> `>=` / `<=`) on the state enum - the ordering preserves behavior
    for the states actually reachable at each comparison.
  - `NumberReplacer` on dataclass default fields (`_failures=0`, `_opened_at=0.0`) that are
    overwritten before they are read.
- **Tool note:** `mutmut` (used for the other Parts) cannot map class-method mutants to tests -- it
  reports "no test case for any mutant" for a method-only module. `cosmic-ray` is the fleet-legit
  mutation alternative, established by HC-29 (the mutation-score-KPI part's cosmic-ray adapter).

## Performance

Micro-benchmark (Python 3.13, aarch64):

| surface | time |
|---|---|
| `allow()` | ~0.16 us/call |
| `call()` (closed, success) | ~0.39 us/call |

**NEUTRAL** - a resilience guard, not a hot loop.

## Provenance

Clean-room reconstruction of the standard circuit-breaker pattern (Azure resilience guidance). No
code copied from the byte-identical state machines it unifies (ai-log-triage `triage/circuit.py`,
federal-guidance-library `fgl/circuit.py`) or from codeforge `kernel/shelf`.
