"""Proof for consume: it records a consumer on the card, idempotently."""

from __future__ import annotations

import shutil
from pathlib import Path

from hardware_store import consume
from hardware_store import store_lib as sl

PASS_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pass"
PART = "example-reverser"


def _stage(tmp_path: Path) -> Path:
    root = tmp_path / "store"
    shutil.copytree(PASS_FIXTURE, root)
    return root / "catalog" / PART / "CARD.md"


def test_records_a_new_consumer(tmp_path: Path) -> None:
    card_path = _stage(tmp_path)
    status = consume.record_consumption(card_path, "demo-repo", "demo-repo/app.py",
                                        "0.1.0", "2026-08-02")
    assert status == "recorded"
    card = sl.load_card(card_path)
    assert [c["repo"] for c in card.consumers] == ["demo-repo"]
    assert card.consumers[0]["path"] == "demo-repo/app.py"


def test_second_identical_record_is_idempotent(tmp_path: Path) -> None:
    card_path = _stage(tmp_path)
    args = (card_path, "demo-repo", "demo-repo/app.py", "0.1.0", "2026-08-02")
    consume.record_consumption(*args)
    again = consume.record_consumption(*args)
    assert again == "already-recorded"
    assert len(sl.load_card(card_path).consumers) == 1


def test_card_still_parses_after_consume(tmp_path: Path) -> None:
    card_path = _stage(tmp_path)
    consume.record_consumption(card_path, "a", "a/x.py", "0.1.0", "2026-08-02")
    consume.record_consumption(card_path, "b", "b/y.py", "0.2.0", "2026-08-02")
    card = sl.load_card(card_path)  # must not raise
    assert {c["repo"] for c in card.consumers} == {"a", "b"}
