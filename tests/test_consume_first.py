"""Proof for consume_first: it flags a probable reimplementation unless overridden."""

from __future__ import annotations

import json
from pathlib import Path

from hardware_store import consume_first as cf

REGISTRY = [
    {"slug": "retry", "canonical_name": "retry", "capability": "retry with backoff",
     "category": "Pattern", "maturity": "CERTIFIED", "languages": ["python"],
     "consumers": ["x"], "version": "0.1.0"},
    {"slug": "circuit-breaker", "canonical_name": "circuit_breaker",
     "capability": "fail fast", "category": "Pattern", "maturity": "CERTIFIED",
     "languages": ["python"], "consumers": ["x"], "version": "0.1.0"},
]


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _log(tmp_path: Path, repo: str | None) -> Path:
    log = tmp_path / "search_log.jsonl"
    if repo is not None:
        log.write_text(json.dumps({"repo": repo, "term": "retry"}) + "\n", encoding="utf-8")
    return log


def test_flags_reimplementation_without_search_or_decision(tmp_path: Path) -> None:
    f = _write(tmp_path / "retry_helper.py", "def retry_call():\n    ...\n")
    flags = cf.scan([f], REGISTRY, _log(tmp_path, repo=None), repo="stream-a")
    assert len(flags) == 1
    assert flags[0].capability_slug == "retry"
    assert flags[0].overridden_by == ""
    _, code = cf.render(flags)
    assert code == 1


def test_decision_comment_overrides(tmp_path: Path) -> None:
    f = _write(tmp_path / "retry_helper.py",
               "# DECISION: domain-specific retry, Store part does not fit\n"
               "def retry_call():\n    ...\n")
    flags = cf.scan([f], REGISTRY, _log(tmp_path, repo=None), repo="stream-a")
    assert flags[0].overridden_by == "DECISION"
    _, code = cf.render(flags)
    assert code == 0


def test_logged_search_overrides(tmp_path: Path) -> None:
    f = _write(tmp_path / "circuit.py", "class CircuitBreaker:\n    ...\n")
    flags = cf.scan([f], REGISTRY, _log(tmp_path, repo="stream-a"), repo="stream-a")
    assert flags[0].capability_slug == "circuit-breaker"
    assert flags[0].overridden_by == "search-log"
    _, code = cf.render(flags)
    assert code == 0


def test_unrelated_file_is_not_flagged(tmp_path: Path) -> None:
    f = _write(tmp_path / "widget.py", "value = 1\n")
    flags = cf.scan([f], REGISTRY, _log(tmp_path, repo=None), repo="stream-a")
    assert flags == []
    _, code = cf.render(flags)
    assert code == 0


def test_non_python_file_ignored(tmp_path: Path) -> None:
    f = _write(tmp_path / "notes.md", "we should add retry here\n")
    flags = cf.scan([f], REGISTRY, _log(tmp_path, repo=None), repo="stream-a")
    assert flags == []


def test_search_log_matches_only_the_named_repo(tmp_path: Path) -> None:
    f = _write(tmp_path / "retry_helper.py", "def retry_call():\n    ...\n")
    # log belongs to a different repo -> no override for stream-a
    flags = cf.scan([f], REGISTRY, _log(tmp_path, repo="other-repo"), repo="stream-a")
    assert flags[0].overridden_by == ""
