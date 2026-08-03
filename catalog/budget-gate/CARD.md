+++
part_id = "PRT-0001"
canonical_name = "budget_gate"
capability = "Decide whether a proposed spend fits its budget: a bounded-autonomy cost governor that returns a within/breach verdict for any additive cost unit (dollars, tokens, API calls, compute-seconds)."
category = "Operations"
maturity = "CERTIFIED"
contract = "contract/budget_gate.py"
inputs = "a key, a proposed amount, the period's prior spent, a ceilings map, an optional default ceiling; tally takes a ledger of {key, amount, period} entries"
outputs = "a Verdict (status within|breach, headroom, overage, legible reason); tally returns a float total"
permissions = "none (a pure decision function; no I/O, no clock, no network)"
security = "no I/O to exploit; fail-loud on malformed input stops an unbudgeted or corrupt spend from silently passing; for exact accounting pass integer minor units (cents) - floats use a documented epsilon at the ceiling boundary"
accessibility = "n/a (library primitive)"
performance = "check ~3.6 us/call (always builds an audit reason); tally O(n) over the ledger; NEUTRAL - a governance gate, not a hot loop"
failure_modes = [
  "BudgetError on a negative amount or prior spent",
  "BudgetError on a key with no ceiling and no default (an unbudgeted action is a governance hole, not a free pass)",
  "BudgetError on a negative ceiling",
  "BudgetError on a corrupt ledger row (non-numeric or negative amount) - never silently under-counts spend",
]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 88
mutation_tool = "mutmut"

[provenance]
origin = "clean-room reconstruction of the bounded-autonomy cost-ceiling pattern (RD-2026-0004 FH-07 / EXP-33-budget-gate); the mechanism was proven in fleet-ops/harness/_budget.py, NO fleet-ops code reused"
ai_generated = "implementation and tests are AI-assisted (Claude), human-reviewed and gated"
verified_by = "16 contract tests (100% coverage), mypy --strict, ruff, and mutmut (88% kill rate); dogfooded byte-for-byte in fleet-ops"

[rd_certification]
rd_id = "RD-2026-0004"
verdict = "HARDWARE_STORE_PART"

[[implementations]]
language = "python"
path = "impl/python/budget_gate.py"
version = "0.1.0"
benchmark = "check ~3.6 us/call; tally ~340 us over a 1,000-row ledger"

[[current_consumers]]
repo = "fleet-ops"
path = "fleet-ops/harness/_budget.py"
version = "0.1.0"
adopted = "2026-08-03"
+++

# budget_gate (CARD)

A bounded-autonomy **cost governor**. Given the ceiling for a key and what has already been spent
this period, `check_budget` rules whether a proposed spend fits, and returns a **verdict** (not a
bare bool): `within` or `breach`, with headroom/overage and a legible audit reason. `tally` sums a
spend ledger by key and optional period so the caller does not re-implement the sum. Pure and
stdlib-only - no clock, no file, no network: the caller supplies the period's prior spend and the
ceilings; the Part only decides.

- **Contract:** `contract/budget_gate.py` (check_budget, tally, Verdict, BudgetError).
- **Implementation:** `impl/python/budget_gate.py` (Python 3.13, stdlib only).
- **Tests:** `tests/test_contract.py` - acceptance + refusal/hostile (negative inputs, unbudgeted
  key, corrupt ledger row, zero-ceiling, float-boundary); 100% coverage, 88% mutation kill rate.
- **Consumer:** fleet-ops `harness/_budget.py` replaced its hand-rolled ceiling logic with this Part
  (per-run + monthly-MTD decisions), behaviour preserved byte-for-byte.

Maturity: **CERTIFIED** (RD-2026-0004 HARDWARE_STORE_PART; one real consumer; mutation >= threshold).
