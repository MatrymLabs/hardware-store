# DISPATCH CX-004

```yaml
packet_id:            CX-004
status:               LANDED
title:                PART ORDER, a durable exactly-once record (applied-once ledger)
stream:               hardware-store
owner:                Codex
reviewer:             Claude Code (re-runs every command independently)
merges:               founder
certifies:            R&D Verdict Gate. NOT this packet, NOT Codex, NOT Claude Code.
size:                 medium
flight:               M3 The Loop Turns
leg:                  3A

goal: >
  Extract the durable exactly-once record that two products have now built independently, as a
  Part with a contract, so a third consumer adopts it instead of writing it a fourth time. The
  Part records that an operation identified by a key has already been applied, and the record's
  EXISTENCE is the guard. It is a record, never a wallet and never a lock.

named_consumers:
  - codeforge     kernel/world/reward_ledger.py   RewardGrantRow, keyed (character, source, occurrence)
  - saas-starter  app/models.py:90                WebhookEvent, keyed by the Stripe event id

prior_research: >
  rd/RESEARCH_REGISTER.md, verified current 2026-08-12. The capability is NOT in the register as an
  unconsumed finding; it arrived by the pull rule instead, from two independent implementations.
  The Working Shelf already holds `Idempotency Key Store` (kernel/shelf/idempotency.py), whose own
  card records "Traded away (v1): durability and cross-process atomicity, keeping a pure
  single-process core" and whose `experimental` field already names the missing step: "back it with
  a durable UNIQUE-indexed table + row lock or upsert for atomic check-run-store across processes".
  That shelf part is the PREDECESSOR. Read its card before writing a line.

preconditions: >
  codeforge #911 merged (reward_ledger on main). saas-starter WebhookEvent unchanged and untouched.
  Demand map: ship reports/2026-08-12-demand-map.md.

verification_command: |
  cd /home/josh/Projects/MatrymLabs/hardware-store
  export PATH="$PWD/.venv/bin:$PATH"
  make check

definition_of_done: >
  catalog/applied-once/ carries CARD.md, contract/, tests/test_contract.py and impl/python/;
  the contract tests pass as given and unmodified; `make check` green; `store_check` green;
  registry.json carries the entry with maturity CANDIDATE and BOTH named consumers listed.
  The Part is FILED, not certified. Do not set maturity above CANDIDATE.

out_of_scope: >
  Refactoring either consumer to adopt the Part. A Part earns adoption; it is not forced into
  its consumers by the packet that creates it. codeforge/kernel/shelf/idempotency.py is NOT
  touched: superseding or merging it is a separate ruling, recorded as an extraction signal.
  Certification. The Verdict Gate is the only path into the Certified Tier.

approval_gates: >
  Founder merges. No self-certification. The Verdict Gate certifies. Claude Code re-runs every
  command independently before the verdict. If the contract cannot serve BOTH named consumers
  without contortion, STOP and return that finding: a Part that fits one consumer is not a Part.

rollback: >
  git revert the merge commit. The catalogue directory is new and no consumer imports it yet,
  which is exactly why adoption is out of scope.

file_allowlist:
  - catalog/applied-once/CARD.md                    # NEW
  - catalog/applied-once/contract/applied_once.py   # NEW. the contract surface
  - catalog/applied-once/impl/python/applied_once_impl.py  # NEW. the reference implementation
  - catalog/applied-once/tests/test_contract.py     # NEW. contract tests, verbatim below
  - catalog/applied-once/conftest.py                # NEW. mirror typed-settings' layout
  - catalog/applied-once/setup.cfg                  # NEW. same
  - registry.json                                   # the CANDIDATE entry, both consumers
  - handoff/CX-004/RETURN.md                        # NEW. explicitly authorised

contract_tests:       catalog/applied-once/tests/test_contract.py
contract_test_policy: |
  ASSERTION-LOCKED. Given verbatim below. Create it exactly as written. You may ADD tests; you may
  NOT weaken, delete or rewrite an assertion. If an assertion is wrong, STOP and say so in the
  RETURN with your reasoning. Do not edit it into agreement with your implementation.

return_artifact:      handoff/CX-004/RETURN.md
return_authorisation: |
  EXPLICITLY AUTHORISED. Create it. Required, not optional. Its extraction block may not be blank
  ("none observed" is a valid answer; silence is not).
```

## Why this Part exists, in one paragraph

Two products built the same mechanism without knowing about each other. `saas-starter` keys a row
by the Stripe event id and says *"Its existence IS the idempotency guard: a duplicate at-least-once
delivery finds the id already present and is a no-op."* `codeforge` keys a row by
`(character, source, occurrence)` and says *"the claim IS the insert"*. Same doctrine, same shape,
different products: a billing webhook and a game reward payout. That is the pull rule's second
occurrence, and it is the whole reason this order exists rather than a speculative one.

## The data contract, decided here

An **applied-once record** answers one question: *has the operation identified by this key already
been applied?* The key is opaque to the Part. `saas-starter` will pass `"evt_1234"`;
`codeforge` will pass `"hero|npc:training_dummy|4"`. **The Part must not know or care.**

Two operations, and the difference between them is the point:

- `seen(key)` - a plain read. Was this applied? Cheap, and safe to be wrong under a race.
- `claim(key)` - the guard. Returns True if THIS caller won the right to apply it, False if
  somebody already did. **This must be atomic**, because check-then-act does not hold across
  processes: two can both read "not applied" and both apply.

`claim` is the one that matters. A Part that only offers `seen` is a Part that pushes the hard
problem back onto every consumer.

## Invariant

**A key is claimed at most once, ever, and that fact outlives the process.**

Not "the code path ran once". A retry, a reconnect, a redelivery, a second process, or a restart
must not be able to claim the same key twice, and the record must be durable.

## The trap, stated so you do not fall in it

The naive storage choice is a dict, and the shelf's existing part already made it deliberately.
**Durability across a process boundary is the entire reason this Part exists.** If your
implementation passes its tests with an in-memory store, the tests are wrong and you must say so
rather than ship it.

## The contract tests, verbatim

Create `catalog/applied-once/tests/test_contract.py` with exactly this content.

```python
"""Contract tests for applied-once: a key is claimed at most once, and the record is durable.

Acceptance: an unseen key is claimable; claiming records it; a DIFFERENT key is unaffected; the
key is opaque, so a Stripe event id and a composite game grant identity behave identically.

Refusal (fail loud): the same key never claims twice; an empty key is refused; the record survives
a fresh store object opened on the same backing location.

Why this file exists: two products built this independently (saas-starter WebhookEvent, codeforge
RewardGrantRow) and the shelf's in-memory Idempotency Key Store explicitly traded away the
durability both of them needed.
"""

from __future__ import annotations

import pytest

from applied_once import AppliedOnce, KeyRefused


def test_an_unseen_key_is_not_yet_applied(store: AppliedOnce) -> None:
    assert not store.seen("evt_1234")


def test_claiming_an_unseen_key_succeeds(store: AppliedOnce) -> None:
    assert store.claim("evt_1234") is True


def test_a_claimed_key_is_seen(store: AppliedOnce) -> None:
    store.claim("evt_1234")
    assert store.seen("evt_1234")


def test_the_same_key_never_claims_twice(store: AppliedOnce) -> None:
    """The guard. A duplicate at-least-once delivery must lose."""
    assert store.claim("evt_1234") is True
    assert store.claim("evt_1234") is False
    assert store.claim("evt_1234") is False


def test_a_different_key_is_unaffected(store: AppliedOnce) -> None:
    store.claim("evt_1234")
    assert not store.seen("evt_5678")
    assert store.claim("evt_5678") is True


def test_the_key_is_opaque_to_the_part(store: AppliedOnce) -> None:
    """saas-starter passes a provider event id; codeforge passes a composite grant identity.

    The Part must not know or care. If either shape needs special handling, the contract is wrong.
    """
    assert store.claim("evt_1234") is True
    assert store.claim("hero|npc:training_dummy|4") is True
    assert store.claim("hero|npc:training_dummy|5") is True
    assert store.claim("hero|npc:training_dummy|4") is False


def test_an_empty_key_is_refused_loudly(store: AppliedOnce) -> None:
    """A record nobody can look up again is the same as no record, except it looks like one."""
    for bad in ("", "   "):
        with pytest.raises(KeyRefused):
            store.claim(bad)
        with pytest.raises(KeyRefused):
            store.seen(bad)


def test_the_record_outlives_the_store_object(store_factory) -> None:
    """The whole point, and what the shelf's in-memory predecessor cannot do.

    A SECOND store opened on the same backing location must already know the key. An
    implementation that keeps state in the instance cannot pass this, which is the intended
    pressure.
    """
    first = store_factory()
    assert first.claim("evt_durable") is True

    second = store_factory()
    assert second.seen("evt_durable")
    assert second.claim("evt_durable") is False
```

`conftest.py` provides `store` and `store_factory`. `store_factory()` must return a NEW store
object bound to the SAME backing location every call, so the durability test is real rather than a
reference to the same instance.

## Definition of done

```bash
cd /home/josh/Projects/MatrymLabs/hardware-store
export PATH="$PWD/.venv/bin:$PATH"
make check
```

- The contract tests pass as given, unmodified.
- `store_check` green; `registry.json` carries `applied-once` at maturity **CANDIDATE** with both
  named consumers.
- The CARD records the predecessor honestly: this Part exists because the shelf's
  `Idempotency Key Store` traded durability away, and it says so in its own card.
- `make check` green.

## EXTRACTION CONTEXT

```yaml
store_search_result: |
  SEARCHED, both tiers, this session, per ADR-0005. Logged in
  ship reports/2026-08-12-demand-map.md.
    Certified Tier (6 parts): budget-gate, circuit-breaker, lexicon-gate, retry, source-monitor,
      typed-settings. No exactly-once record. Nearest neighbours are retry and circuit-breaker,
      which handle FAILURE, not DUPLICATION. Different problem.
    Working Shelf (104 parts): `Idempotency Key Store` is a direct hit on shape and an explicit
      miss on guarantee, by its own card. It is the predecessor, not the Part.

parts_to_consume: |
  NONE consumable as-is. The shelf predecessor is single-process by deliberate design. Read its
  card and its `experimental` field: this Part is that field, implemented. Do NOT copy its code
  without saying so; do NOT modify it in this packet.

watch_for: |
  A third consumer is probably already here. `recall/recall/jobs.py` describes an operation as
  idempotent but has no durable guard, so it is a CANDIDATE consumer, not a current one. Note it
  in the RETURN; do not adopt it, and do not count it as a consumer on the card. Two named
  consumers is what the pull rule needed and two is what the card claims.
```
