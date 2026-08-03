# budget_gate - evidence

## Isolation proof (EXP-33-budget-gate, RD-2026-0004 FH-07)
- 16 contract tests (acceptance + refusal/hostile: negative inputs, unbudgeted key, corrupt ledger
  row, zero-ceiling, float-boundary), 100% line+branch coverage.
- mypy --strict clean, ruff clean.

## Mutation testing (the tests-that-bite score)
- tool: mutmut 3.7.0
- result: 104 mutants generated; 92 killed, 12 survived -> 88% kill rate (>= 70% threshold).

## Benchmark (micro)
- check_budget: ~3.6 us/call (it always builds an audit reason). tally over a 1,000-row ledger:
  ~340 us. Honest label: NEUTRAL on performance (a governance gate, not a hot loop) - the value is
  reuse + a legible verdict, not speed.

## Real consumer
- fleet-ops/harness/_budget.py consumes check_budget for both the per-run and monthly-MTD decisions
  (fleet-ops PR #1). Behaviour preserved byte-for-byte vs the prior hand-rolled enforcer.
