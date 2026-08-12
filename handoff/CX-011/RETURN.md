packet_id: CX-011
status: COMPLETE
tests_passing: yes

## Verification

Consume-first searches were performed in both tiers. Certified Tier search (`catalog/*/CARD.md`)
for citation, provenance, identifier, and reference found `provenance` sections but no reusable
citation-resolution Part. Working Shelf search (`../codeforge-codex/catalog/parts.yaml`) found
provenance metadata entries, but no applicable implementation. `source-monitor` (PRT-0003) was
judged and not consumed because it fingerprints external sources rather than resolving internal
Part identities.

The registered worktree had no local `.venv`; its pre-existing status was clean before edits. The
gate therefore used the sibling environment explicitly:

```text
export PATH="/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin:$PATH"
make check PY=/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python

/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m ruff check .
All checks passed!
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m mypy hardware_store
Success: no issues found in 7 source files
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m pytest -q
165 passed in 4.51s
/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python -m hardware_store.store_check
Hardware Store integrity check :: /home/josh/Projects/MatrymLabs/hardware-store-codex
  no findings - the Store is clean
VERDICT: PASS (0 failing, 0 warning)
```

`git rev-list --count HEAD..origin/main` was 0 before implementation.

## Calibration

Removing provenance identity handling made the new RD-only test red:

```text
FAILED test_consumer_citing_only_rd_provenance_id_is_accepted
AssertionError: assert False is True
RED_EXIT:1
```

Restoring it made both the RD-only acceptance and neither-identity refusal green:

```text
..  [100%]
2 passed, 21 deselected in 0.05s
GREEN_EXIT:0
```

The temporary sabotage was restored; no calibration file remains.

## Scope

`_path_imports_part` now accepts the card's PRT id or its declared provenance `rd_id`. Consumers
citing neither identity remain failures. No Card schema, catalog card, registry, or other check was
changed.

`git diff --stat`:

```text
 hardware_store/store_check.py | 11 +++++++++--
 tests/test_store_check.py     | 25 +++++++++++++++++++++++++
 handoff/CX-011/RETURN.md      | 67 +++++++++++++++++++++++++++++++++++++++++++
```

All touched paths are allowlisted.

Pattern screen: lane echo (persistence, commands, events, transactions, world graph, integration):
none observed. Catalogue match: no applicable Certified or Working Shelf Part. Recurrence check:
none observed. Verdict note: this is a local Store gate correction, not an extraction candidate.

Extraction block: none observed; no reusable component was introduced.

Unverified: the exact default `make check` invocation cannot resolve `.venv/bin/python` in this
registered worktree because that environment is absent; the same gate passed with the explicit
available environment shown above.
