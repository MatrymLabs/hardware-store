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

import threading

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


def test_only_one_of_many_concurrent_claimants_wins(store: AppliedOnce) -> None:
    """The central atomicity guarantee must fail on check-then-act."""
    wins: list[bool] = []
    lock = threading.Lock()
    start = threading.Barrier(8)

    def race() -> None:
        start.wait()
        won = store.claim("evt_contested")
        with lock:
            wins.append(won)

    threads = [threading.Thread(target=race) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert wins.count(True) == 1, f"{wins.count(True)} callers claimed one operation: {wins}"
    assert wins.count(False) == 7
