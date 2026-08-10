+++
part_id = "PRT-0006"
canonical_name = "typed-settings"
capability = "Declare what a process needs from its environment, then load it once into an immutable, type-coerced, validated view. A field marked secret MAY NOT carry a default, so a missing secret is a startup failure rather than a guessable fallback. Every problem in the environment is reported together, naming the environment variable."
category = "Development"
maturity = "CERTIFIED"
contract = "contract/typed_settings.py"
inputs = "a list of declared Fields (name, target type, optional default, secret flag, optional env var override); an environment mapping (str -> str)"
outputs = "an immutable Settings view supporting attribute and item access, whose repr and str redact every secret; or SettingsError naming every unsatisfied variable at once"
permissions = "none. It reads the mapping it is HANDED, never os.environ directly, so a consumer controls the source and a test needs no monkeypatching of global state"
security = "the reason this Part exists. A secret field with a default is rejected at DECLARATION time, so the mistake cannot reach a running process. Secrets are redacted from repr and str, so a settings object cannot print a JWT key into a traceback or a log line. Fail-loud on a missing secret turns a silent auth weakness into a failed deploy."
accessibility = "n/a (library primitive)"
performance = "unmeasured at CANDIDATE. Loading is O(fields) once per process and cached by the consumer; it is not on any hot path. To be recorded before CERTIFIED."
failure_modes = [
  "SettingsError at DECLARATION when a field is marked secret and given a default (a default is a hardcoded secret whenever the variable is unset)",
  "SettingsError at LOAD when a required field is absent, naming the ENVIRONMENT VARIABLE rather than the attribute, because the operator reading it is looking at a deploy config",
  "SettingsError at LOAD when a value cannot be coerced to the declared type, naming the variable",
  "SettingsError reports EVERY problem found, not the first: a loader that stops at the first omission turns one deploy into five",
  "Settings is immutable; assignment raises rather than silently rebinding a value mid-process",
]
migration = ""
deprecation_path = ""

[rd_certification]
verdict = "HARDWARE_STORE_PART"
rd_id = "RD-2026-0014"
decided_by = "Josh Evans (founder), 2026-08-10"
evidence = "rd/03-evidence/RD-2026-0014-evidence.md"
conditions = "CERTIFIED on ONE wired consumer. The pull rule's second-consumer bar (saas-starter) is Stage 5 and still open. The mutation score is reproducible only at mutmut 2.5.1, now pinned; 3.7.0 cannot run this Part layout at all."

[tests]
suite = "tests/test_contract.py"
mutation_score = 77
mutmut_version = "2.5.1"
mutation_tool = "mutmut"

[provenance]
rd_record = "RD-2026-0014"
origin = "reverse-engineered from SPECIFICATIONS, not implementations: 12factor III (config belongs in the environment), OWASP ASVS 2.10.4 (secrets are not hardcoded), and pydantic-settings documentation for library behaviour. No copyleft implementation was studied, so no clean-room wall is claimed and none was required. The port also generalises three of the fleet's own MIT implementations (recall, saas-starter, codeforge)."
clean_room = false
licence_risk = "none. Sources are prose standards (CC-BY-SA, read for principle), MIT documentation, and our own MIT code."

[[implementations]]
language = "python"
path = "impl/python/typed_settings_impl.py"
version = "0.1.0"
benchmark = "unmeasured. Loading is O(fields) once per process and cached by the consumer; it is not on any hot path. Recorded as unmeasured rather than guessed."

[[current_consumers]]
repo = "recall"
path = "recall/recall/typed_settings_impl.py"
version = "0.1.0"
adopted = "2026-08-10"

+++

# typed-settings

## Why this Part exists

It was not designed. It was **extracted**, because the pull rule fired: the capability already
existed, independently implemented, in two shipping products.

`CMD` 2026-08-10, both `recall/recall/config.py` and `saas-starter/app/config.py` carried the same
base class, the same config dict, the same `jwt_secret` / `jwt_algorithm` /
`access_token_ttl_seconds` fields, the same `@lru_cache get_settings()`, and this line
**character-for-character**:

```python
jwt_secret: str = "dev-only-change-me"  # overridden by JWT_SECRET; prod must set a real one
```

`saas-starter`'s module docstring promised that a blank secret *"must fail loud rather than sign
tokens with a guessable key"*. **Nothing implemented it.** The guarantee was prose in one repo,
absent in the other, and untested in both.

That is the argument for a Part rather than a convention. A convention only a reader can apply is
not a control, and a duplicated convention carries its defects as many times as it is duplicated.

The immediate hole was closed ahead of this Part (recall #28, saas-starter #26) because a live gap
should not wait for a six-stage process. This Part makes the fix **portable and permanent**: the
rule moves from two hand-written classes into one contract with a test suite that any
implementation must satisfy.

## The rule that is genuinely ours

The sources establish that config belongs in the environment and that secrets are not hardcoded.
Neither says *"a secret field may not carry a default"*. That inference is this fleet's, it is
recorded as an inference in `RD-2026-0014-claims.md`, and it is the rule the Part enforces at
declaration time rather than at load time, so the mistake cannot reach a running process.

## Status

**CERTIFIED** by R&D verdict RD-2026-0014 on 2026-08-10, on **one** wired consumer.

`recall` consumes it: `recall/config.py` declares its fields through this Part instead of a local
settings class, with the Part vendored at `recall/typed_settings.py` and
`recall/typed_settings_impl.py`, both citing PRT-0006. Verified at 65 passed, 94.43% coverage.

**`saas-starter` is the named second consumer and is NOT yet wired.** It is deliberately absent
from `current_consumers` above, because a card must list consumers that actually consume: listing
a path that does not carry this Part's provenance id would make `consumer-resolves` pass on a
claim that is not true. Stage 5 wires it, and the pull rule's second-consumer bar stays open until
then.

## What the certification rests on, and what it does not

The mutation score of 77.4% was earned on the SECOND attempt. The first measured 64.5%, and the
adapter was correct: three contract tests were passing without proving their claim, including an
immutability test that would have passed on a mutable class. The gate falsified the tests rather
than confirming the code, which is what a mutation gate is for.

The score is reproducible only at **mutmut 2.5.1**, pinned in ship's `pyproject.toml`. 3.7.0
cannot run this Part layout at all. If the pin moves, the number must be re-earned rather than
carried forward.
