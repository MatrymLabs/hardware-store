"""Every Part's contract tests must actually RUN in the gate that certifies it.

For as long as `testpaths` read `["tests"]`, `make check` reported PASS while executing none of the
103 contract tests in the catalogue. `retry`, `typed-settings` and `circuit-breaker` were CERTIFIED
and consumed by real repositories on the strength of contracts CI had never once run. Nothing was
broken; nothing was being checked either, and those are not the same thing.

Fixing `testpaths` fixes today. This file fixes the class: a Part added tomorrow whose tests the
gate cannot collect fails here, loudly, instead of being certified on an unrun contract.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CATALOGUE = ROOT / "catalog"


def parts_with_contract_tests() -> list[str]:
    """Discovered from the catalogue, never hand-listed, so a new Part is covered on arrival."""
    return sorted(p.parent.parent.name for p in CATALOGUE.glob("*/tests/test_contract.py"))


def test_the_catalogue_actually_holds_parts() -> None:
    """Guard the guard: if discovery breaks, every assertion below passes vacuously."""
    assert len(parts_with_contract_tests()) >= 6, parts_with_contract_tests()


@pytest.mark.parametrize("part", parts_with_contract_tests())
def test_a_parts_contract_tests_are_collected_by_the_gate(part: str) -> None:
    """Collected, not merely present on disk. Presence is what the old config already had."""
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", f"catalog/{part}/tests"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert done.returncode == 0, (
        f"the gate cannot collect {part}'s contract tests, so certifying it would rest on a "
        f"contract nothing has run:\n{(done.stdout + done.stderr)[-800:]}"
    )
    assert "test" in done.stdout, f"{part} collected zero tests"


def test_every_part_in_the_registry_has_contract_tests() -> None:
    """A registry entry with no runnable contract is a claim with no evidence behind it."""
    import json

    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    entries = registry if isinstance(registry, list) else registry.get("parts", [])
    have = set(parts_with_contract_tests())
    # STUDIED is an explicit, announced exemption: it records a written pattern, not an
    # implementation claim. CANDIDATE and CERTIFIED still require runnable contract evidence.
    missing = sorted(
        e["slug"]
        for e in entries
        if e.get("slug")
        and e.get("maturity") != "STUDIED"
        and e["slug"] not in have
    )
    assert not missing, f"registered Parts with no contract tests: {missing}"


def test_the_gates_own_config_still_points_at_the_catalogue() -> None:
    """The regression that caused all of this, pinned directly.

    The tests above collect each Part explicitly, so they keep passing even if `testpaths` is
    narrowed back to `["tests"]` and the gate stops running the catalogue entirely. That is the
    exact defect this file exists to prevent, and without this assertion the guard would have had
    the same blind spot as the thing it guards.
    """
    import tomllib

    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pytest_config = config["tool"]["pytest"]["ini_options"]
    assert "catalog" in pytest_config["testpaths"], (
        "testpaths no longer covers the catalogue, so the gate certifies Parts whose contract "
        f"tests it never runs. testpaths={pytest_config['testpaths']}"
    )
    assert "importlib" in pytest_config.get("addopts", ""), (
        "every Part names its test file test_contract.py; without importlib import mode they "
        "collide and the catalogue cannot be collected at all"
    )
