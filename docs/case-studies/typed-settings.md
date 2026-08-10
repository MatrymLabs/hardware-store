# Case study: how one duplicated config class became a certified part

**Part:** PRT-0006 `typed-settings` · **Certified:** 2026-08-10 (RD-2026-0014) ·
**Consumers:** `recall`, `saas-starter`

This is the first capability to travel the full extraction path in this repository, from observed
duplication to a certified part with two independent consumers. It is written up because the
interesting results were the ones that went wrong.

---

## 1. The principle studied

Two claims from published sources, neither of them ours:

- **Twelve-Factor III:** configuration belongs in the environment, not in the code.
- **OWASP ASVS 2.10.4:** secrets are not hardcoded.

Both are widely agreed and widely followed, and following both is not sufficient. A codebase can
read every value from the environment, hardcode nothing, and still ship a guessable production
credential. That is the gap this part addresses, and it was found in our own code rather than
theorised.

### The defect, as found

Two independently written repositories carried this line **character for character**:

```python
jwt_secret: str = "dev-only-change-me"  # overridden by JWT_SECRET; prod must set a real one
```

The value is read from the environment, and it is not hardcoded in any sense that a scanner would
flag, because it is a *default*. It is only a credential when the environment variable is missing,
which is exactly the circumstance in which nobody is looking.

One of the two repositories had a module docstring promising that a blank secret *"must fail loud
rather than sign tokens with a guessable key."* **Nothing implemented it.** The guarantee was
prose in one repo, absent in the other, and untested in both.

### The rule that is genuinely ours

Neither source says it, so it is recorded as our inference rather than borrowed authority:

> **A field marked secret may not carry a default.**

A default *is* a hardcoded secret in every run where the variable is unset. The rule is enforced at
**declaration** time, not at load time, so the mistake cannot reach a running process at all.

---

## 2. The port

The part is a **contract plus an implementation**, not a library. The contract is protocols and
types with no behaviour; the test suite imports **only** the contract and receives the
implementation through a fixture. The same suite therefore runs unchanged against an
implementation in another language, which is the point of indexing the catalogue by capability
rather than by package.

```
declare fields  ->  load once from a mapping you HAND it  ->  immutable, type-coerced view
```

Three decisions worth defending:

**It never reads `os.environ` itself.** It reads the mapping it is given. A consumer controls the
source, and a test needs no monkeypatching of global state.

**It reports every problem at once.** A loader that stops at the first missing variable turns one
deploy into five. The error names the **environment variable**, not the attribute, because the
person reading it is looking at a deploy config.

**Secrets are redacted from `repr` and `str`.** A settings object cannot print a signing key into a
traceback or a log line.

---

## 3. The verification, including the part that failed

### The tests failed before the implementation existed

```
14 failed        # against an empty adapter
16 passed        # after implementation, and after the suite was strengthened
```

Fourteen, then sixteen. Two tests were added because of what happened next.

### The mutation gate falsified the tests, not the code

Mutation testing introduces deliberate defects and asks whether the suite notices. The first run
scored **20/31 = 64.5%**, below our 70 threshold, **and the implementation was correct.**

Three tests were passing without proving their claim:

| test | why it passed anyway |
|---|---|
| `test_settings_are_immutable` | asserted that assigning to `settings.port` raises. It raises because `port` is not a *declared* attribute on a slots class, whether or not the class is frozen. Mutants flipping `frozen=True` to `False` **survived**. The test would have passed on a mutable class. |
| `test_repr_redacts_every_secret` | asserted the secret was *absent* from the repr, never what replaced it. Mutating the redaction marker from `***` to `XX***XX` **survived**. |
| `test_the_underlying_mapping_cannot_be_written_through` | asserted item assignment raises. It does, because the type defines no `__setitem__` **at all**. The test proved nothing about defensive copying. |

Rewritten to assert the properties directly (`__dataclass_params__.frozen`, an exact redaction
marker, and a genuine defensive-copy check that mutates the caller's mapping after load), the score
went to **24/31 = 77.4%**.

**This is the strongest evidence in the record, and it is an argument against our tests rather than
for our code.** A gate that can only agree with you is decoration.

The seven surviving mutants are each argued in the part's `evidence/mutation.md`. Six are
message-text mutations left alive deliberately, because pinning human-readable prose would make a
language-agnostic contract untranslatable. One is genuinely equivalent, confirmed by hand.

### The tool version turned out to be load-bearing

mutmut 3.7.0 **cannot run this layout at all**: it does not copy `conftest.py` into its mutants
directory and reports every mutant unchecked. Four configurations were tried before the cause was
identified. 2.5.1 runs it unmodified and is now pinned.

That pin is not housekeeping. An earlier part in this catalogue was certified at **88%** from an
unpinned 2.x run, and **that number is not currently reproducible.** A score you cannot reproduce
is a claim, not a measurement, and it is recorded that way.

---

## 4. The reuse

The bar is **two independent consumers**, not one. One consumer proves a part runs. It cannot tell
you whether the contract fits anything but the case it was extracted from.

| consumer | result |
|---|---|
| `recall` | 65 passed, 94.43% coverage |
| `saas-starter` | 72 passed, 94.15% coverage |

In both, the local settings class was **removed rather than wrapped**, verified by
`grep -c BaseSettings app/config.py` returning `0`. The two vendored implementations differ by
exactly one line, an import path.

### What the second consumer found, which the first could not

`secret=True` currently means two things at once: *redacted in output* and *may not carry a
default*. A consumer cannot ask for one without the other.

`saas-starter` has Stripe fields that must keep a development default, so they had to be declared
as ordinary fields. Loading a production-shaped environment shows the consequence:

```
Settings(..., jwt_secret='***', ..., stripe_api_key='sk_live_51REALPRODUCTIONKEY', ...)

jwt_secret             leaked in repr: False
stripe_api_key         leaked in repr: True
```

The development placeholder is harmless. The **real production value injected over it is not
redacted**, because the declaration had to choose between having a default and being a secret.

Filed as an issue against the part, recorded on its card as a known limitation, and **not** fixed
in the pull request that found it: changing a certified contract needs its own review and a re-run
of the mutation gate at the pinned version. The consuming repo did not fork the part or work
around it.

This is the second-consumer rule earning its keep, and the argument for it is now evidence rather
than assertion.

---

## 5. What this does not claim

- **Not that the implementation is bug-free.** 77.4% means 24 of 31 deliberate defects are caught.
- **Not that the catalogue is proven.** One capability cleared the two-consumer bar here. Three of
  six parts still sit at one consumer.
- **Not a performance claim.** Loading is O(fields) once per process and is not on any hot path,
  but it is **unmeasured**, and the card says so. No claim may cite a number that does not exist.
- **Not a throughput measurement.** This ran inside a single working session, which is a duration,
  not a rate.

---

## 6. What we would tell another team

**Extract on the second occurrence, never the first.** This part exists because the same code was
found twice, in two shipping repositories, carrying the same defect. Duplication is cheaper than
the wrong abstraction, and a capability written once has not told you what its contract is yet.

**Make the guarantee structural, not documentary.** The promise already existed as a comment in one
repo and was simply not true. Moving it into a contract with a test suite is the difference between
a convention a reader must apply and a control that applies itself.

**Point the gates at your tests, not just your code.** The mutation run found nothing wrong with
the implementation and three things wrong with the suite verifying it, including an immutability
test that would have passed on a mutable class. Those tests had been green the whole time.

**A gate is not evidence until you have watched it fail.** Every verdict cited here was accompanied
by a deliberate sabotage that reddened it and a restore that returned it to green. A `PASS` from a
gate nobody has ever seen fail is an untested assertion wearing a verdict's clothes.
