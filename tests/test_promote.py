"""Proof for promote: it refuses an uncertified candidate and promotes a certified one."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from hardware_store import promote
from hardware_store import store_lib as sl

PASS_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pass"
PART = "example-reverser"

CERT_BLOCK = (
    "[rd_certification]\n# empty on purpose: a CANDIDATE has not been through R&D's gate yet"
)


def _store_with_candidate(tmp_path: Path, *, certified: bool) -> Path:
    """Build a tmp Store whose intake/ holds the example candidate."""
    root = tmp_path / "store"
    (root / "catalog").mkdir(parents=True)
    (root / "registry.json").write_text("[]\n", encoding="utf-8")
    shutil.copytree(PASS_FIXTURE / "catalog" / PART, root / "intake" / PART)
    if certified:
        card = root / "intake" / PART / "CARD.md"
        text = card.read_text(encoding="utf-8")
        text = text.replace('maturity = "CANDIDATE"', 'maturity = "CERTIFIED"')
        text = text.replace(
            CERT_BLOCK,
            '[rd_certification]\nrd_id = "RD-2026-0003"\nverdict = "HARDWARE_STORE_PART"',
        )
        card.write_text(text, encoding="utf-8")
    return root


def test_refuses_uncertified_candidate(tmp_path: Path) -> None:
    root = _store_with_candidate(tmp_path, certified=False)
    status, gaps = promote.promote(PART, root, when="2026-08-02")
    assert status == "refused"
    assert any("rd_certification" in g for g in gaps)
    assert not (root / "catalog" / PART).exists()  # nothing moved
    assert (root / "intake" / PART).exists()


def test_promotes_certified_candidate(tmp_path: Path) -> None:
    root = _store_with_candidate(tmp_path, certified=True)
    status, gaps = promote.promote(PART, root, when="2026-08-02")
    assert status == "promoted", gaps
    assert (root / "catalog" / PART / "CARD.md").is_file()
    assert not (root / "intake" / PART).exists()  # moved, not copied
    assert (root / "intake" / "PROMOTIONS.md").is_file()  # pointer left behind
    registry = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    assert [e["part_id"] for e in registry] == ["PRT-EX01"]  # registry rebuilt


def test_missing_candidate_is_reported(tmp_path: Path) -> None:
    root = _store_with_candidate(tmp_path, certified=True)
    status, _ = promote.promote("no-such-part", root, when="2026-08-02")
    assert status == "missing"


def test_certification_gaps_names_each_problem() -> None:
    card = sl.Card(slug="x", path=Path("x"), data={"maturity": "CANDIDATE"})
    gaps = promote.certification_gaps(card)
    assert any("rd_certification" in g for g in gaps)
    assert any("CERTIFIED" in g for g in gaps)
