packet_id: CX-019
status: COMPLETE
tests_passing: yes

## Verification

Remote was fetched before reading the dispatch. `git rev-list --count HEAD..origin/main` returned
`0`.

Both reuse tiers were searched as required. Certified Tier (`catalog/`, seven carded Parts) had no
catalogue-schema Part. Working Shelf (`../codeforge-codex/catalog/parts.yaml`) was searched for
catalog, registry, and schema; broad matching was non-discriminating, and the narrowed catalogue
management candidates had no matching mechanism. Verdict: no existing Part; none consumed.

Required gate output, run this session:

```text
export PATH="/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin:$PATH"
make check PY=/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python

/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m ruff check .
All checks passed!
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m mypy hardware_store
Success: no issues found in 7 source files
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m pytest -q
171 passed in 4.10s
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m hardware_store.store_check
Hardware Store integrity check :: /home/josh/Projects/MatrymLabs/hardware-store-codex
  no findings - the Store is clean
VERDICT: PASS (0 failing, 0 warning)
```

Store search output distinguishes the new maturity in the real formatter:

```text
[STUDIED  ] applied-once :: Durably record an opaque operation key exactly once.
```

## Calibration

Removing `taint_class` from a valid STUDIED fixture produced:

```text
FAIL [card-schema] example-reverser: STUDIED card missing required provenance field 'taint_class'
WARN [impl-exists] example-reverser: STUDIED card: implementation check skipped (pattern has no code)
WARN [tests-exist] example-reverser: STUDIED card: contract test check skipped (pattern has no code)
VERDICT: FAIL (1 failing, 2 warning)
STUDIED_RED_EXIT:1
```

Restoring it produced:

```text
WARN [impl-exists] example-reverser: STUDIED card: implementation check skipped (pattern has no code)
WARN [tests-exist] example-reverser: STUDIED card: contract test check skipped (pattern has no code)
VERDICT: PASS (0 failing, 2 warning)
STUDIED_GREEN_EXIT:0
```

Removing a CANDIDATE implementation produced the required refusal:

```text
FAIL [impl-exists] example-reverser: implementation path does not exist: impl/python/example_reverser.py
VERDICT: FAIL (1 failing, 0 warning)
CANDIDATE_RED_EXIT:1
```

Restoring it returned the fixture to:

```text
no findings - the Store is clean
VERDICT: PASS (0 failing, 0 warning)
CANDIDATE_GREEN_EXIT:0
```

The Certified guard remains covered by the existing certification sabotage and the full 171-test
suite; `check_certified_gate` was not changed.

## Scope and extraction

`MATURITIES` now includes STUDIED. Code fields remain mandatory for every other maturity; STUDIED
requires `source_studied`, `taint_class`, and `clean_room`. Implementation and contract-test checks
skip STUDIED only and announce those skips as warnings. No card or registry entry was added, so the
mirror required no edit.

`git diff --stat`:

```text
 hardware_store/store_check.py | 19 +++++++++++++++++++
 hardware_store/store_lib.py   |  6 ++++--
 tests/test_store_check.py     | 32 ++++++++++++++++++++++++++++++++
```

All changed paths are allowlisted. No unverified command remains. The local worktree lacks its own
`.venv`; the available repository environment was used explicitly in the gate command above.

Pattern screen: lane echo (persistence, commands, events, transactions, world graph, integration):
none observed. Catalogue match: no applicable Part. Recurrence check: none observed. Verdict note:
this is Store-instrument schema work, not a reusable application capability.

Extraction block: no reusable Part was introduced. The Store can now hold a studied pattern without
pretending it has code, while its CANDIDATE and CERTIFIED bars remain enforced.
