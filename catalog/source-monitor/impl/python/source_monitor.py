"""CARD: source_monitor -- watch a source and classify what changed, without mutating anything.

Clean-room generalization of the federal-guidance-library change detector (RD-2026-0004 FH-03; the
mechanism is proven in fgl/diff.py + fetch.py, which stay natural consumers). A source (a URL, a
file, an API endpoint, a config blob) is fetched, hashed, and compared against the last snapshot;
the result is one of four classified changes with an operator action. The sharp, reusable idea: a
dead link is a *classified value* (BROKEN_LINK), not an exception - so a monitor never crashes on an
unreachable source, it reports it.

Two disciplines make this reusable beyond regulations. The NETWORK IS A SEAM: the caller injects a
`fetch(source) -> bytes` callable (real HTTP in production, a fake in tests), so this part is pure
and offline - tests never touch the network. DETECTION IS DECOUPLED FROM MUTATION: `check` RETURNS
the new snapshot and the classification; it never writes a file, updates a registry, or advances a
status. The caller persists the snapshot and decides what to do AFTER a human reviews the change.
That is what keeps the source of truth human-owned (the FGL doctrine, generalized).

Stdlib only (hashlib, dataclasses, enum). The only impurity is the injected fetch, and its failure
is caught and classified, never propagated.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

#: The caller's fetch seam: given a source locator, return its raw bytes, or raise on any failure
#: (unreachable, timeout, 4xx/5xx). The monitor catches the failure and classifies it BROKEN_LINK.
Fetch = Callable[[str], bytes]


class MonitorError(ValueError):
    """A malformed monitor input -- fail loud (an empty source id, or a previous snapshot whose
    source id does not match the one being checked). A silent mismatch would compare the wrong
    baselines and mis-classify every change."""


class ChangeKind(StrEnum):
    """What a check found, against the last snapshot."""

    BROKEN_LINK = "broken_link"  # source unreachable -> fix the source / confirm withdrawal
    FIRST_CAPTURE = "first_capture"  # no prior snapshot -> baseline established
    UNCHANGED = "unchanged"  # identical content -> no action
    CONTENT_CHANGED = "content_changed"  # content differs -> human review


#: The operator action each change implies (the caller renders this; the part never acts on it).
ACTION: dict[ChangeKind, str] = {
    ChangeKind.BROKEN_LINK: "HIGH: source unreachable - fix the locator or confirm withdrawal",
    ChangeKind.FIRST_CAPTURE: "INFO: baseline snapshot captured",
    ChangeKind.UNCHANGED: "OK: no change since the last snapshot",
    ChangeKind.CONTENT_CHANGED: "HIGH: content changed - open a change review",
}


def content_hash(content: bytes) -> str:
    """The stable sha256 hex digest of content -- the integrity anchor for every snapshot."""
    return hashlib.sha256(content).hexdigest()


@dataclass(frozen=True)
class Snapshot:
    """A point-in-time capture of a source: its `source_id`, the `content_hash`, the byte `size`,
    the caller-supplied `captured_at` timestamp (a label, so the part stays clockless). The caller
    persists this AFTER a review; the part only produces it."""

    source_id: str
    content_hash: str
    size: int
    captured_at: str


@dataclass(frozen=True)
class Change:
    """The verdict of one check: the `kind`, the `snapshot` just taken (None on a broken link), the
    `previous` snapshot compared against, the `action`, and a `detail` (the fetch error on a
    broken link, else ""). A verdict, not a bare bool. `changed` is True only when action is really
    needed (content changed or the link broke); an unchanged or first-capture check is not a change
    to act on."""

    source_id: str
    kind: ChangeKind
    snapshot: Snapshot | None
    previous: Snapshot | None
    action: str
    detail: str = ""

    @property
    def changed(self) -> bool:
        """True when the check needs operator attention (content changed or the source broke)."""
        return self.kind in (ChangeKind.CONTENT_CHANGED, ChangeKind.BROKEN_LINK)


def classify(previous: Snapshot | None, new_hash: str) -> ChangeKind:
    """Classify a successful fetch's hash against the previous snapshot (pure; the broken-link case
    is decided by `check`, which sees the failure). No previous -> FIRST_CAPTURE; equal hash ->
    UNCHANGED; else CONTENT_CHANGED."""
    if previous is None:
        return ChangeKind.FIRST_CAPTURE
    return ChangeKind.UNCHANGED if new_hash == previous.content_hash else ChangeKind.CONTENT_CHANGED


def check(
    source_id: str,
    locator: str,
    fetch: Fetch,
    previous: Snapshot | None,
    *,
    now: str,
) -> Change:
    """Fetch `locator`, classify it against `previous`, and return a `Change` -- without persisting.

    The injected `fetch` does the actual retrieval; any exception it raises is caught and classified
    BROKEN_LINK (with the error in `detail`), so an unreachable source is a value, not a crash. On a
    successful fetch the content is hashed, a new `Snapshot` is built (stamped `now`, a caller-
    supplied label), and the change is classified. The part NEVER writes anything: the returned
    snapshot is the caller's to persist after review, keeping the source of truth human-owned.

    Fails loud (`MonitorError`) on an empty `source_id`, or a `previous` snapshot for a different
    source (comparing the wrong baselines would mis-classify)."""
    if not source_id:
        raise MonitorError("source_id must be non-empty")
    if previous is not None and previous.source_id != source_id:
        raise MonitorError(f"previous snapshot is for {previous.source_id!r}, not {source_id!r}")
    try:
        content = fetch(locator)
    except Exception as exc:  # noqa: BLE001
        # ANY fetch failure (timeout, 4xx/5xx, SSL, DNS) is a classified broken link, never a crash
        return Change(
            source_id,
            ChangeKind.BROKEN_LINK,
            None,
            previous,
            ACTION[ChangeKind.BROKEN_LINK],
            str(exc),
        )
    digest = content_hash(content)
    kind = classify(previous, digest)
    snapshot = Snapshot(source_id, digest, len(content), now)
    return Change(source_id, kind, snapshot, previous, ACTION[kind])


def report_line(change: Change) -> str:
    """A legible one-line report for a change: the timestamp, source, kind, and action (plus the
    error detail on a broken link). What a caller would append to a dated change report."""
    when = change.snapshot.captured_at if change.snapshot else "n/a"
    detail = f" ({change.detail})" if change.detail else ""
    return f"[{when}] {change.source_id}: {change.kind.value}{detail} -> {change.action}"
