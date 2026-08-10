"""store_search -- search the catalog by capability, and record that you looked.

Consume-first is a law, not a hope: before a stream implements a capability it
searches the Store, and the search is logged. Reimplementing a catalogued
capability without a documented reason is a CI-detectable defect (Phase 2). This
tool is the front door to that discipline.

    python -m hardware_store.store_search "rate limiting" [--category Operations]
                                 [--language python] [--repo my-repo] [--json]

Matches are ranked by where the term hits (capability > name > category). Every
query is appended to ``intake/search_log.jsonl`` so the record exists.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from hardware_store import store_lib as sl
else:
    from . import store_lib as sl


def search(cards: list[sl.Card], term: str, category: str | None,
           language: str | None) -> list[tuple[int, sl.Card]]:
    """Return (score, card) for cards matching the query, best score first."""
    # Match on ANY term, not the whole phrase as one literal.
    #
    # Until 2026-08-10 the query was a single substring, so every multi-word search missed. The
    # certified `typed-settings` Part could not be found by its own canonical name: `settings`
    # returned it, `typed settings` returned "no catalogued Part matches", which reads as
    # permission to build one. A consume-first rule whose search says a thing does not exist
    # CAUSES the duplication it exists to prevent, and this defect was found while following that
    # rule for real.
    terms = [w for w in term.lower().split() if w]
    hits: list[tuple[int, sl.Card]] = []
    for card in cards:
        if category and card.data.get("category") != category:
            continue
        if language and language not in card.languages:
            continue
        score = 0
        if terms:
            capability = str(card.data.get("capability", "")).lower()
            names = f"{card.canonical_name.lower()} {card.slug.lower()}"
            kind = str(card.data.get("category", "")).lower()
            for word in terms:
                if word in capability:
                    score += 3
                if word in names:
                    score += 2
                if word in kind:
                    score += 1
            if score == 0:
                continue
        hits.append((score, card))
    return sorted(hits, key=lambda sc: (-sc[0], sc[1].slug))


def log_query(root: Path, term: str, category: str | None, language: str | None,
              repo: str | None, result_count: int, stamp: str,
              log_file: Path | None = None) -> Path:
    """Append the query to the search log so 'we looked' is a record, not a claim.

    A stream repo passes ``log_file`` to write into its own committed log (which its
    consume-first CI reads); the Store itself uses the default ``intake/`` log.
    """
    log_path = log_file if log_file is not None else root / "intake" / "search_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "when": stamp, "repo": repo or "unknown", "term": term,
        "category": category, "language": language, "results": result_count,
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    return log_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search the Hardware Store catalog.")
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("term", nargs="?", default="", help="capability search term")
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--category", default=None, choices=(None, *sl.CATEGORIES))
    parser.add_argument("--language", default=None, help="filter by implementation language")
    parser.add_argument("--repo", default=None, help="the searching repo (recorded in the log)")
    parser.add_argument("--log-file", type=Path, default=None,
                        help="write the query here instead of the Store's intake/ log "
                             "(a stream points this at its own committed log)")
    parser.add_argument("--when", default=None,
                        help="ISO timestamp for the log entry (default: 'unstamped'; "
                             "callers/CI pass the real time so the tool stays deterministic)")
    parser.add_argument("--no-log", action="store_true", help="do not record the query")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    cards = sl.load_cards(root / "catalog")
    results = search(cards, args.term, args.category, args.language)

    if not args.no_log:
        log_query(root, args.term, args.category, args.language, args.repo,
                  len(results), args.when or "unstamped", log_file=args.log_file)

    if args.json:
        print(json.dumps([sl.registry_entry(c) for _, c in results], indent=2))
    else:
        if not results:
            print(f"no catalogued Part matches '{args.term}' "
                  "(if you build one, that's a submission, not a duplicate)")
        for _score, card in results:
            print(f"  [{card.maturity:9}] {card.slug} :: {card.data.get('capability', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
