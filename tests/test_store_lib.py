"""Proof for store_lib: front-matter parsing accepts good cards, refuses bad ones."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import store_lib as sl

PASS_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pass"

GOOD = '+++\npart_id = "PRT-1"\n+++\n\n# body\n'


def test_parses_good_front_matter() -> None:
    assert sl.parse_front_matter(GOOD)["part_id"] == "PRT-1"


def test_refuses_missing_opening_fence() -> None:
    with pytest.raises(sl.CardError):
        sl.parse_front_matter("# no front matter here\n")


def test_refuses_unterminated_fence() -> None:
    with pytest.raises(sl.CardError):
        sl.parse_front_matter('+++\npart_id = "PRT-1"\n')


def test_refuses_invalid_toml() -> None:
    with pytest.raises(sl.CardError):
        sl.parse_front_matter("+++\nthis is = = not toml\n+++\n")


def test_build_registry_mirrors_the_card() -> None:
    cards = sl.load_cards(PASS_FIXTURE / "catalog")
    reg = sl.build_registry(cards)
    assert len(reg) == 1
    assert reg[0]["part_id"] == "PRT-EX01"
    assert reg[0]["languages"] == ["python"]
    assert reg[0]["consumers"] == []


def test_candidate_card_is_not_certified() -> None:
    card = sl.load_cards(PASS_FIXTURE / "catalog")[0]
    assert card.maturity == "CANDIDATE"
    assert card.is_certified is False
