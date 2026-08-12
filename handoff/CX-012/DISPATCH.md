# DISPATCH CX-012

```yaml
packet_id:            CX-012
title:                secret=True must mean redacted, and stop forcing consumers to choose
stream:               rd
owner:                Codex
reviewer:             Claude Code, who re-runs every command independently
merges:               founder
size:                 medium
taint_class:          SAFE. No studied external material. Sources are specifications only (12factor III, OWASP ASVS 2.10.4), already cited on the card.

goal: >
  Separate the two jobs `secret=True` does today, WITHOUT losing the rule that has already caught
  two hardcoded secrets in this Workshop. `secret=True` must always redact. The no-default rule
  stays ON by default. A consumer that genuinely needs a development default declares it
  explicitly, so the dangerous choice becomes loud in the declaration instead of being expressed
  by silently dropping redaction.

boundary: >
  This is a CERTIFIED contract. `catalog/typed-settings/CARD.md` is in the allowlist because the
  contract's stated semantics change and a card that describes the old behaviour is a false claim.
  Every OTHER card, the registry, and `hardware_store/` are excluded: this order changes one Part,
  not the Store.
  Consumers are excluded and are NOT to be migrated here. Existing declarations must keep working
  unchanged, which is the compatibility requirement below, and a consumer that wants the new
  escape hatch adopts it in its own repository on its own schedule.

preconditions: >
  CHECK: file catalog/typed-settings/impl/python/typed_settings_impl.py contains def field
  CHECK: file catalog/typed-settings/contract/typed_settings.py contains MAY NOT carry a default
  CHECK: file catalog/typed-settings/tests/test_contract.py contains test_a_secret_field_may_not_carry_a_default
  CHECK: file catalog/typed-settings/evidence/mutation.md contains mutmut 2.5.1
  CHECK: file catalog/typed-settings/impl/python/typed_settings_impl.py lacks dev_default_ok

verification_command: |
  cd <your registered hardware-store worktree>
  export PATH="$PWD/.venv/bin:$PATH"
  git fetch origin && git rev-list --count HEAD..origin/main   # must print 0
  make check

definition_of_done: >
  `secret=True` redacts in repr and str ALWAYS, whether or not the field carries a default.
  `secret=True` with a default still RAISES SettingsError, exactly as today, unless the
  declaration also passes the explicit opt-out.
  The opt-out is named so it is greppable across every repository in one command; `dev_default_ok`
  is the proposed name and you may argue for a better one in the RETURN rather than silently
  choosing your own.
  A field declared `secret=True, default=..., dev_default_ok=True` is accepted AND redacted.
  Every existing contract test still passes UNCHANGED.
  make check green, and the mutation gate re-run and re-filed.

compatibility: >
  HARD. Not one existing declaration may change meaning. `secret=True` alone behaves exactly as
  today. `secret=True` with a default and no opt-out fails exactly as today, with the same error
  class. If any existing test needs editing to pass, STOP: that is a semantic break wearing a
  refactor, and it is a block rather than a judgement call.

mutation_gate: >
  REQUIRED and re-filed. `catalog/typed-settings/evidence/mutation.md` records 24 killed / 31
  mutants = 77.4% against a 70% threshold, at mutmut 2.5.1 PINNED. The pin is load-bearing: 3.7.0
  was tried and does not run this Part. Re-run at 2.5.1, and if the score falls below 70 the order
  is BLOCKED, not adjusted.

out_of_scope: >
  Secret storage, rotation, distribution. File-format configuration. Any other Part.
  Migrating consumers. Changing the threshold. Changing the mutmut pin.

approval_gates: >
  Founder merges. No self-certification. This Part is in the Certified Tier and this order changes
  its security semantics, so the refusal cases matter more than the acceptance case: a permissive
  change that keeps the suite green proves nothing on its own.

rollback: >
  git revert. One implementation, one contract document, one card, additive tests.

file_allowlist:
  - catalog/typed-settings/impl/python/typed_settings_impl.py
  - catalog/typed-settings/contract/typed_settings.py
  - catalog/typed-settings/tests/test_contract.py       # ADDITIVE only
  - catalog/typed-settings/CARD.md                      # the stated semantics
  - catalog/typed-settings/evidence/mutation.md         # the re-filed score
  - handoff/CX-012/RETURN.md                            # NEW, explicitly authorised

contract_tests:       catalog/typed-settings/tests/test_contract.py
contract_test_policy: |
  ADDITIVE. The sixteen existing tests are ASSERTION-LOCKED and must pass unchanged.
  Add, at minimum, all four:
    a secret WITH a default and the opt-out is ACCEPTED
    that same field is REDACTED in repr, with a production-shaped value injected over the default
    a secret with a default and NO opt-out still RAISES, same error class as today
    a NON-secret field is still not redacted, so redaction did not become universal by accident

return_artifact:      handoff/CX-012/RETURN.md
return_authorisation: |
  EXPLICITLY AUTHORISED. Required. Record what the gate COLLECTED as well as what passed, and
  paste the mutation score with its command.

store_search_result: |
  SEARCH BOTH TIERS and log both. Search "secret", "redact", "settings", "environment".
  This IS the Part, so the search is for something that already solves the SEPARATION, not for
  the Part itself.

parts_to_consume: |
  UNKNOWN until you search. Likely none.

watch_for: |
  The failure mode here is a change that makes the suite greener by making the Part more
  permissive. The four contract tests above are locked in both directions for that reason. If you
  find yourself deleting or loosening an existing assertion, that is the block.
```

## The measurement, taken 2026-08-12 on origin/main

`CMD` The refusal, today:

```
ts.field("stripe_api_key", str, default="sk_test_dev", secret=True)
SettingsError: secret field 'stripe_api_key' may not carry a default
```

`CMD` So the consumer drops `secret=True` to keep the default, and a production value is loaded
over it:

```
Settings(jwt_secret='***', stripe_api_key='sk_live_51REALPRODUCTIONKEY')

jwt_secret      leaked in repr: False
stripe_api_key  leaked in repr: True
```

**The Part pushed the consumer into a strictly worse state than declaring nothing.** That is the
whole defect. The rule is right; its enforcement forces an unsafe workaround.

## Why the rule survives

The contract's own words: *"'dev-only-change-me' as a fallback IS a hardcoded secret, and two
repositories in this fleet shipped exactly that, one of them while documenting the opposite."*

That rule stays ON by default. Every existing declaration keeps failing exactly as it does today.
What changes is that a consumer with a genuine need writes the exception down, where a reviewer and
a grep can both find it, instead of expressing it by removing redaction.

## Invariant

**A field declared secret is redacted, always. Whether it may carry a default is a separate
question, answered conservatively unless a human wrote the exception down.**
