"""Contract: budget_gate -- the interface every implementation of the cost-governor Part honors.

Language-agnostic in intent (stated here as Python Protocols/signatures). An implementation in any
language provides the same three surfaces with the same semantics:

  check_budget(key, amount, *, spent, ceilings, default_ceiling=None) -> Verdict
      Rule whether spending `amount` on `key` fits, given `spent` already used this period.
      - the ceiling is ceilings[key], else default_ceiling; a key with neither FAILS LOUD
      - a negative amount or spent FAILS LOUD (BudgetError)
      - "within" when spent + amount <= ceiling (inclusive, float-safe), else "breach"
      - returns a VERDICT object (never a bare bool), carrying headroom/overage + a legible reason

  tally(entries, key, *, period=None) -> float
      Sum the `amount` of ledger entries matching `key` (and `period`, when given). A corrupt row
      (non-numeric or negative amount) FAILS LOUD. Clockless: the caller passes the period label.

  Verdict: a frozen record with .key .amount .spent .ceiling .status ("within"|"breach")
           .headroom .overage .reason, and a .within convenience property.
  BudgetError(ValueError): raised on malformed input (unbudgeted key, negative amount/spent/ceiling,
           corrupt ledger row).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Protocol, runtime_checkable


@runtime_checkable
class VerdictContract(Protocol):
    key: str
    amount: float
    spent: float
    ceiling: float
    status: str
    headroom: float
    overage: float
    reason: str

    @property
    def within(self) -> bool: ...


class CheckBudget(Protocol):
    def __call__(
        self,
        key: str,
        amount: float,
        *,
        spent: float,
        ceilings: Mapping[str, float],
        default_ceiling: float | None = None,
    ) -> VerdictContract: ...


class Tally(Protocol):
    def __call__(
        self, entries: Iterable[Mapping[str, object]], key: str, *, period: str | None = None
    ) -> float: ...
