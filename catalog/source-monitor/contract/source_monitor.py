"""Contract: source_monitor -- the interface every implementation of the drift detector honors.

check(source_id, locator, fetch, previous, *, now) -> Change
    Fetch via the injected `fetch(locator)->bytes` seam, classify against `previous`, and RETURN
    a Change - persisting NOTHING (detection is decoupled from mutation; the caller stores the
    snapshot after review). Any fetch failure is caught and classified BROKEN_LINK (a value, not a
    crash). FAILS LOUD (MonitorError) on empty source_id or a previous snapshot for another src.
classify(previous, new_hash) -> ChangeKind     # pure: FIRST_CAPTURE / UNCHANGED / CONTENT_CHANGED
content_hash(content: bytes) -> str            # sha256 hex, the integrity anchor
report_line(change) -> str
Snapshot: source_id, content_hash, size, captured_at.
Change: source_id, kind, snapshot|None, previous|None, action, detail (+ .changed).
ChangeKind: first_capture | unchanged | content_changed | broken_link.
MonitorError(ValueError): raised on malformed input.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

Fetch = Callable[[str], bytes]


class SnapshotContract(Protocol):
    source_id: str
    content_hash: str
    size: int
    captured_at: str


class ChangeContract(Protocol):
    source_id: str
    kind: str
    snapshot: SnapshotContract | None
    previous: SnapshotContract | None
    action: str
    detail: str

    @property
    def changed(self) -> bool: ...


class Check(Protocol):
    def __call__(
        self,
        source_id: str,
        locator: str,
        fetch: Fetch,
        previous: SnapshotContract | None,
        *,
        now: str,
    ) -> ChangeContract: ...
