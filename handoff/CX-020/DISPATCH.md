# DISPATCH CX-020

**Status:** LANDED, hardware-store #48, 2026-08-12. Amended once after a correct Codex block, then re-verified independently: the CANDIDATE guard was re-run against registry.json, which is what the test actually reads.

```yaml
packet_id:            CX-020
title:                File the studied patterns as cards, so a search can find them
stream:               rd
owner:                Codex
reviewer:             Claude Code, who re-runs every command independently
merges:               founder
size:                 medium
taint_class: >
    SAFE. The source body is INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter, and the
    register classifies these fifteen patterns explicitly: "The fifteen engineering patterns, all
    SAFE, all UNCONSUMED." Verified before this order was written, because the charter's boundary is
    absolute: "NEVER may not be read by the spec-writer either, and may never reach Codex in any
    form." Nothing in this order is CAUTION or NEVER, and no research document is attached to it.
    You receive the specification below, never the body.

goal: >
    File thirteen studied patterns as `STUDIED` cards in the Certified Tier, so consume-first can
    find them. CX-019 landed the maturity that makes this possible; before it, every one of these
    cards produced four FAILs.

    THE INVARIANT, in prose and separate from the commands that test it: a pattern the Workshop has
    identified as useful is findable by search, and states honestly what it is. Doctrine 7b: "The
    card IS the deliverable of a study, and it is finished when the pattern is written down well
    enough that a future consumer could implement from the card alone." A card that merely names a
    pattern has not been written; it has been listed.

why_this_is_not_speculative_building: >
    It is worth stating, because the pull rule reads as if it forbids this. It does not. Doctrine
    section 7, founder override 2026-08-12: a useful pattern IS a Part, carrying the maturity it has
    earned. These reach `STUDIED`, which claims nothing beyond "studied and written down". None
    becomes CANDIDATE without an implementation and none becomes CERTIFIED without R&D, a real
    consumer and a mutation score. No code is written by this order at all.

out_of_scope: >
    WRITING ANY IMPLEMENTATION. This order produces cards, not modules. If a pattern looks easy to
    implement, that is a separate order and a separate decision; note it in the RETURN.

    RD-2026-0114 (event/trigger scripting VM) and RD-2026-0115 (flag/bit-array world state) are
    already INCORPORATED and are NOT carded here. Carding an incorporated finding would claim the
    Store holds something the engine already owns.

    RD-2026-0130 through RD-2026-0133 (Mesen2, ImHex, Ghidra, asar) are TOOLS, not patterns. A tool
    is not a Part. Leave them; they belong in a toolchain record if anywhere.

    RD-2026-0140 (RE skills curriculum) is a curriculum, not a pattern. Leave it.

    Do not touch `hardware_store/`, `store_check.py`, or any existing card.

preconditions: >
    CHECK: file hardware_store/store_lib.py contains STUDIED
    CHECK: file registry.json exists
    CHECK: file catalog/metatile-hierarchy absent

the_thirteen: >
    Each is one card. The `project_fit` column is the register's, kept because it tells a future
    consumer where the pattern is expected to earn its place.

      RD-2026-0110  metatile-hierarchy        8x8 to 16x16 to 32x32 composition           ARPG
      RD-2026-0111  tilemap-bit-packing       index, palette, priority, flip in one word  ARPG
      RD-2026-0112  layer-composition         layers and priority resolution              ARPG
      RD-2026-0113  compression-as-data-design LZSS, RLE, dictionary as a data decision   Both
      RD-2026-0116  constrained-map-streaming map connection and streaming under a RAM cap Both
      RD-2026-0117  palette-discipline        15 colours plus transparent as a constraint  ARPG
      RD-2026-0118  sprite-budget             sprite/OAM management and VRAM budgeting     ARPG
      RD-2026-0119  checksummed-save-slot     treat a bad checksum as an empty slot        Both
      RD-2026-0120  dictionary-text-encoding  DTE and compact dialogue storage             Both
      RD-2026-0121  bank-and-memory-map       data locality and payload framing            Both
      RD-2026-0122  frame-time-budget         a fixed per-frame budget that must be met    ARPG
      RD-2026-0123  offset-per-tile           per-tile offset effects; ideas only          ARPG
      RD-2026-0124  voluntary-budget          a self-imposed budget as a design forcing fn Both

    **RD-2026-0119 is the one to write first and best.** "Treat a bad checksum as an empty slot" is
    a complete failure-handling doctrine in six words: a corrupt save never presents as a playable
    save, so the player loses a session rather than a character. It is the closest of the thirteen
    to a Part this Workshop would actually consume, and if you can only write one well, write that
    one and block on the rest.

what_a_card_must_contain: >
    `capability` is the pattern in OUR words, stating what it does and the problem it solves, at the
    length the existing cards use. Read `catalog/source-monitor/CARD.md` for the register and shape.

    `failure_modes` is not optional and not "none". A studied pattern has known ways to go wrong and
    naming them is most of what makes the card worth reading. Where the failure mode is genuinely
    unknown, say "not yet characterised" and say why.

    `[provenance] source_studied` names the body, not a ROM: "INTAKE RUN 01 BODY 3, the ROM Hacking
    Research Lane Charter (RD-2026-01xx)". `taint_class = "SAFE"`. `clean_room` states that no
    proprietary source was read and no separation was required, which is true for this body and must
    not be claimed for any other.

    `category` is one of `CATEGORIES`. `"Pattern"` fits most of these; `"Data"` or `"Game"` may fit
    better for some. Choose per card and do not invent a category.

    `part_id` continues the existing sequence. `maturity = "STUDIED"`.

    **Write the pattern, not the platform.** "A tilemap entry packs index, palette, priority and flip
    into one word so a screen's worth of map fits a cache line" is a Part. "The SNES PPU has four
    background layers" is a hardware fact and belongs nowhere in this Store.

amendment_1: >
    AMENDED 2026-08-12, after Codex correctly BLOCKED on it for the third time in one day, and for
    the third time the fault is the order's.

    `tests/test_gate_covers_the_catalogue.py::test_every_part_in_the_registry_has_contract_tests`
    asserts that EVERY registry entry has runnable contract tests. It predates STUDIED and knows
    nothing about maturity: measured, `registry=4 maturity-aware=0`. Thirteen STUDIED entries have
    no contract by design, so it fails on all thirteen at once:

      AssertionError: registered Parts with no contract tests: ['bank-and-memory-map',
      'checksummed-save-slot', 'compression-as-data-design', ...]

    The order then forbade adding tests and excluded that file, so it required something it also
    forbade. That is the Dispatch Law's simultaneous-satisfiability half for the third time today.

    THE ROOT DEFECT IS CX-019's, NOT THIS ORDER'S. CX-019 taught `store_check` that a STUDIED card
    needs no code and its allowlist covered `tests/test_store_check.py` only. A SECOND test file
    asserts the same property from a different angle and nobody taught it. The habit is the one this
    Coordinator wrote into CX-010's amendment this afternoon and then repeated twice: scope an
    allowlist from the module being changed rather than from the set of artifacts that assert on its
    behaviour. `make packets` cannot catch it and does not claim to.

    The grep that would have caught it, run now rather than earlier:
      grep -rln 'registry' tests/   ->  test_promote, test_store_check, test_gate_covers_the_catalogue
      of those, maturity-aware:         test_promote yes, test_store_check yes, the third NO

contract_tests: >
    ONE change, and it is a correction to an existing test, not new test code.

    `test_every_part_in_the_registry_has_contract_tests` must exempt STUDIED entries. Its docstring
    reasoning stays true for everything else: "a registry entry with no runnable contract is a claim
    with no evidence behind it." A STUDIED entry makes no such claim; it claims to be a written-down
    pattern, which is why CX-019 gave it three provenance fields to satisfy instead.

    THE EXEMPTION MUST BE EXPLICIT AND ANNOUNCED, never a silent skip that quietly shrinks the
    population. Doctrine section 5: a silent exemption reads as coverage.

    Add, in the same file, the guard that keeps this from becoming "the test stopped asking":
      a CANDIDATE or CERTIFIED registry entry with no contract tests must STILL fail.
    Prove it by temporarily flipping one new card to CANDIDATE, watching the test fail, and flipping
    it back. Paste both transitions.

    Everything else in this order is unchanged: no implementation, no new Part tests, no code.

verification_command: |
    cd hardware-store
    make check
    .venv/bin/python -m hardware_store.store_search ""
    .venv/bin/python -m hardware_store.store_search "checksum"

definition_of_done: >
    Thirteen STUDIED cards; `registry.json` regenerated to mirror them; `make check` green over the
    whole instrument; both searches pasted, showing `[STUDIED]` beside the new entries and proving a
    term search finds a pattern by its subject rather than only by its slug; the calibration below
    pasted.

calibration_required: >
    Remove `taint_class` from ONE of the new cards, confirm `store_check` FAILS naming that card,
    restore, confirm PASS. Paste both. Confirm the card is byte-identical after restore.

    A gate that has never been observed to fail over THESE cards has not been observed over them.

rollback: >
    Revert the commit. Nothing consumes a STUDIED card and no code depends on one.

approval_gates: >
    None beyond the founder's merge. No code, no dependency, no interface change. The taint is SAFE
    and verified against the register before dispatch.

store_search_result: >
    Both tiers searched 2026-08-12; one tier logged is an incomplete search.
    Certified Tier (hardware-store/catalog/): nine directories, seven carded, zero matching any of
    the thirteen subjects. The Store holds no tilemap, save-slot, text-encoding or frame-budget Part.
    Working Shelf (codeforge/catalog/parts.yaml, 104 entries): the nearest are `weighted-table`,
    `zone-scheduler` and `minimap`, and none is any of these patterns; `minimap` renders an ASCII map
    from a room graph, which is a projection, not a tile format.

    Verdict: NO PART EXISTS for any of the thirteen. This order files them for the first time.

parts_to_consume: >
    None. This order writes cards, not code, and consumes nothing.

watch_for: >
    THE FAILURE MODE IS THIRTEEN CARDS THAT NAME A PATTERN WITHOUT WRITING IT. A card whose
    `capability` restates its own title has not been written. The test a reader applies is doctrine
    7b's: could a future consumer implement from this card alone? If not, the card is a listing.

    Second: this order changes cards, so `registry.json` goes stale and `registry-mirror` will FAIL.
    It is in the allowlist. The mirror has no generator; hand-edit it and say so in the RETURN, as
    CX-012 did. That finding is filed and still open.

    Third: `[STUDIED]` must read unmistakably in search output. If it does not, that is a finding
    worth reporting, not a cosmetic detail, because someone consuming a description while expecting
    a module is the failure the maturity exists to prevent.

file_allowlist:
  - catalog/                                   # NEW cards only; no existing card modified
  - registry.json                              # the mirror, regenerated with them
  - tests/test_gate_covers_the_catalogue.py    # AMENDED: teach it STUDIED, and guard the exemption
  - handoff/CX-020/RETURN.md                   # NEW, explicitly authorised
```
