# RETURN CX-004

```yaml
packet_id: CX-004
pr_url: https://github.com/MatrymLabs/hardware-store/pull/29
status: COMPLETE
commands_run:
  - command: pytest -q catalog/applied-once/tests/test_contract.py
    exit_code: 0
    output_excerpt: "8 passed in 0.16s"
  - command: make check
    exit_code: 2
    output_excerpt: "I001 Import block is un-sorted or un-formatted at catalog/applied-once/tests/test_contract.py:14:1"
  - command: make check
    exit_code: 0
    output_excerpt: "All checks passed; Success: no issues found in 7 source files; 47 passed in 0.73s; VERDICT: PASS (0 failing, 0 warning)"
tests_passing: yes, 47 passed in 0.73s
files_touched:
  - catalog/applied-once/CARD.md
  - catalog/applied-once/contract/applied_once.py
  - catalog/applied-once/impl/python/applied_once_impl.py
  - catalog/applied-once/tests/test_contract.py
  - catalog/applied-once/conftest.py
  - catalog/applied-once/setup.cfg
  - registry.json
  - handoff/CX-004/RETURN.md
blockers: none
```

## Extraction signals

```yaml
reimplemented: >
  No certified Store part was reimplemented. The inspected shelf predecessor is an explicit
  single-process, in-memory predecessor with a broader result-and-fingerprint contract. CX-004
  supplies its documented durability and cross-process atomicity gap without modifying it.
recurrence: >
  Second real occurrence confirmed: codeforge RewardGrantRow uses character, source, and
  occurrence; saas-starter WebhookEvent uses a Stripe event id. The filed Part records their
  shared durable-record guard, not either product's domain identity.
generalizable: >
  Yes. Opaque durable atomic claim semantics work for any at-least-once delivery or retry where
  the operation identity is known. The record is deliberately not a wallet, lock, result cache,
  or transaction coordinator.
friction: >
  The existing Idempotency Key Store intentionally lacks durability and cross-process atomicity.
  Its card documents that gap, so no silent fork or workaround was required.
dissent: >
  The two listed source consumers establish the pull but do not yet import the newly filed Part.
  They are truthfully marked pending adoption, and the card remains CANDIDATE. The cited demand
  map artifact was absent from this checkout; consumer evidence was verified directly instead.
```

## Verification

```text
$ make check
All checks passed!
Success: no issues found in 7 source files
47 passed in 0.73s
Hardware Store integrity check :: /home/josh/Projects/MatrymLabs/hardware-store
  no findings - the Store is clean
VERDICT: PASS (0 failing, 0 warning)
```
