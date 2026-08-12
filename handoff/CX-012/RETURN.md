packet_id: CX-012
status: PARTIAL
tests_passing: yes

## Mutation status

The additive contract implementation and 20 contract tests pass, but the required mutation gate
cannot execute against this checkout with the pinned mutmut tool. Verbatim command and output:

```text
cd catalog/typed-settings
export PATH="/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin:$PATH"
mutmut run

done in 365ms (1 files mutated, 0 ignored, 0 unmodified)
20 passed in 0.04s
Stopping early, because we could not find any test case for any mutant. It seems that the selected
tests do not cover any code that we mutated.
```

The required 2.5.1 mutation score was therefore not produced. No mutation threshold adjustment or
tool pin change was attempted. This remains UNVERIFIED.

## Local evidence

```text
export PATH="/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin:$PATH"
pytest -q catalog/typed-settings/tests/test_contract.py
....................                                                     [100%]
20 passed in 0.09s
```

The implementation keeps `secret=True` redacted and adds the explicit `dev_default_ok=True`
declaration. Existing refusal behavior remains unchanged; new tests cover opt-in acceptance,
redaction with an injected production value, refusal without opt-out, and non-secret visibility.

Both reuse tiers were searched: Certified Tier cards for secret, redact, settings, environment;
Working Shelf `../codeforge-codex/catalog/parts.yaml` for the same terms. No separate applicable
Part was found or consumed.

`make check PY=/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python` passed this session:

```text
169 passed in 4.49s
Hardware Store integrity check :: /home/josh/Projects/MatrymLabs/hardware-store-codex
  no findings - the Store is clean
VERDICT: PASS (0 failing, 0 warning)
```

The amended `registry.json` was hand-edited to mirror CARD.md because no generator exists. This is
an extraction signal, not a generator implementation. `git diff --stat` is limited to the amended
allowlist.

Pattern screen: lane echo (persistence, commands, events, transactions, world graph, integration):
none observed. Catalogue match: none observed. Recurrence check: none observed. Verdict note:
mutation evidence is required before this Certified Tier semantic change can be accepted.

Extraction block: registry mirror has no generator; hand-editing was required and should become a
separate generator order. Unverified: the required mutmut 2.5.1 score; rerun from a checkout
where its configured test-selection path is visible to mutmut.
