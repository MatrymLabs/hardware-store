# DISPATCH CX-019

**Status:** LANDED, hardware-store #44, 2026-08-12. Amended after a correct Codex block, then re-verified independently by the Coordinator before merge.

```yaml
packet_id:            CX-019
title:                The Store cannot hold a pattern, and doctrine now says it must
stream:               rd
owner:                Codex
reviewer:             Claude Code, who re-runs every command independently
merges:               founder
size:                 medium
taint_class:          SAFE. No studied external material. The Store's own schema, on the Store's own gate.

goal: >
    Let a card describe a PATTERN that has been studied but not yet implemented, at a new maturity
    `STUDIED`, and make the gate demand of such a card the things a pattern must carry instead of the
    things only code can have.

    THE INVARIANT, in prose and separate from the commands that test it: a card states what it is,
    and the gate holds it to the standard its own maturity claims. A STUDIED card is not exempt from
    inspection; it is inspected against a different and equally specific set of requirements. Nothing
    reaches CERTIFIED without code, tests, a real consumer and R&D.

why_now: >
    Founder ruling 2026-08-12, two of them. First: a useful pattern is a Part, just untested.
    Second, after the collision below was measured: let the Store hold a studied pattern rather than
    build twenty speculative implementations to satisfy a schema.

    Doctrine section 7b, merged as ship #259, now reads "A useful pattern found by study is carded at
    CANDIDATE, immediately. The card IS the deliverable of a study." Measured against the Store the
    same hour, a pattern card with no code produces:

      FAIL card-schema   missing required field 'contract'
      FAIL card-schema   missing required field 'implementations'
      FAIL impl-exists   card lists no implementations (a card with no code)
      FAIL tests-exist   no contract tests - an implementation without tests is a defect

    Doctrine was written before the instrument was checked. That is the Coordinator's defect and it
    is recorded here rather than smoothed over. `CATEGORIES` already contains "Pattern", so the slot
    was reserved and the required fields never made room for it.

    Twenty-three studied findings (RD-2026-0110 through 0140: metatile hierarchy, tilemap
    bit-packing, SRAM checksum-fail-to-empty, DTE text compression, VBlank frame budgets, bank and
    memory-map discipline, and the toolchain entries) are waiting on this. They are unfindable while
    they sit in a register nobody greps, and a pattern nobody can find is a pattern that gets
    rebuilt.

out_of_scope: >
    THE CERTIFICATION BAR. `check_certified_gate` is not to be touched: CERTIFIED and FLEET_CORE
    still require an `rd_certification` record, a real consumer, and a mutation score at threshold.
    A STUDIED card must NOT become a way to reach CERTIFIED without code.

    Also out of scope: writing any of the twenty-three cards. This order changes the schema and the
    gate. The cards are a separate order and depend on this one landing.

    Do not add a maturity beyond `STUDIED`. `FLEET_CORE` already exists unused; do not populate or
    remove it here.

preconditions: >
    CHECK: file hardware_store/store_lib.py contains MATURITIES
    CHECK: file hardware_store/store_check.py contains check_certified_gate
    CHECK: file hardware_store/store_lib.py lacks STUDIED

the_design: >
    Settled by the Coordinator so it is not decided by implementation. Names are yours where they do
    not appear below.

    1. `MATURITIES` gains `"STUDIED"`. `CERTIFIED_MATURITIES` is unchanged.

    2. `REQUIRED_FIELDS` splits. Every card, at any maturity, still carries: `part_id`,
       `canonical_name`, `capability`, `category`, `maturity`, `failure_modes`, `provenance`.
       `contract`, `tests` and `implementations` become required only for maturities that claim
       code, which is every maturity except `STUDIED`.

    3. A STUDIED card carries three things instead, and the gate FAILS without them:
         - `[provenance] source_studied` - what was read. A card that cannot name its source cannot
           be certified later, and doctrine 7b says so.
         - `[provenance] taint_class` - SAFE, CAUTION or NEVER, inherited from the research. Codex
           never receives CAUTION or NEVER material, so a card that omits it cannot be routed.
         - `[provenance] clean_room` - the record path, or an explicit statement that no clean-room
           separation was required because nothing proprietary was read. Doctrine: "Do not describe
           work as clean-room unless the separation actually happened."

    4. `check_impls` and `check_tests` skip STUDIED cards and ANNOUNCE the skip in the report. A
       silent exemption reads as coverage; doctrine section 5 requires the announcement.

    5. `store_search` already prints `[{card.maturity:9}]`, which fits STUDIED. Confirm it reads
       unmistakably different from CANDIDATE in real output and paste a sample. Someone consuming a
       description while expecting a module is the failure this order opens, and the maturity prefix
       is the only thing standing in front of it.

contract_tests: >
    Additive to tests/test_store_check.py. The four that matter, and none may be satisfied by
    weakening another check:

      a STUDIED card with source_studied + taint_class + clean_room PASSES with no code
      a STUDIED card missing ANY of those three FAILS, naming which
      a CANDIDATE card with no implementation still FAILS, exactly as it does today
      a CERTIFIED card still needs rd_certification + a real consumer + the mutation score

    The third and fourth are the guard. This order must not become "the gate stopped asking".

verification_command: |
    cd hardware-store
    make check
    .venv/bin/python -m hardware_store.store_search ""

definition_of_done: >
    STUDIED accepted; the three provenance fields enforced on it; code fields no longer required of
    it; skips announced in the report; existing CANDIDATE and CERTIFIED behaviour unchanged and
    proven unchanged; `make check` green over the whole instrument; store_search output pasted; both
    calibrations below pasted.

calibration_required: >
    Two transitions, each red then green, pasted verbatim:
      remove `taint_class` from a STUDIED card -> store_check FAILS naming it -> restore -> PASS
      remove the implementation from a CANDIDATE card -> store_check still FAILS -> restore -> PASS
    The second proves the change did not loosen the existing gate, which is the way this order fails
    if it fails.

rollback: >
    Revert the commit. No card in the catalogue uses STUDIED yet, so nothing depends on it.

approval_gates: >
    None beyond the founder's merge. Both rulings are already given. No new dependency, no public
    interface outside the Store's own card schema, and the certification path is untouched.

store_search_result: >
    Both tiers searched 2026-08-12; one tier logged is an incomplete search.
    Certified Tier (hardware-store/catalog/, 9 directories, 7 carded): zero Parts manage a catalogue
    schema. Seven cards mention maturity because they declare their own; none provides the mechanism.
    Working Shelf (codeforge/catalog/parts.yaml, 104 entries): narrowed to entries whose PURPOSE is
    catalogue or card management, seven matched on the word and none on the meaning - `typed-settings`
    is an environment catalogue, `loader-cache` caches parsed files, `probabilistic` is sketches.
    A first pass matching any occurrence of catalog/registry/schema returned 104 of 104, which is not
    evidence; recorded because a search that matches everything has measured nothing.

    Verdict: NO PART EXISTS. This is a change to the Store's own instrument, not a reusable
    capability. First occurrence, logged only.

parts_to_consume: >
    None. See store_search_result.

watch_for: >
    The failure mode of this order is that it makes the gate stop asking. Every relaxation must be
    scoped to STUDIED and proven not to reach CANDIDATE or CERTIFIED; that is what the third and
    fourth contract tests are for, and they are not optional.

    Second: `registry.json` is a MIRROR of the cards and `registry-mirror` enforces it. It is in the
    allowlist pre-emptively. CX-012 was blocked by exactly this, because the order excluded the
    mirror while requiring a card change. The mirror has no generator; hand-edit it and say so.

file_allowlist:
  - hardware_store/store_lib.py                # MATURITIES, the required-field split
  - hardware_store/store_check.py              # the STUDIED branch and the announced skips
  - tests/test_store_check.py                  # ADDITIVE
  - registry.json                              # the mirror, if a card changes; see watch_for
  - handoff/CX-019/RETURN.md                   # NEW, explicitly authorised
```
