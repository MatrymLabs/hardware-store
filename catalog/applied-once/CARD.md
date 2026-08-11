+++
part_id = "PRT-0007"
canonical_name = "applied-once"
capability = "Durably record an opaque operation key exactly once. An atomic claim returns true only to the caller that creates the record, and false to every later caller using the same key."
category = "Data"
maturity = "CANDIDATE"
contract = "contract/applied_once.py"
inputs = "an opaque non-empty string key naming one operation; a durable SQLite backing location for the Python reference implementation"
outputs = "seen(key), an advisory existence read; claim(key), an atomic true-for-winner and false-for-already-claimed guard; or KeyRefused for an empty key"
permissions = "the reference adapter creates and writes only its SQLite database path"
security = "an operation key is opaque to the Part and stored only as a unique durable record. Consumers remain responsible for choosing keys that do not expose sensitive values."
accessibility = "n/a (library primitive)"
performance = "UNMEASURED. Each operation opens a short SQLite connection and uses a primary-key lookup or insert. No latency claim is made before a benchmark exists."
failure_modes = [
  "KeyRefused for an empty or whitespace-only key, because it could not be reliably looked up again",
  "SQLite errors propagate rather than pretending a durable claim succeeded",
  "seen is an advisory read and may be stale under a race; consumers must use claim as the guard",
]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 0
mutation_tool = "unmeasured while CANDIDATE"

[provenance]
rd_record = ""
origin = "Extracted from two independent fleet implementations: codeforge RewardGrantRow, keyed by character, source, and occurrence; and saas-starter WebhookEvent, keyed by Stripe event id. The predecessor is codeforge kernel/shelf/idempotency.py, whose in-memory design explicitly trades away durability and cross-process atomicity."
clean_room = true
licence_risk = "none. This Part was derived from fleet-owned implementations and standard SQLite semantics."

[[implementations]]
language = "python"
path = "impl/python/applied_once_impl.py"
version = "0.1.0"
benchmark = "unmeasured"

# NOT consumers. Verified against git on 2026-08-12: neither path cites PRT-0007, because the
# Part was extracted FROM them. `consumers` means code that adopted the Part and says so;
# `extracted_from` means code the Part came out of. Opposite directions, and holding both in one
# field is what let this catalogue claim seven consumers while having three.
[[extracted_from]]
repo = "codeforge"
path = "codeforge/kernel/world/reward_ledger.py"
version = "source implementation, pending adoption"
adopted = "2026-08-11"

[[extracted_from]]
repo = "saas-starter"
path = "saas-starter/app/models.py"
version = "source implementation, pending adoption"
adopted = "2026-08-11"
+++

# applied-once

## Why this Part exists

This Part is a pull, not a speculative library. `codeforge` independently records reward grants
by `(character, source, occurrence)`, while `saas-starter` records Stripe webhook event IDs. In
each case, the record's existence is the idempotency guard. One protects a game reward; the other
protects a billing-side webhook. The key shapes differ, so the Part treats them as opaque.

The predecessor, `codeforge/kernel/shelf/idempotency.py`, is deliberately single-process and
in-memory. It stores results and fingerprints, which this narrower record does not attempt to do.
Its own card says a durable unique-indexed table plus row lock or upsert is the missing step. This
reference adapter supplies that durable atomic claim using SQLite's primary key and `INSERT OR
IGNORE`.

## Contract boundary

`seen` is a cheap existence read. It is not safe as a guard under a race. `claim` is the guard: a
unique durable insert succeeds for one caller and becomes a no-op for every duplicate. The Part is
not a wallet, a result cache, a distributed lock, or a transaction coordinator. Consumers couple
their operation's side effect to a successful claim in their own transaction boundary.

## Status

**CANDIDATE.** The two source consumers establish the pull, but neither imports this newly filed
Part yet. Adoption is deliberately outside CX-004. R&D alone may certify it after its verdict.

`recall/recall/jobs.py` describes an operation as idempotent without a durable guard. It is a
possible third consumer, not a current consumer and not evidence for certification.
