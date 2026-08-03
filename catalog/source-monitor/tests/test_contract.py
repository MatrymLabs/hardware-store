"""Test twin for source_monitor (EXP-35) -- acceptance AND refusal/hostile cases.

Acceptance: a first check is FIRST_CAPTURE with a baseline snapshot; an identical refetch is
UNCHANGED; differing content is CONTENT_CHANGED; a fetch that raises is BROKEN_LINK (a value, not a
crash) with the error captured; the snapshot carries hash/size/timestamp; the fetch seam is
injected (no network); check never persists (it only returns the snapshot). Refusal/hostile: an
empty source_id and a previous snapshot for a different source fail loud; report_line renders each
kind; the same content always hashes the same.
"""

from __future__ import annotations

import pytest
from source_monitor import (
    ACTION,
    Change,
    ChangeKind,
    MonitorError,
    Snapshot,
    check,
    classify,
    content_hash,
    report_line,
)

NOW = "2026-08-03"


def _fetch(content: bytes):
    """A fake fetch seam returning fixed bytes (the network is never touched)."""
    return lambda locator: content


def _boom(exc: Exception):
    """A fake fetch seam that fails, to prove a broken link is classified, not raised."""

    def _f(locator: str) -> bytes:
        raise exc

    return _f


# --- acceptance -----------------------------------------------------------------------------------


def test_a_first_check_is_first_capture_with_a_baseline_snapshot() -> None:
    change = check("reg-01", "https://x/doc", _fetch(b"hello"), None, now=NOW)
    assert isinstance(change, Change) and change.kind is ChangeKind.FIRST_CAPTURE
    assert change.changed is False  # a baseline is not something to act on
    snap = change.snapshot
    assert snap is not None
    assert snap.source_id == "reg-01" and snap.size == 5 and snap.captured_at == NOW
    assert snap.content_hash == content_hash(b"hello")


def test_an_identical_refetch_is_unchanged() -> None:
    baseline = check("reg-01", "u", _fetch(b"body"), None, now="2026-08-01").snapshot
    change = check("reg-01", "u", _fetch(b"body"), baseline, now=NOW)
    assert change.kind is ChangeKind.UNCHANGED and change.changed is False


def test_differing_content_is_content_changed() -> None:
    baseline = check("reg-01", "u", _fetch(b"v1"), None, now="2026-08-01").snapshot
    change = check("reg-01", "u", _fetch(b"v2 is different"), baseline, now=NOW)
    assert change.kind is ChangeKind.CONTENT_CHANGED and change.changed is True
    assert change.previous is baseline and change.snapshot is not None
    assert change.snapshot.content_hash != baseline.content_hash


def test_a_failing_fetch_is_a_broken_link_not_a_crash() -> None:
    baseline = Snapshot("reg-01", "abc", 3, "2026-08-01")
    change = check("reg-01", "u", _boom(TimeoutError("timed out")), baseline, now=NOW)
    assert change.kind is ChangeKind.BROKEN_LINK and change.changed is True
    assert change.snapshot is None  # nothing was captured
    assert "timed out" in change.detail and change.previous is baseline


def test_check_never_persists_it_only_returns_the_snapshot() -> None:
    # the caller owns persistence; two checks with no store between them each just return a snapshot
    calls: list[str] = []

    def counting_fetch(locator: str) -> bytes:
        calls.append(locator)
        return b"same"

    first = check("reg-01", "u", counting_fetch, None, now=NOW)
    second = check("reg-01", "u", counting_fetch, first.snapshot, now=NOW)
    assert second.kind is ChangeKind.UNCHANGED  # detection worked purely from passed-in state
    assert calls == [
        "u",
        "u",
    ]  # the only side effect is the injected fetch; nothing else ran


def test_classify_is_pure_over_a_previous_and_a_hash() -> None:
    prev = Snapshot("s", content_hash(b"a"), 1, NOW)
    assert classify(None, content_hash(b"a")) is ChangeKind.FIRST_CAPTURE
    assert classify(prev, content_hash(b"a")) is ChangeKind.UNCHANGED
    assert classify(prev, content_hash(b"b")) is ChangeKind.CONTENT_CHANGED


def test_same_content_always_hashes_the_same() -> None:
    assert content_hash(b"stable") == content_hash(b"stable")
    assert content_hash(b"stable") != content_hash(b"other")


def test_report_line_renders_each_kind() -> None:
    changed = check("reg-01", "u", _fetch(b"new"), Snapshot("reg-01", "old", 3, "x"), now=NOW)
    line = report_line(changed)
    assert "reg-01" in line and "content_changed" in line and NOW in line
    broken = check("reg-01", "u", _boom(ConnectionError("no route")), None, now=NOW)
    broken_line = report_line(broken)
    assert "broken_link" in broken_line and "no route" in broken_line and "n/a" in broken_line


def test_every_kind_has_an_action() -> None:
    assert set(ACTION) == set(ChangeKind)  # no kind is left without operator guidance


# --- refusal / hostile ----------------------------------------------------------------------------


def test_an_empty_source_id_fails_loud() -> None:
    with pytest.raises(MonitorError, match="source_id must be non-empty"):
        check("", "u", _fetch(b"x"), None, now=NOW)


def test_a_previous_snapshot_for_a_different_source_fails_loud() -> None:
    wrong = Snapshot("other-source", "abc", 3, "2026-08-01")
    with pytest.raises(MonitorError, match="not 'reg-01'"):
        check("reg-01", "u", _fetch(b"x"), wrong, now=NOW)
