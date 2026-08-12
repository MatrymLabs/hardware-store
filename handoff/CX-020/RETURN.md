# RETURN CX-020

status: BLOCKED
tests_passing: no

## Block

The required whole gate was run after adding the thirteen STUDIED cards and their registry
mirror. It fails because the existing catalogue-coverage test requires every registry entry to
have runnable contract tests, while this order explicitly forbids new test code and says STUDIED
cards have no contract tests. Resolving this requires changing a file outside the allowlist
(the gate test or the test policy), so work stops here without widening scope.

## Verification command (actual output)

Command:

```text
export PATH="/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin:$PATH"
make check PY=/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python
```

Output:

```text
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m ruff check .
All checks passed!
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m mypy hardware_store
Success: no issues found in 7 source files
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m pytest -q
.................F...................................................... [ 42%]
........................................................................ [ 84%]
...........................                                              [100%]
=================================== FAILURES ===================================
______________ test_every_part_in_the_registry_has_contract_tests ______________

    def test_every_part_in_the_registry_has_contract_tests() -> None:
        """A registry entry with no runnable contract is a claim with no evidence behind it."""
        import json

        registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
        entries = registry if isinstance(registry, list) else registry.get("parts", [])
        have = set(parts_with_contract_tests())
        missing = sorted(e["slug"] for e in entries if e.get("slug") and e["slug"] not in have)
>       assert not missing, f"registered Parts with no contract tests: {missing}"
E       AssertionError: registered Parts with no contract tests: ['bank-and-memory-map', 'checksummed-save-slot', 'compression-as-data-design', 'constrained-map-streaming', 'dictionary-text-encoding', 'frame-time-budget', 'layer-composition', 'metatile-hierarchy', 'offset-per-tile', 'palette-discipline', 'sprite-budget', 'tilemap-bit-packing', 'voluntary-budget']
E       assert not ['bank-and-memory-map', 'checksummed-save-slot', 'compression-as-data-design', 'constrained-map-streaming', 'dictionary-text-encoding', 'frame-time-budget', ...]

tests/test_gate_covers_the_catalogue.py:59: AssertionError
1 failed, 170 passed in 4.19s
make: *** [Makefile:32: test] Error 1
```

The targeted store integrity check itself passes, with the expected STUDIED skip warnings:

```text
Hardware Store integrity check :: /home/josh/Projects/MatrymLabs/hardware-store-codex
VERDICT: PASS (0 failing, 26 warning)
```

## Scope and diff

The only implementation paths changed are the thirteen new `catalog/*/CARD.md` files, the
allowlisted `registry.json` mirror, and this RETURN. No existing card, `hardware_store/`, or test
file was modified.

```text
git diff --stat
```

The new files are untracked until the blocked work is committed; `git status --short` lists only
the thirteen allowlisted card directories, `registry.json`, and this RETURN.

## Reuse search

Both tiers were searched before writing. Certified Tier (`hardware-store/catalog/`): nine
directories, seven carded, no Part covering any of these subjects. Working Shelf
(`codeforge/catalog/parts.yaml`, 104 entries): nearest `weighted-table`, `zone-scheduler`, and
`minimap`; none is a tilemap, save-slot, text-encoding, frame-budget, or related Part. No Part was
consumed.

## Unverified

The whole gate remains unverified as passing because of the allowlist contradiction. The required
searches and taint calibration did run and are recorded below.

```text
python -m hardware_store.store_search "" --no-log
python -m hardware_store.store_search "checksum"
```

Search output contained `[STUDIED]` for all thirteen new entries; the subject search returned the
checksummed-save-slot card:

```text
[STUDIED  ] bank-and-memory-map :: Assign data and code to explicit banks and memory regions, framing payloads so consumers can locate, load, and address them without hidden locality assumptions.
[STUDIED  ] checksummed-save-slot :: Validate a save slot with a checksum and treat any mismatch as an empty slot, ensuring corruption never presents as a playable character and the failure policy is deterministic.
[STUDIED  ] compression-as-data-design :: Choose LZSS, run-length encoding, or dictionary compression as part of data modeling, balancing decode cost, repetition, and storage budget instead of treating compression as a final opaque step.
[STUDIED  ] constrained-map-streaming :: Stream connected map regions through a bounded RAM window, loading the next region before traversal requires it and evicting safe regions without breaking connections.
[STUDIED  ] dictionary-text-encoding :: Store repeated dialogue phrases as dictionary tokens and expand them during rendering, trading a compact data stream for a controlled decode path and editable phrase vocabulary.
[STUDIED  ] frame-time-budget :: Give each frame a fixed execution budget and schedule work so rendering, input, streaming, and simulation meet that budget instead of allowing one subsystem to monopolize a frame.
[STUDIED  ] layer-composition :: Resolve visible pixels from ordered tile layers by priority, transparency, and occlusion, keeping background, foreground, and effect composition deterministic.
[STUDIED  ] metatile-hierarchy :: Compose small tiles into reusable 16x16 and 32x32 metatiles, so maps store repeated visual structure once while collision and decoration remain aligned.
[STUDIED  ] offset-per-tile :: Attach a small positional offset to each tile so one map representation can express effects such as shake, parallax, or irregular placement without rewriting the tile geometry.
[STUDIED  ] palette-discipline :: Treat fifteen visible colours plus transparent as a hard palette budget, assigning roles deliberately so art variation fits the target display and transparency remains unambiguous.
[STUDIED  ] sprite-budget :: Manage sprite and OAM residency under fixed per-frame and VRAM budgets, prioritizing visible or gameplay-critical actors when demand exceeds capacity.
[STUDIED  ] tilemap-bit-packing :: Pack tile index, palette selection, priority, and horizontal or vertical flip into one fixed-width map word, making tilemap storage compact and decoding deterministic.
[STUDIED  ] voluntary-budget :: Use a self-imposed resource or complexity budget as a design forcing function, making tradeoffs explicit before implementation and preserving room for future content.
[STUDIED  ] checksummed-save-slot :: Validate a save slot with a checksum and treat any mismatch as an empty slot, ensuring corruption never presents as a playable character and the failure policy is deterministic.
```

Calibration red (temporary card missing `taint_class`):

```text
FAIL [card-schema] checksummed-save-slot: STUDIED card missing required provenance field 'taint_class'
VERDICT: FAIL (1 failing, 26 warning)
```

Calibration green after restoring the temporary fixture:

```text
VERDICT: PASS (0 failing, 26 warning)
byte-identical: yes
```

## Extraction

The registry mirror has no generator (`make registry` does not exist and nothing in
`hardware_store/` writes it). It would have to be hand-edited once the gate contradiction is
resolved; this is an extraction signal for a future generator order.

## Pattern screen

- Lane echo: persistence, commands, events, transactions, world graph, integration — none
  observed in this schema/card-only change.
- Catalogue match: both reuse tiers were searched; no existing Part matched, and no Part was
  consumed.
- Recurrence check: the registry-mirror/test-coverage coupling has already blocked CX-012-style
  card changes; this is the same class of stale gate boundary.
- Verdict note: BLOCKED. The cards are within the stated allowlist, but `make check` cannot certify
  them without an out-of-allowlist gate or test-policy change.
