# DISPATCH CX-011

```yaml
packet_id:            CX-011
title:                The Store cannot see half the citations it asks for
stream:               rd
owner:                Codex
reviewer:             Claude Code, who re-runs every command independently
merges:               founder
size:                 small
taint_class:          SAFE. No studied external material. The Store's own gate, on the Store's own cards.

goal: >
  Teach `consumer-resolves` to recognise a Part's RD provenance id as a citation, not only its
  PRT id. Six of nine cards carry both; a consumer that cites the Part by the RD id it was
  extracted from is invisible to the check today, and the Store reports PASS over it.

boundary: >
  Computed from the allowlisted file's imports. `hardware_store/shelf.py` (the Card model and the
  Report) is deliberately NOT in the allowlist: this order changes how a citation is RECOGNISED,
  not what a Card is. If the fix appears to need a new Card field, that is a schema change and a
  block, not a widening.
  `catalog/*/CARD.md` are also excluded. The cards are correct as written; the gate cannot read
  them. Editing a card to satisfy a gate is fixing the output instead of the generator.

preconditions: >
  CHECK: file hardware_store/store_check.py contains def _path_imports_part
  CHECK: file hardware_store/store_check.py contains card.part_id
  CHECK: file hardware_store/store_check.py lacks RD-2026
  CHECK: file catalog/retry/CARD.md contains RD-2026-0009
  CHECK: file catalog/typed-settings/CARD.md contains RD-2026-0014
  CHECK: file tests/test_store_check.py exists

verification_command: |
  cd <your registered hardware-store worktree>
  export PATH="$PWD/.venv/bin:$PATH"
  git fetch origin && git rev-list --count HEAD..origin/main   # must print 0
  make check

definition_of_done: >
  `_path_imports_part` accepts the Part's PRT id OR any RD provenance id its card declares.
  A consumer citing only the RD id resolves. A consumer citing NEITHER still fails, and a test
  proves that second half, because a citation check that accepts everything is not a check.
  make check green, and store_check's own verdict pasted into the RETURN.

out_of_scope: >
  The Card schema. The cards themselves. The second-consumer pull rule's THRESHOLD; this order
  changes what counts as evidence of consumption, never how many consumers a Part needs.
  Any other check in store_check.

approval_gates: >
  Founder merges. No self-certification. This gate guards the Certified Tier, so a change that
  makes it easier to pass needs its refusal case proven, not asserted.

rollback: >
  git revert. One function and its tests.

file_allowlist:
  - hardware_store/store_check.py          # _path_imports_part only
  - tests/test_store_check.py              # its existing twin, additive
  - handoff/CX-011/RETURN.md               # NEW, explicitly authorised

contract_tests:       tests/test_store_check.py
contract_test_policy: |
  ADDITIVE. Do not weaken an existing assertion. Both directions required:
  a consumer citing ONLY the RD id resolves; a consumer citing neither id still FAILS.

return_artifact:      handoff/CX-011/RETURN.md
return_authorisation: |
  EXPLICITLY AUTHORISED. Required. Record what the gate COLLECTED as well as what passed.

store_search_result: |
  SEARCH BOTH TIERS and log both. Search "citation", "provenance", "identifier", "reference".
  Judge `source-monitor` (PRT-0003) on its card: it fingerprints external sources, which is a
  different question from resolving an internal identifier.

parts_to_consume: |
  UNKNOWN until you search. Likely none; this is one regex and one lookup.

watch_for: |
  This gate currently reports PASS. Any change that keeps it PASS proves nothing on its own, which
  is why the refusal case is contract-locked. If you find yourself making the check more permissive
  without a test that still fails, stop.
```

## The measurement, taken 2026-08-12

`CMD` Every card carrying both identities:

```
budget-gate       PRT-0001   also cites RD-2026-0004
circuit-breaker   PRT-0005   also cites RD-2026-0011
lexicon-gate      PRT-0002   also cites RD-2026-0004
retry             PRT-0004   also cites RD-2026-0009
source-monitor    PRT-0003   also cites RD-2026-0004
typed-settings    PRT-0006   also cites RD-2026-0014
```

**Six of nine.** `_path_imports_part` compiles one pattern, from `card.part_id`, so a consumer that
cites the Part by the RD id it was extracted from is not seen. `store_check` says
`VERDICT: PASS (0 failing, 0 warning)` over that.

The other half of ship's issue #22, a missing citation being only a WARN, is already fixed:
`store_check.py:199` reads *"FAIL, not warn. A consumer that does not cite the Part is a reuse
claim with no..."*. Verified before this order was written rather than assumed from the issue text.

## Invariant

**The second-consumer pull rule is only as strong as the citation check underneath it, and a check
that recognises one of two legitimate identities is measuring half the Store.**
