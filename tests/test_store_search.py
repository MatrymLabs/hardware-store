"""Proof for store_search: it finds by capability, filters, and logs the query."""

from __future__ import annotations

import json
from pathlib import Path

from hardware_store import store_lib as sl
from hardware_store import store_search as ss

PASS_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pass"


def _cards() -> list[sl.Card]:
    return sl.load_cards(PASS_FIXTURE / "catalog")


def test_finds_by_capability_term() -> None:
    results = ss.search(_cards(), "reverse", None, None)
    assert [c.slug for _, c in results] == ["example-reverser"]


def test_empty_term_lists_everything() -> None:
    results = ss.search(_cards(), "", None, None)
    assert len(results) == 1


def test_category_filter_excludes_mismatch() -> None:
    assert ss.search(_cards(), "reverse", "Data", None) == []
    assert len(ss.search(_cards(), "reverse", "Pattern", None)) == 1


def test_language_filter() -> None:
    assert len(ss.search(_cards(), "", None, "python")) == 1
    assert ss.search(_cards(), "", None, "rust") == []


def test_query_is_logged(tmp_path: Path) -> None:
    log = ss.log_query(tmp_path, "reverse", None, "python", "demo-repo", 1, "2026-08-02")
    line = json.loads(log.read_text(encoding="utf-8").strip())
    assert line["repo"] == "demo-repo" and line["term"] == "reverse" and line["results"] == 1


def test_no_log_flag_writes_nothing(tmp_path: Path) -> None:
    ss.main(["reverse", "--root", str(tmp_path), "--no-log"])
    assert not (tmp_path / "intake" / "search_log.jsonl").exists()


def test_search_without_no_log_records_the_query(tmp_path: Path) -> None:
    ss.main(["reverse", "--root", str(tmp_path), "--repo", "demo", "--when", "2026-08-02"])
    assert (tmp_path / "intake" / "search_log.jsonl").exists()


def test_log_file_overrides_the_default_location(tmp_path: Path) -> None:
    dest = tmp_path / ".hardware-store" / "search_log.jsonl"
    ss.log_query(tmp_path, "retry", None, None, "stream-repo", 0, "2026-08-02", log_file=dest)
    line = json.loads(dest.read_text(encoding="utf-8").strip())
    assert line["repo"] == "stream-repo"
    assert not (tmp_path / "intake" / "search_log.jsonl").exists()
