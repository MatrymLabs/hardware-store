# Mutation evidence: PRT-0006 typed-settings

**Result: 24 killed / 31 mutants = 77.4%**, above the fleet's certified threshold of 70.

## Exact command and toolchain

```bash
cd rd/02-experiments/PRT-0006-typed-settings
export PATH="/home/josh/Projects/MatrymLabs/.venv/bin:$PATH"
mutmut run --paths-to-mutate impl/python
mutmut results
```

- **mutmut 2.5.1**, pinned in ship's `pyproject.toml`.
- Python 3.12, this host.

**The version is load-bearing and the pin is not decoration.** mutmut **3.7.0** was tried first and
**cannot run this Part layout at all**: it copies `setup.cfg`, `tests/` and `impl/` into `mutants/`
but not `conftest.py`, then reports every mutant `not checked` and stops with *"could not find any
test case for any mutant"*. Four conftest shapes were tried (file-relative, cwd-relative, package
import, module-level import) and none mapped. 2.5.1 runs this Part **unmodified**.

Related, and worth knowing before trusting any older number: the `retry` Part's recorded **88%**
was produced by a 2.x run, nothing pinned the tool, and 3.x is a rewrite. That figure is currently
not reproducible. This pin stops PRT-0006 inheriting the same problem.

## What the first run found: the tests, not the adapter

The first measurement was **20/31 = 64.5%**, below the bar. The adapter was correct; the
**contract tests were weaker than they looked**, and two passed for the wrong reason:

| survivor | what it proved |
|---|---|
| `frozen=True` -> `frozen=False` | `test_settings_are_immutable` asserted `settings.port = 9999` raises. It raises because `port` is not a declared attribute on a slots class, **whether or not the class is frozen**. The test would pass on a mutable class. |
| `slots=True` -> `slots=False` | same test, same wrong reason |
| `'***'` -> `'XX***XX'` | `test_repr_redacts_every_secret` asserted only that the secret was ABSENT. Nothing checked what replaced it, so the redaction marker could be anything. |

Fixed by asserting the property directly: `__dataclass_params__.frozen`, `__slots__`, a
`FrozenInstanceError` on a **declared** attribute, and an exact redaction marker.

A third test was then rewritten for the same reason. `test_the_underlying_mapping_cannot_be_written_through`
asserted `settings["port"] = 9999` raises, which it does because the type defines no
`__setitem__` at all. It is now `test_the_loaded_values_are_a_defensive_copy`, which mutates the
caller's mapping after load and asserts the settings do not change. That is the real property.

## The 7 survivors, each argued

Six are **string-literal mutations** that wrap message text or a separator in `XX...XX`:

| id | mutation |
|---|---|
| 9 | `", "` -> `"XX, XX"` (repr separator) |
| 12 | repr field format wrapped |
| 19 | `"secret field ... may not carry a default"` wrapped |
| 26 | `"missing required environment variable ..."` wrapped |
| 30 | `"... cannot be coerced to ..."` wrapped |
| 31 | `"; "` -> `"XX; XX"` (error joiner) |

**Deliberately not killed.** Killing them means asserting exact human-readable message text in a
**language-agnostic contract**. An implementation in Go or Rust would word these differently and
must still satisfy the port. The tests assert what the contract actually requires: that the
message NAMES the environment variable, that every problem appears, and that problems are joined
into one message. Pinning the prose would make the contract untranslatable, which is a worse
defect than a surviving string mutant.

The seventh is **equivalent**:

- **8**: `object.__setattr__(self, "_values", ...)` -> `"XX_valuesXX"`. This re-wrap in
  `__post_init__` is belt-and-braces. `load()` already constructs a fresh dict of coerced values,
  so the defensive copy is real without it, and the `MappingProxyType` wrapper it adds is
  unobservable because the type defines no `__setitem__`. The mutant changes nothing a caller can
  detect. Confirmed by hand: mutating the source mapping after load leaves `settings.port`
  unchanged either way.

## Honest limit

77.4% is a real measurement of these tests against this adapter on this host. It is not a claim
that the adapter is correct, only that the suite bites: 24 of 31 deliberate defects are caught,
and the 7 that are not have been read and argued rather than counted.
