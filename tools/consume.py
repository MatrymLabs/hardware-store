"""consume -- record that a repo adopted a Part, onto the Part's own card.

Consumption is the other half of no-graveyard: a CERTIFIED Part must have at
least one real consumer. When a stream depends on a Part (pinned by version),
it runs this to append itself to the card's ``current_consumers`` table, so the
card tells the truth about who relies on it.

    python -m tools.consume <slug> --repo my-repo \\
        --path my-repo/src/foo.py --version 0.1.0

This mutates the CARD.md front-matter only (append a ``[[current_consumers]]``
table); it does not certify anything. Certification stays R&D's sole gate.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools import store_lib as sl
else:
    from . import store_lib as sl


def _toml_str(value: str) -> str:
    """Minimal TOML string escaping for the values we write."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_consumer_block(repo: str, path: str, version: str, when: str) -> str:
    return (
        "\n[[current_consumers]]\n"
        f"repo = {_toml_str(repo)}\n"
        f"path = {_toml_str(path)}\n"
        f"version = {_toml_str(version)}\n"
        f"adopted = {_toml_str(when)}\n"
    )


def already_recorded(card: sl.Card, repo: str, path: str) -> bool:
    return any(c.get("repo") == repo and c.get("path") == path for c in card.consumers)


def record_consumption(card_path: Path, repo: str, path: str, version: str,
                       when: str) -> str:
    """Append a consumer table to the card's front-matter. Returns a status word."""
    card = sl.load_card(card_path)
    if already_recorded(card, repo, path):
        return "already-recorded"
    text = card_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    # Find the closing +++ fence and insert just before it.
    fence_positions = [i for i, ln in enumerate(lines) if ln.strip() == sl.FRONT_MATTER_FENCE]
    if len(fence_positions) < 2:
        raise sl.CardError(f"{card_path}: cannot find a closed front-matter block")
    close = fence_positions[1]
    block = render_consumer_block(repo, path, version, when)
    lines.insert(close, block if block.startswith("\n") else "\n" + block)
    card_path.write_text("".join(lines), encoding="utf-8")
    return "recorded"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record a Part consumption on its card.")
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("slug", help="the Part's catalog slug")
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--repo", required=True, help="the consuming repo name")
    parser.add_argument("--path", required=True, help="fleet-relative path that imports the Part")
    parser.add_argument("--version", required=True, help="the pinned Part version consumed")
    parser.add_argument("--when", default="unstamped",
                        help="ISO timestamp (callers/CI pass real time; tool stays deterministic)")
    args = parser.parse_args(argv)

    card_path = args.root.resolve() / "catalog" / args.slug / "CARD.md"
    if not card_path.is_file():
        print(f"no such Part: {args.slug} (expected {card_path})", file=sys.stderr)
        return 2
    status = record_consumption(card_path, args.repo, args.path, args.version, args.when)
    print(f"{status}: {args.repo} -> {args.slug} @ {args.version}")
    print("note: run 'store_check' and rebuild registry.json; certification remains R&D's gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
