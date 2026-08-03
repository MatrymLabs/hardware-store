"""consume_first -- the stream-side gate: prove you looked before you rebuild.

A stream repo runs this in CI over its changed files. It enforces law #3
(consume first, and prove you looked): if a changed file looks like it
re-implements a capability the Store already catalogs, the build fails unless the
stream either (a) has a logged ``store_search`` for that capability, or (b) writes
a ``DECISION:`` comment in the file explaining why it is not consuming the Part.
Never silently.

    python -m hardware_store.consume_first \\
        --registry <store>/registry.json \\
        --search-log <store>/intake/search_log.jsonl \\
        --repo my-repo --changed a.py b.py

Exit 0 if clean or every flag is overridden; 1 if a probable reimplementation
lands with neither a logged search nor a DECISION.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from hardware_store import store_lib as sl
else:
    from . import store_lib as sl


@dataclass(frozen=True)
class Flag:
    """A changed file that probably reimplements a catalogued capability."""

    file: str
    capability_slug: str
    keyword: str
    overridden_by: str  # "" if not overridden; else "DECISION" or "search-log"


def capability_keywords(registry: list[dict]) -> dict[str, set[str]]:
    """Map each catalogued Part slug to the significant tokens that betray a reimplementation.

    Names are split on ``_``/``-`` into tokens; only tokens longer than three chars
    are kept, so matching is on membership (``retry`` in ``retry_call``) rather than a
    word-boundary regex (which underscores defeat) and short/common tokens don't misfire.
    """
    keywords: dict[str, set[str]] = {}
    for entry in registry:
        slug = entry.get("slug", "")
        words: set[str] = set()
        for name in (slug, entry.get("canonical_name", "")):
            words.update(t.lower() for t in re.split(r"[_\-]", name) if len(t) > 3)
        keywords[slug] = words
    return keywords


def _tokens(text: str) -> set[str]:
    return set(re.split(r"[^a-z0-9]+", text.lower()))


def _searched(search_log: Path, repo: str) -> bool:
    """Did this repo log any store_search? (proof it consulted the Store)."""
    if not search_log.is_file():
        return False
    for line in search_log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("repo") == repo:
            return True
    return False


def _has_decision(text: str) -> bool:
    return re.search(r"(?im)^\s*#?\s*DECISION\s*:", text) is not None


def scan(changed: list[Path], registry: list[dict], search_log: Path,
         repo: str) -> list[Flag]:
    keywords = capability_keywords(registry)
    searched = _searched(search_log, repo)
    flags: list[Flag] = []
    for path in changed:
        if path.suffix != ".py" or not path.is_file():
            continue
        body = path.read_text(encoding="utf-8", errors="ignore")
        tokens = _tokens(path.stem + " " + body)
        for slug, words in keywords.items():
            hit = next((w for w in words if w in tokens), None)
            if not hit:
                continue
            override = ("DECISION" if _has_decision(body)
                        else "search-log" if searched else "")
            flags.append(Flag(str(path), slug, hit, override))
            break  # one flag per file is enough to make the point
    return flags


def render(flags: list[Flag]) -> tuple[str, int]:
    unresolved = [f for f in flags if not f.overridden_by]
    lines = ["consume-first check"]
    for f in flags:
        if f.overridden_by:
            lines.append(f"  OK   {f.file}: matches catalogued '{f.capability_slug}' "
                         f"(overridden by {f.overridden_by})")
        else:
            lines.append(f"  FAIL {f.file}: probable reimplementation of catalogued "
                         f"'{f.capability_slug}' (keyword '{f.keyword}') - no logged "
                         "store_search and no DECISION: override")
    if not flags:
        lines.append("  no changed file resembles a catalogued capability")
    verdict = "FAIL" if unresolved else "PASS"
    lines.append(f"VERDICT: {verdict} ({len(unresolved)} unresolved of {len(flags)} flagged)")
    return "\n".join(lines), (1 if unresolved else 0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consume-first CI gate for a stream repo.")
    parser.add_argument("--registry", type=Path, required=True,
                        help="path to the Store's registry.json")
    parser.add_argument("--search-log", type=Path, required=True,
                        help="path to the Store's intake/search_log.jsonl")
    parser.add_argument("--repo", required=True,
                        help="the stream repo name (matches the search log)")
    parser.add_argument("--changed", nargs="*", type=Path, default=[],
                        help="changed files (CI computes via git diff --name-only)")
    args = parser.parse_args(argv)

    registry = sl.load_registry(args.registry) if args.registry.is_file() else []
    flags = scan(args.changed, registry, args.search_log, args.repo)
    text, code = render(flags)
    print(text)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
