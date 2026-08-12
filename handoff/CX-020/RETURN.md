# RETURN CX-020

status: COMPLETE
tests_passing: yes

The amended allowlist authorizes the catalogue-coverage correction. STUDIED entries are explicitly
exempt; CANDIDATE and CERTIFIED entries remain required to have runnable contract tests.

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
........................................................................ [ 42%]
........................................................................ [ 84%]
...........................                                              [100%]
171 passed in 4.16s
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m hardware_store.store_check
Hardware Store integrity check :: /home/josh/Projects/MatrymLabs/hardware-store-codex
VERDICT: PASS (0 failing, 26 warning)
```

The targeted store integrity check itself passes, with the expected STUDIED skip warnings:

```text
Hardware Store integrity check :: /home/josh/Projects/MatrymLabs/hardware-store-codex
VERDICT: PASS (0 failing, 26 warning)
```

## Scope and diff

The thirteen new `catalog/*/CARD.md` files, the allowlisted `registry.json` mirror, the amended
allowlisted catalogue-coverage test, and this RETURN are the only changed paths. No existing card
or `hardware_store/` file was modified.

```text
 handoff/CX-020/RETURN.md                | 94 ++++++++++++++++++++-------------
 tests/test_gate_covers_the_catalogue.py | 10 +++-
 2 files changed, 65 insertions(+), 39 deletions(-)
```

The earlier card and registry commit is unchanged; this repair commit touches only the
allowlisted test and RETURN.

## Reuse search

Both tiers were searched before writing. Certified Tier (`hardware-store/catalog/`): nine
directories, seven carded, no Part covering any of these subjects. Working Shelf
(`codeforge/catalog/parts.yaml`, 104 entries): nearest `weighted-table`, `zone-scheduler`, and
`minimap`; none is a tilemap, save-slot, text-encoding, frame-budget, or related Part. No Part was
consumed.

## Calibration transitions

The maturity guard was calibrated by temporarily changing `metatile-hierarchy` from STUDIED to
CANDIDATE. The test failed as required:

```text
........F.
FAILED tests/test_gate_covers_the_catalogue.py::test_every_part_in_the_registry_has_contract_tests
AssertionError: registered Parts with no contract tests: ['metatile-hierarchy']
1 failed, 9 passed
```

After restoring STUDIED, the same test file passed:

```text
..........                                                               [100%]
10 passed in 3.15s
```

The taint calibration from the original implementation remains valid and is retained below.

## Unverified

CI has not been independently rerun in this session; the command that resolves that is the
repository's pull-request CI workflow on the merge commit.

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
- Verdict note: COMPLETE. The explicit STUDIED exemption is guarded by a failing CANDIDATE
  transition, and the full local gate passes.
