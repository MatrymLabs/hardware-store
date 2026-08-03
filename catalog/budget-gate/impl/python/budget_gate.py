"""CARD: budget_gate -- a bounded-autonomy cost governor: decide whether an action fits its budget.

Clean-room reconstruction of the bounded-autonomy cost-ceiling pattern (RD-2026-0004 FH-07). The
mechanism is proven in fleet-ops/harness/_budget.py; NO fleet-ops code is reused here - this is a
fresh, generalized, cost-unit-agnostic part built from the spec, so it can govern LLM dollars, API
calls, compute-seconds, or any additive spend.

A caller about to spend asks the gate: given what has already been spent this period and the ceiling
for this key, does `amount` fit? The gate returns a VERDICT (never a bare bool, per the Matrym style
guide), so the caller logs a reason and the audit trail stays legible: "held: adding 3.10 to 48.00
would breach the 50.00 ceiling for 'llm-triage' (over by 1.10)."

Pure and stdlib-only: the gate never reads a clock, a file, or a network. The caller supplies the
period's prior spend (from wherever it keeps its ledger) and the ceilings; the gate only decides.
`tally` sums a spend ledger by key (and optional period) so the caller does not re-implement the
sum, but even that stays clockless - the caller passes the current period label. That keeps the
whole part testable with plain numbers and reusable across any unit of cost.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

#: Boundary tolerance. Costs arrive as binary floats where 0.1 + 0.2 = 0.30000000000000004, so
#: a legitimate exact-fit spend would spuriously breach under a strict `<=`. A spend within this
#: epsilon of the ceiling counts as within (far below one cent, so no real overage hides under it).
#: A caller wanting exactness should pass integer minor units (cents), not floats.
_EPSILON = 1e-9


class BudgetError(ValueError):
    """A malformed budget check -- fail loud, never silently pass an unbudgeted or negative spend.

    Raised for a negative amount or prior spend, a negative ceiling, or a key with no ceiling and no
    default. An unbudgeted action is a governance hole, not a free pass, so it must be explicit."""


@dataclass(frozen=True)
class Verdict:
    """The gate's ruling on one proposed spend. `status` is "within" or "breach" (a verdict, not a
    bare bool); `headroom` is what remains under the ceiling AFTER the spend (0.0 on a breach);
    `overage` is how far a breach exceeds the ceiling (0.0 when within); `reason` is a legible
    one-line audit string. `within` is a convenience mirror of `status == "within"`."""

    key: str
    amount: float
    spent: float
    ceiling: float
    status: str
    headroom: float
    overage: float
    reason: str

    @property
    def within(self) -> bool:
        """True when the spend fits under the ceiling (the audit trail keeps the reason)."""
        return self.status == "within"


def _resolve_ceiling(
    key: str, ceilings: Mapping[str, float], default_ceiling: float | None
) -> float:
    """The ceiling for `key`: its own entry, else the default. A key with neither is a governance
    hole -- fail loud (an unbudgeted action must be declared, never assumed free)."""
    ceiling = ceilings.get(key, default_ceiling)
    if ceiling is None:
        raise BudgetError(f"no ceiling for key {key!r} and no default_ceiling given")
    if ceiling < 0:
        raise BudgetError(f"ceiling for key {key!r} is negative ({ceiling})")
    return float(ceiling)


def check_budget(
    key: str,
    amount: float,
    *,
    spent: float,
    ceilings: Mapping[str, float],
    default_ceiling: float | None = None,
) -> Verdict:
    """Rule whether spending `amount` on `key` fits, given `spent` already used this period.

    The ceiling is `ceilings[key]`, else `default_ceiling`; a key with neither fails loud
    (`BudgetError`) rather than passing an unbudgeted spend. A negative `amount` or `spent` fails
    loud too. The verdict is "within" when `spent + amount <= ceiling`, else "breach"; `headroom`
    and `overage` report the distance either way. Boundary is inclusive: a spend that lands exactly
    on the ceiling is within (0.0 headroom), never a breach."""
    if amount < 0:
        raise BudgetError(f"amount for key {key!r} is negative ({amount})")
    if spent < 0:
        raise BudgetError(f"spent for key {key!r} is negative ({spent})")
    ceiling = _resolve_ceiling(key, ceilings, default_ceiling)
    projected = spent + amount
    if projected <= ceiling + _EPSILON:
        headroom = max(0.0, ceiling - projected)
        reason = (
            f"within: spending {amount:.2f} on {key!r} keeps {spent:.2f} under the "
            f"{ceiling:.2f} ceiling ({headroom:.2f} left)"
        )
        return Verdict(key, amount, spent, ceiling, "within", headroom, 0.0, reason)
    overage = projected - ceiling
    reason = (
        f"breach: adding {amount:.2f} to {spent:.2f} would exceed the {ceiling:.2f} "
        f"ceiling for {key!r} (over by {overage:.2f})"
    )
    return Verdict(key, amount, spent, ceiling, "breach", 0.0, overage, reason)


def tally(entries: Iterable[Mapping[str, object]], key: str, *, period: str | None = None) -> float:
    """Sum the `amount` of ledger `entries` matching `key` (and `period`, when given).

    A ledger entry is a mapping with at least `key` and a numeric `amount`; when `period` is given,
    only entries whose own `period` equals it count (the caller passes the current period label,
    e.g. "2026-08", so this stays clockless). An entry with a non-numeric or negative `amount` fails
    loud -- a corrupt ledger row must not silently under-count spend. This is the "spent" a caller
    feeds to `check_budget`."""
    total = 0.0
    for entry in entries:
        if entry.get("key") != key:
            continue
        if period is not None and entry.get("period") != period:
            continue
        amount = entry.get("amount")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise BudgetError(f"ledger entry for {key!r} has a non-numeric amount ({amount!r})")
        if amount < 0:
            raise BudgetError(f"ledger entry for {key!r} has a negative amount ({amount})")
        total += float(amount)
    return total
