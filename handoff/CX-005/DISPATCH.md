# DISPATCH CX-005

```yaml
packet_id:            CX-005
status:               LANDED
title:                A contract must test the property its CARD claims
stream:               hardware-store
owner:                Codex
reviewer:             Claude Code (re-runs every command independently)
merges:               founder
size:                 medium
flight:               M3 The Loop Turns
leg:                  3B
queue_position:       1 of 3. Blocked? Report verbatim and START CX-006. Do not wait.

goal: >
  Make PRT-0007's contract suite able to falsify the property the Part exists for, then audit the
  other six suites for the same gap. A contract that cannot fail on the loss of its own central
  guarantee certifies nothing, and consumers adopt on the strength of these suites.

preconditions: >
  hardware-store #29 merged (applied-once at CANDIDATE). #30 and #31 may or may not be merged;
  neither blocks this. codeforge #917 carries a working concurrency test you may read.

verification_command: |
  cd /home/josh/Projects/MatrymLabs/hardware-store
  export PATH="$PWD/.venv/bin:$PATH"
  make check

definition_of_done: >
  catalog/applied-once/tests/test_contract.py gains a concurrency case that REDDENS when claim() is
  check-then-act and passes on the shipped implementation, demonstrated both ways in the RETURN;
  an audit table in the RETURN naming, for each of the other six Parts, the central property its
  CARD claims and whether its suite can falsify it; make check green.

out_of_scope: >
  Repairing the other six suites. Audit and REPORT them; each repair is its own packet, and a
  seven-Part test rewrite inside one dispatch is how a medium becomes unreviewable.
  registry.json, CARD maturity, consumer lists. Not this packet.

approval_gates: >
  Founder merges. No self-certification. If auditing reveals a Part whose CARD claims a property
  its implementation does NOT have, STOP and report it as a finding rather than fixing it quietly.

rollback: >
  git revert the merge commit. Only test files change.

file_allowlist:
  - catalog/applied-once/tests/test_contract.py    # the concurrency case
  - handoff/CX-005/RETURN.md                       # NEW, explicitly authorised

contract_tests:       catalog/applied-once/tests/test_contract.py
contract_test_policy: |
  ADDITIVE ONLY. Every existing assertion in that file stays exactly as it is. You are ADDING a
  case, not revising the suite. If an existing assertion looks wrong, say so in the RETURN.

return_artifact:      handoff/CX-005/RETURN.md
return_authorisation: |
  EXPLICITLY AUTHORISED. Required. Extraction block may not be blank.

store_search_result: |
  NOT REQUIRED for this packet: it adds a test to an existing Part rather than implementing a
  capability. Say so explicitly in the RETURN rather than leaving the field empty.

parts_to_consume: |
  None. This is test coverage for a Part that already exists.

watch_for: |
  "The suite tests what is easy, not what is claimed" is a shape worth screening across the fleet,
  not just here. If the audit finds it in more than one Part, that is a pattern, not six bugs.
```

## The evidence, so you do not have to rediscover it

`applied-once` exists because its predecessor traded away durability and cross-process atomicity.
Its suite proves durability. It cannot prove atomicity.

`CMD` Sabotaging `claim()` into check-then-act, the exact race the Part exists to prevent:

```
all 8 contract tests: PASSED
```

They are single-threaded. `test_the_same_key_never_claims_twice` calls `claim` three times in
sequence, which a check-then-act implementation satisfies perfectly. **The one property that
distinguishes this Part from what it supersedes is the one its contract cannot falsify.**

An implementation like this ships today and passes everything:

```python
def claim(self, key):
    if self.seen(key):
        return False
    self._record(key)
    return True
```

## Invariant

**A contract test suite must redden when the Part loses the property its CARD claims.**

## The trap, learned building this in codeforge

Warm the store BEFORE racing. N cold claimants each initialise the backing store and collide on
setup, and the test then fails for a reason that has nothing to do with the claim. That produced a
false finding for me before I read the exception text. Warm it, then race.

Working reference, which does redden on the sabotage:
`codeforge/tests/test_reward_ledger_conforms.py::test_only_one_of_many_concurrent_claimants_wins`

## Definition of done

```bash
cd /home/josh/Projects/MatrymLabs/hardware-store
export PATH="$PWD/.venv/bin:$PATH"
make check
```

Demonstrate BOTH directions in the RETURN: the new case passing on the shipped implementation, and
reddening when `claim` is sabotaged to check-then-act. A test shown only green proves nothing.
