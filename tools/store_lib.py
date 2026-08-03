"""store_lib -- the Hardware Store's shared core: card parsing, schema, registry, verdicts.

The Store catalogs engineering CAPABILITY, not technology. Every Part is a directory
under ``catalog/`` carrying a CARD.md whose ``+++``-fenced TOML front-matter is the
machine-readable card. ``registry.json`` is the aggregated index built from those cards.

This module has one job: turn the on-disk Store into typed objects the three tools
(store_check, store_search, consume) reason over. Pure stdlib, no third-party deps:
front-matter is TOML (stdlib ``tomllib``), the index is JSON (stdlib ``json``).
"""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# --- The card contract -------------------------------------------------------

#: Categories a Part may be filed under (capability domains, not technologies).
CATEGORIES: tuple[str, ...] = (
    "Domain", "Application", "Interface", "Data", "Client", "Integration", "AI",
    "Operations", "Security", "Accessibility", "Validation", "Generator",
    "Development", "Game", "Simulation", "Pattern",
)

#: The maturity ladder. Promotion up it is R&D's call, never a stream's.
MATURITIES: tuple[str, ...] = ("CANDIDATE", "CERTIFIED", "FLEET_CORE", "DEPRECATED")

#: Maturities that must clear the certification gate (rd_certification + real
#: consumer + mutation score at/above threshold).
CERTIFIED_MATURITIES: frozenset[str] = frozenset({"CERTIFIED", "FLEET_CORE"})

#: Fields every card must carry, whatever its maturity.
REQUIRED_FIELDS: tuple[str, ...] = (
    "part_id", "canonical_name", "capability", "category", "maturity",
    "contract", "failure_modes", "tests", "provenance", "implementations",
)

#: Deprecated fleet vocabulary. Banned anywhere in the Store (style_guide.md).
DEPRECATED_VOCAB: tuple[str, ...] = (
    "Borg", "Assimilation", "Collective", "Drone", "Hive", "Cube", "Veritas",
)

#: A CERTIFIED Part's tests must bite at least this hard (percent), fleet default.
DEFAULT_MUTATION_THRESHOLD: int = 70

FRONT_MATTER_FENCE = "+++"


class CardError(ValueError):
    """A CARD.md that cannot be parsed into a valid card."""


# --- Typed card + verdict objects -------------------------------------------

@dataclass(frozen=True)
class Card:
    """One parsed Hardware Card: its slug, path, and front-matter mapping."""

    slug: str
    path: Path
    data: dict

    @property
    def part_id(self) -> str:
        return str(self.data.get("part_id", ""))

    @property
    def canonical_name(self) -> str:
        return str(self.data.get("canonical_name", ""))

    @property
    def maturity(self) -> str:
        return str(self.data.get("maturity", ""))

    @property
    def is_certified(self) -> bool:
        return self.maturity in CERTIFIED_MATURITIES

    @property
    def implementations(self) -> list[dict]:
        impls = self.data.get("implementations", [])
        return list(impls) if isinstance(impls, list) else []

    @property
    def languages(self) -> list[str]:
        return [str(i.get("language", "")) for i in self.implementations]

    @property
    def consumers(self) -> list[dict]:
        cons = self.data.get("current_consumers", [])
        return list(cons) if isinstance(cons, list) else []

    @property
    def mutation_score(self) -> float:
        tests = self.data.get("tests", {})
        try:
            return float(tests.get("mutation_score", 0))
        except (TypeError, ValueError):
            return 0.0


@dataclass(frozen=True)
class Finding:
    """One thing the checker noticed. Severity is 'fail' or 'warn'."""

    check: str
    part: str
    message: str
    severity: str = "fail"


@dataclass
class Report:
    """A read-only verdict over the Store. Verdicts, never bare booleans."""

    findings: list[Finding] = field(default_factory=list)

    def note(self, check: str, part: str, message: str, severity: str = "fail") -> None:
        self.findings.append(Finding(check, part, message, severity))

    @property
    def failures(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "fail"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warn"]

    @property
    def verdict(self) -> str:
        return "FAIL" if self.failures else "PASS"


# --- Parsing the Store off disk ---------------------------------------------

def parse_front_matter(text: str, source: str = "<card>") -> dict:
    """Extract and parse the ``+++``-fenced TOML front-matter from a card body."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONT_MATTER_FENCE:
        raise CardError(f"{source}: missing opening '{FRONT_MATTER_FENCE}' front-matter fence")
    try:
        close = next(i for i in range(1, len(lines)) if lines[i].strip() == FRONT_MATTER_FENCE)
    except StopIteration:
        raise CardError(f"{source}: unterminated front-matter fence") from None
    block = "\n".join(lines[1:close])
    try:
        return tomllib.loads(block)
    except tomllib.TOMLDecodeError as exc:
        raise CardError(f"{source}: invalid TOML front-matter: {exc}") from exc


def load_card(card_path: Path) -> Card:
    """Parse a single CARD.md into a :class:`Card` (slug = its parent dir name)."""
    text = card_path.read_text(encoding="utf-8")
    data = parse_front_matter(text, source=str(card_path))
    return Card(slug=card_path.parent.name, path=card_path, data=data)


def load_cards(catalog_dir: Path) -> list[Card]:
    """Load every ``catalog/<slug>/CARD.md`` under ``catalog_dir`` (sorted by slug)."""
    if not catalog_dir.is_dir():
        return []
    cards = [load_card(p) for p in sorted(catalog_dir.glob("*/CARD.md"))]
    return cards


def registry_entry(card: Card) -> dict:
    """The index row for a card: the fields agents query, nothing more."""
    impls = card.implementations
    version = str(impls[0].get("version", "")) if impls else ""
    return {
        "part_id": card.part_id,
        "slug": card.slug,
        "canonical_name": str(card.data.get("canonical_name", "")),
        "capability": str(card.data.get("capability", "")),
        "category": str(card.data.get("category", "")),
        "maturity": card.maturity,
        "languages": card.languages,
        "consumers": [str(c.get("repo", "")) for c in card.consumers],
        "version": version,
    }


def build_registry(cards: list[Card]) -> list[dict]:
    """Aggregate cards into the machine-readable index, ordered by part_id."""
    return sorted((registry_entry(c) for c in cards), key=lambda e: e["part_id"])


def load_registry(registry_path: Path) -> list[dict]:
    """Load registry.json (returns [] if absent). Raises on malformed JSON."""
    if not registry_path.is_file():
        return []
    return json.loads(registry_path.read_text(encoding="utf-8"))


def canonical_registry(entries: list[dict]) -> str:
    """A stable string form of the registry for exact mirror comparison."""
    return json.dumps(sorted(entries, key=lambda e: e.get("part_id", "")),
                      sort_keys=True, indent=2)
