"""promote -- move a candidate from intake/ to catalog/ ONLY on an R&D verdict.

This is the submission pipeline's one-way valve. A candidate lives in
``intake/<slug>/``; it reaches ``catalog/<slug>/`` at CERTIFIED only when its card
carries an ``[rd_certification]`` record with the Factory verdict
``HARDWARE_STORE_PART`` and an ``RD-####`` id. No stream self-certifies; this tool
refuses anything R&D has not blessed.

    python -m hardware_store.promote <slug> [--root DIR] [--when YYYY-MM-DD]

The move preserves history (``git mv`` when the Store is a git repo) and leaves a
pointer in ``intake/PROMOTIONS.md`` (move-with-pointer; nothing is destroyed).
After the move it rebuilds ``registry.json`` so the Store stays mirror-green.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from hardware_store import store_lib as sl
else:
    from . import store_lib as sl

CERT_VERDICT = "HARDWARE_STORE_PART"


def certification_gaps(card: sl.Card) -> list[str]:
    """Reasons this candidate is NOT eligible for promotion. Empty means eligible."""
    gaps: list[str] = []
    cert = card.data.get("rd_certification") or {}
    if not cert:
        gaps.append("no [rd_certification] record (R&D has not issued a verdict)")
    else:
        if not str(cert.get("rd_id", "")).strip():
            gaps.append("[rd_certification] has no rd_id (the RD-#### line id)")
        if str(cert.get("verdict", "")).strip() != CERT_VERDICT:
            gaps.append(f"[rd_certification].verdict is not {CERT_VERDICT}")
    if card.maturity not in sl.CERTIFIED_MATURITIES:
        gaps.append(f"maturity is '{card.maturity}', not CERTIFIED/FLEET_CORE")
    return gaps


def _git_move(src: Path, dst: Path, root: Path) -> bool:
    """Try to move with git (history-preserving). Returns False if not a git repo."""
    if not (root / ".git").exists():
        return False
    proc = subprocess.run(["git", "-C", str(root), "mv", str(src), str(dst)],
                          capture_output=True, text=True)
    return proc.returncode == 0


def promote(slug: str, root: Path, when: str) -> tuple[str, list[str]]:
    """Promote a candidate. Returns (status, gaps). status in promoted/refused/missing."""
    src = root / "intake" / slug
    card_path = src / "CARD.md"
    if not card_path.is_file():
        return "missing", [f"no candidate at intake/{slug}/CARD.md"]

    card = sl.load_card(card_path)
    gaps = certification_gaps(card)
    if gaps:
        return "refused", gaps

    dst = root / "catalog" / slug
    if dst.exists():
        return "refused", [f"catalog/{slug} already exists"]

    dst.parent.mkdir(parents=True, exist_ok=True)
    if not _git_move(src, dst, root):
        import shutil
        shutil.move(str(src), str(dst))

    cert = card.data.get("rd_certification", {})
    pointer = root / "intake" / "PROMOTIONS.md"
    header = "" if pointer.exists() else "# Promotions (move-with-pointer log)\n\n"
    with pointer.open("a", encoding="utf-8") as fh:
        fh.write(f"{header}- {when}: intake/{slug}/ -> catalog/{slug}/ "
                 f"(rd_id={cert.get('rd_id')}, verdict={cert.get('verdict')})\n")

    sl.write_registry(root)
    return "promoted", []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote an R&D-certified candidate into the catalog.")
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("slug", help="the candidate's intake/ slug")
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--when", default="unstamped",
                        help="ISO date for the promotion pointer (callers/CI pass real time)")
    args = parser.parse_args(argv)

    status, gaps = promote(args.slug, args.root.resolve(), args.when)
    if status == "promoted":
        print(f"promoted: intake/{args.slug} -> catalog/{args.slug}; registry.json rebuilt")
        print("next: run 'store-check' to confirm the Store is green")
        return 0
    print(f"REFUSED to promote '{args.slug}':", file=sys.stderr)
    for gap in gaps:
        print(f"  - {gap}", file=sys.stderr)
    print("only R&D's HARDWARE_STORE_PART verdict promotes a candidate.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
