"""Test twin for budget_gate (EXP-33) -- acceptance AND refusal/hostile cases.

Acceptance: a within-ceiling spend rules "within" with correct headroom; an over-ceiling spend rules
"breach" with correct overage; the ceiling boundary is inclusive; default_ceiling backfills an
unlisted key; tally sums by key and by period. Refusal/hostile: negative amount/spent/ceiling fail
loud; an unbudgeted key with no default fails loud; a corrupt (non-numeric / negative) ledger row
fails loud; a zero ceiling breaches any positive spend; float-precision boundary holds.
"""

from __future__ import annotations

import pytest
from budget_gate import BudgetError, Verdict, check_budget, tally

CEILINGS = {"llm-triage": 50.0, "backup": 5.0}


# --- acceptance -----------------------------------------------------------------------------------


def test_a_spend_under_the_ceiling_is_within_with_correct_headroom() -> None:
    v = check_budget("llm-triage", 1.50, spent=48.00, ceilings=CEILINGS)
    assert isinstance(v, Verdict) and v.within is True and v.status == "within"
    assert v.headroom == pytest.approx(0.50) and v.overage == 0.0
    assert "within" in v.reason and "llm-triage" in v.reason


def test_a_spend_over_the_ceiling_is_a_breach_with_correct_overage() -> None:
    v = check_budget("llm-triage", 3.10, spent=48.00, ceilings=CEILINGS)
    assert v.within is False and v.status == "breach"
    assert v.overage == pytest.approx(1.10) and v.headroom == 0.0
    assert "breach" in v.reason and "over by 1.10" in v.reason


def test_the_ceiling_boundary_is_inclusive_exact_fit_is_within() -> None:
    v = check_budget("backup", 5.00, spent=0.00, ceilings=CEILINGS)
    assert v.within is True and v.headroom == 0.0  # landing exactly on the ceiling is allowed


def test_default_ceiling_backfills_an_unlisted_key() -> None:
    v = check_budget("adhoc", 2.00, spent=0.00, ceilings=CEILINGS, default_ceiling=3.0)
    assert v.within is True and v.ceiling == 3.0
    assert (
        check_budget("adhoc", 4.00, spent=0.0, ceilings=CEILINGS, default_ceiling=3.0).status
        == "breach"
    )


def test_a_specific_ceiling_overrides_the_default() -> None:
    v = check_budget("backup", 4.00, spent=2.00, ceilings=CEILINGS, default_ceiling=100.0)
    assert v.ceiling == 5.0 and v.status == "breach"  # backup's own 5.0, not the 100.0 default


def test_a_zero_spend_check_reports_full_headroom() -> None:
    v = check_budget("llm-triage", 0.00, spent=0.00, ceilings=CEILINGS)
    assert v.within is True and v.headroom == pytest.approx(50.0)


def test_tally_sums_only_the_matching_key() -> None:
    ledger = [
        {"key": "llm-triage", "amount": 10.0},
        {"key": "backup", "amount": 2.0},
        {"key": "llm-triage", "amount": 5.5},
    ]
    assert tally(ledger, "llm-triage") == pytest.approx(15.5)
    assert tally(ledger, "backup") == pytest.approx(2.0)
    assert tally(ledger, "absent") == 0.0  # a key with no rows sums to zero, not an error


def test_tally_filters_by_period_when_given() -> None:
    ledger = [
        {"key": "llm-triage", "amount": 10.0, "period": "2026-07"},
        {"key": "llm-triage", "amount": 4.0, "period": "2026-08"},
        {"key": "llm-triage", "amount": 1.0, "period": "2026-08"},
    ]
    assert tally(ledger, "llm-triage", period="2026-08") == pytest.approx(5.0)  # month-to-date
    assert tally(ledger, "llm-triage") == pytest.approx(15.0)  # all periods when unspecified


def test_tally_feeds_check_budget_end_to_end() -> None:
    ledger = [{"key": "llm-triage", "amount": 47.0, "period": "2026-08"}]
    spent = tally(ledger, "llm-triage", period="2026-08")
    assert check_budget("llm-triage", 2.0, spent=spent, ceilings=CEILINGS).within is True
    assert check_budget("llm-triage", 4.0, spent=spent, ceilings=CEILINGS).status == "breach"


# --- refusal / hostile ----------------------------------------------------------------------------


def test_an_unbudgeted_key_with_no_default_fails_loud() -> None:
    with pytest.raises(BudgetError, match="no ceiling"):
        check_budget("mystery", 1.0, spent=0.0, ceilings=CEILINGS)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"key": "llm-triage", "amount": -1.0, "spent": 0.0, "ceilings": CEILINGS},
        {"key": "llm-triage", "amount": 1.0, "spent": -5.0, "ceilings": CEILINGS},
        {"key": "bad", "amount": 1.0, "spent": 0.0, "ceilings": {"bad": -1.0}},
    ],
)
def test_negative_inputs_fail_loud(kwargs) -> None:
    with pytest.raises(BudgetError):
        check_budget(**kwargs)


def test_a_zero_ceiling_breaches_any_positive_spend() -> None:
    v = check_budget("frozen", 0.01, spent=0.0, ceilings={"frozen": 0.0})
    assert v.status == "breach" and v.overage == pytest.approx(0.01)
    # but a zero spend on a zero ceiling is still within (nothing spent, nothing breached)
    assert check_budget("frozen", 0.0, spent=0.0, ceilings={"frozen": 0.0}).within is True


def test_a_corrupt_ledger_row_fails_loud_never_undercounts() -> None:
    with pytest.raises(BudgetError, match="non-numeric"):
        tally([{"key": "x", "amount": "lots"}], "x")
    with pytest.raises(BudgetError, match="non-numeric"):
        tally([{"key": "x", "amount": True}], "x")  # bool is not a spend amount
    with pytest.raises(BudgetError, match="negative"):
        tally([{"key": "x", "amount": -3.0}], "x")


def test_float_precision_boundary_holds() -> None:
    # 0.1 + 0.2 != 0.3 in binary float; the gate must not spuriously breach a legitimate exact fit
    v = check_budget("p", 0.2, spent=0.1, ceilings={"p": 0.3})
    assert v.within is True  # tolerant of representable-value arithmetic at the boundary
