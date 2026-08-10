"""store_check -- the Hardware Store integrity gate. The no-graveyard law, enforced.

Run it against a Store root; it returns a verdict, never a shrug:

    python -m hardware_store.store_check [--root DIR] [--fleet-root DIR]
                               [--threshold N] [--no-run-tests] [--json]

Checks (each one has a sabotage fixture that watches it fail; a checker you never
watched fail is unproven):

  registry-parses      registry.json is valid JSON.
  registry-mirror      registry.json exactly mirrors catalog/ (no ghosts, no unlisted).
  card-schema          every card parses and carries the required fields + valid enums.
  impl-exists          every listed implementation path exists on disk.
  tests-exist          every Part has a contract test suite ...
  tests-pass           ... and it passes against the code (CMD: pytest).
  certified-gate       CERTIFIED/FLEET_CORE need rd_certification + a real consumer +
                       a mutation score at/above the threshold.
  consumer-resolves    each listed consumer path exists and carries the Part's provenance id.
  no-deprecated-vocab  no retired fleet vocabulary anywhere in the Store.

Exit 0 unless the Store has a FAIL. An UNVERIFIED consumer needs its sibling
repository checked out before the gate can make an attributed claim.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Allow both ``python -m hardware_store.store_check`` and ``python tools/store_check.py``.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from hardware_store import store_lib as sl
else:
    from . import store_lib as sl


SKIP_DIRS = {".git", ".venv", "__pycache__", ".mypy_cache", ".ruff_cache",
             ".pytest_cache", "node_modules"}


def _catalog_dir(root: Path) -> Path:
    return root / "catalog"


# --- Individual checks (each appends findings to the shared Report) ----------

def check_registry(root: Path, report: sl.Report) -> list[dict] | None:
    """registry.json parses; return the parsed entries (None if unparseable)."""
    reg_path = root / "registry.json"
    if not reg_path.is_file():
        report.note("registry-parses", "-", "registry.json is missing")
        return None
    try:
        entries = json.loads(reg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.note("registry-parses", "-", f"registry.json is not valid JSON: {exc}")
        return None
    if not isinstance(entries, list):
        report.note("registry-parses", "-", "registry.json must be a JSON array")
        return None
    return entries


def check_cards(root: Path, report: sl.Report) -> list[sl.Card]:
    """Load cards; malformed front-matter is a fail, not a crash."""
    cards: list[sl.Card] = []
    catalog = _catalog_dir(root)
    for card_path in sorted(catalog.glob("*/CARD.md")):
        try:
            cards.append(sl.load_card(card_path))
        except sl.CardError as exc:
            report.note("card-schema", card_path.parent.name, str(exc))
    return cards


def check_schema(cards: list[sl.Card], report: sl.Report) -> None:
    for card in cards:
        for missing in (f for f in sl.REQUIRED_FIELDS if not card.data.get(f)):
            report.note("card-schema", card.slug, f"missing required field '{missing}'")
        if card.data.get("category") not in sl.CATEGORIES:
            report.note("card-schema", card.slug,
                        f"category '{card.data.get('category')}' is not a known "
                        "capability category")
        if card.maturity not in sl.MATURITIES:
            report.note("card-schema", card.slug,
                        f"maturity '{card.maturity}' is not on the ladder {sl.MATURITIES}")


def check_registry_mirror(root: Path, entries: list[dict], cards: list[sl.Card],
                          report: sl.Report) -> None:
    expected = sl.build_registry(cards)
    if sl.canonical_registry(entries) != sl.canonical_registry(expected):
        want_ids = {e["part_id"] for e in expected}
        have_ids = {e.get("part_id", "") for e in entries}
        for ghost in sorted(have_ids - want_ids):
            report.note("registry-mirror", ghost or "-",
                        "registry.json lists a part with no catalog/ card (ghost entry)")
        for missing in sorted(want_ids - have_ids):
            report.note("registry-mirror", missing,
                        "catalog/ card is not listed in registry.json (unlisted card)")
        if want_ids == have_ids:
            report.note("registry-mirror", "-",
                        "registry.json is stale: same parts, but a field disagrees with the cards")


def check_impls(root: Path, cards: list[sl.Card], report: sl.Report) -> None:
    for card in cards:
        if not card.implementations:
            report.note("impl-exists", card.slug,
                        "card lists no implementations (a card with no code)")
        for impl in card.implementations:
            rel = str(impl.get("path", "")).strip()
            if not rel:
                report.note("impl-exists", card.slug, "an implementation has no path")
                continue
            if not (card.path.parent / rel).exists():
                report.note("impl-exists", card.slug,
                            f"implementation path does not exist: {rel}")


def check_tests(root: Path, cards: list[sl.Card], run_tests: bool, report: sl.Report) -> None:
    for card in cards:
        tests_dir = card.path.parent / "tests"
        test_files = list(tests_dir.glob("test_*.py")) if tests_dir.is_dir() else []
        if not test_files:
            report.note("tests-exist", card.slug,
                        "no contract tests (tests/test_*.py) - an implementation "
                        "without tests is a defect")
            continue
        if not run_tests:
            continue
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(tests_dir)],
            capture_output=True, text=True, cwd=card.path.parent,
        )
        if proc.returncode != 0:
            tail = (proc.stdout + proc.stderr).strip().splitlines()[-1:] or ["(no output)"]
            report.note("tests-pass", card.slug, f"contract tests failed: {tail[-1]}")


def check_certified_gate(cards: list[sl.Card], threshold: int, report: sl.Report) -> None:
    for card in (c for c in cards if c.is_certified):
        if not card.data.get("rd_certification"):
            report.note("certified-gate", card.slug,
                        f"{card.maturity} without an rd_certification record - only R&D certifies")
        if not card.consumers:
            report.note("certified-gate", card.slug,
                        f"{card.maturity} with no current_consumers - a Part "
                        "nobody uses is a graveyard entry")
        if card.mutation_score < threshold:
            report.note("certified-gate", card.slug,
                        f"{card.maturity} mutation score {card.mutation_score:g}% is below the "
                        f"{threshold}% threshold (tests do not bite)")


def check_consumers_resolve(cards: list[sl.Card], fleet_root: Path, report: sl.Report) -> None:
    for card in (c for c in cards if c.is_certified):
        for consumer in card.consumers:
            path = str(consumer.get("path", "")).strip()
            if not path:
                report.note("consumer-resolves", card.slug, "a consumer has no path")
                continue
            consumer_repo = str(consumer.get("repo", "")).strip()
            if consumer_repo and not (fleet_root / consumer_repo).is_dir():
                report.note(
                    "consumer-resolves",
                    card.slug,
                    f"consumer repository is not present under the fleet root: {consumer_repo}",
                    severity="unverified",
                )
                continue
            target = fleet_root / path
            if not target.exists():
                report.note("consumer-resolves", card.slug,
                            f"consumer path does not exist under the fleet root: {path}")
                continue
            if not _path_imports_part(target, card):
                report.note("consumer-resolves", card.slug,
                            f"consumer {path} lacks a matching provenance citation for "
                            f"{card.part_id}", severity="warn")


def _path_imports_part(target: Path, card: sl.Card) -> bool:
    """True if the consumer file/dir cites the Part's exact permanent identity."""
    part_id = card.part_id.strip()
    if not part_id:
        return False
    citation = re.compile(rf"(?<![A-Za-z0-9]){re.escape(part_id)}(?![A-Za-z0-9])")
    files = [target] if target.is_file() else [p for p in target.rglob("*.py")
                                               if not (SKIP_DIRS & set(p.parts))]
    for py in files:
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if citation.search(text):
            return True
    return False


def check_no_deprecated_vocab(root: Path, report: sl.Report) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or SKIP_DIRS & set(path.relative_to(root).parts):
            continue
        if path.suffix.lower() not in {".md", ".py", ".toml", ".json", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        # This module names the banned words to enforce them; don't flag itself.
        if path.name in {"store_lib.py", "store_check.py"}:
            continue
        for word in sl.DEPRECATED_VOCAB:
            if _contains_word(text, word):
                report.note("no-deprecated-vocab", str(path.relative_to(root)),
                            f"deprecated fleet vocabulary '{word}' appears in the Store")
                break


def _contains_word(text: str, word: str) -> bool:
    import re
    return re.search(rf"\b{re.escape(word)}\b", text, flags=re.IGNORECASE) is not None


# --- Orchestration -----------------------------------------------------------

def run_check(root: Path, fleet_root: Path, threshold: int, run_tests: bool,
              check_consumers: bool = True) -> sl.Report:
    report = sl.Report()
    entries = check_registry(root, report)
    cards = check_cards(root, report)
    check_schema(cards, report)
    if entries is not None:
        check_registry_mirror(root, entries, cards, report)
    check_impls(root, cards, report)
    check_tests(root, cards, run_tests, report)
    check_certified_gate(cards, threshold, report)
    if check_consumers:
        check_consumers_resolve(cards, fleet_root, report)
    elif any(card.is_certified for card in cards):
        report.note(
            "consumer-resolves",
            "-",
            "consumer provenance not verified: fleet root was not supplied (--no-fleet)",
            severity="warn",
        )
    check_no_deprecated_vocab(root, report)
    return report


def _unverified(report: sl.Report) -> list[sl.Finding]:
    """Findings whose truth depends on a sibling repository not being available."""
    return [f for f in report.findings if f.severity == "unverified"]


def _verdict(report: sl.Report) -> str:
    """The rendered verdict keeps unverified evidence distinct from pass and fail."""
    if report.failures:
        return "FAIL"
    if _unverified(report):
        return "UNVERIFIED"
    return "PASS"


def render(report: sl.Report, root: Path) -> str:
    lines = [f"Hardware Store integrity check :: {root}"]
    if not report.findings:
        lines.append("  no findings - the Store is clean")
    for f in report.failures:
        lines.append(f"  FAIL [{f.check}] {f.part}: {f.message}")
    for f in report.warnings:
        lines.append(f"  WARN [{f.check}] {f.part}: {f.message}")
    for f in _unverified(report):
        lines.append(f"  UNVERIFIED [{f.check}] {f.part}: {f.message}")
    verdict = _verdict(report)
    summary = f"({len(report.failures)} failing, {len(report.warnings)} warning)"
    if _unverified(report):
        summary = f"{summary[:-1]}, {len(_unverified(report))} unverified)"
    lines.append(f"VERDICT: {verdict} {summary}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hardware Store integrity gate.")
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--root", type=Path, default=default_root,
                        help="Store root (dir holding catalog/ and registry.json)")
    parser.add_argument("--fleet-root", type=Path, default=None,
                        help="fleet root for resolving consumer paths (default: Store's parent)")
    parser.add_argument("--threshold", type=int, default=sl.DEFAULT_MUTATION_THRESHOLD,
                        help="minimum mutation score for CERTIFIED parts")
    parser.add_argument("--no-run-tests", action="store_true",
                        help="check that contract tests EXIST but do not run them")
    parser.add_argument("--no-fleet", action="store_true",
                        help="skip consumer-resolution (for CI, where the consuming fleet repos "
                             "are not checked out); Store-internal integrity and that each "
                             "certified card DECLARES a consumer are still enforced")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    fleet_root = (args.fleet_root or root.parent).resolve()
    report = run_check(root, fleet_root, args.threshold, run_tests=not args.no_run_tests,
                       check_consumers=not args.no_fleet)

    if args.json:
        print(json.dumps({
            "root": str(root), "verdict": _verdict(report),
            "findings": [f.__dict__ for f in report.findings],
        }, indent=2))
    else:
        print(render(report, root))
    return 1 if _verdict(report) == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
