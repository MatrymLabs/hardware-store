"""Contract tests for the typed-settings Part.

WRITTEN BEFORE ANY IMPLEMENTATION, AND ASSERTION-LOCKED. Codex implements until these pass and
does not edit an assertion. If an assertion looks wrong, that is an escalation, not a fix.

These run against ANY implementation of the port, not against one adapter. The implementation is
supplied by `loader` in conftest; nothing here imports a concrete module.

Each test states the rule it protects and, where the rule came from a real defect, the defect.
The central one: on 2026-08-10 both `recall` and `saas-starter` shipped

    jwt_secret: str = "dev-only-change-me"  # overridden by JWT_SECRET; prod must set a real one

character-for-character, and `saas-starter`'s own module docstring promised that a blank secret
"must fail loud rather than sign tokens with a guessable key". Nothing implemented it. The
guarantee was prose in one repo, absent in the other, and untested in both. That is why this Part
has a contract rather than a convention.
"""

from __future__ import annotations

import pytest
from typed_settings import MISSING, SettingsError

# --- 1. the declaration itself must fail loud -------------------------------------------------


def test_a_secret_field_may_not_carry_a_default(loader) -> None:
    """The rule the whole Part exists for.

    A default IS a hardcoded secret whenever the variable is unset. Rejecting it at DECLARATION
    time, not at load time, means the mistake cannot reach a running process at all.
    """
    with pytest.raises(SettingsError) as caught:
        loader.field("jwt_secret", str, default="dev-only-change-me", secret=True)
    assert "secret" in str(caught.value).lower()


def test_a_secret_field_without_a_default_is_accepted(loader) -> None:
    """Guard against over-correction: secrets must still be declarable."""
    field = loader.field("jwt_secret", str, secret=True)
    assert field.required is True
    assert field.secret is True


def test_a_non_secret_may_carry_a_default(loader) -> None:
    """Inference I2. Requiring every value makes local development hostile and pushes people to
    commit .env files, which defeats the point."""
    field = loader.field("port", int, default=8000)
    assert field.required is False
    assert field.default == 8000


def test_the_env_var_name_defaults_to_the_upper_cased_field_name(loader) -> None:
    assert loader.field("jwt_secret", str, secret=True).env == "JWT_SECRET"
    assert loader.field("port", int, default=1, env="APP_PORT").env == "APP_PORT"


# --- 2. loading: required, coercion, and naming the variable ----------------------------------


def test_a_missing_required_value_raises_and_names_the_ENV_VAR(loader) -> None:
    """Inference I5. The operator reading this error is looking at a deploy config, not at source,
    so the message must carry the environment variable rather than the attribute name."""
    fields = [loader.field("jwt_secret", str, secret=True)]
    with pytest.raises(SettingsError) as caught:
        loader.load(fields, {})
    assert "JWT_SECRET" in str(caught.value)


def test_a_present_required_value_loads(loader) -> None:
    fields = [loader.field("jwt_secret", str, secret=True)]
    settings = loader.load(fields, {"JWT_SECRET": "s3kr1t-from-the-platform"})
    assert settings.jwt_secret == "s3kr1t-from-the-platform"
    assert settings["jwt_secret"] == "s3kr1t-from-the-platform"


def test_a_missing_optional_value_takes_its_default(loader) -> None:
    fields = [loader.field("port", int, default=8000)]
    assert loader.load(fields, {}).port == 8000


def test_a_declared_type_is_enforced(loader) -> None:
    """A port that arrives as the string "80O0" and is used in arithmetic fails somewhere far from
    the mistake. Coercion at load keeps the failure next to its cause."""
    fields = [loader.field("port", int, default=8000)]
    assert loader.load(fields, {"PORT": "9000"}).port == 9000
    with pytest.raises(SettingsError) as caught:
        loader.load(fields, {"PORT": "not-a-number"})
    assert "PORT" in str(caught.value)


def test_EVERY_problem_is_reported_not_only_the_first(loader) -> None:
    """A loader that stops at the first missing variable turns one deploy into five, each
    discovering the next omission. This is the single most useful behaviour in practice."""
    fields = [
        loader.field("jwt_secret", str, secret=True),
        loader.field("database_url", str, secret=True),
        loader.field("port", int, default=8000),
    ]
    with pytest.raises(SettingsError) as caught:
        loader.load(fields, {"PORT": "not-a-number"})
    message = str(caught.value)
    assert "JWT_SECRET" in message
    assert "DATABASE_URL" in message
    assert "PORT" in message

    # STRENGTHENED after mutation testing. Substring containment let every string mutant survive:
    # wrapping a message in XX...XX still contains the variable name. The SHAPE of the joined
    # message is part of the contract, because an operator reads it as one line.
    assert message.count(";") == 2, f"three problems must be joined into one message: {message!r}"
    assert "; " in message, "problems are not separated readably"


# --- 3. secrets must not leak through a representation ----------------------------------------


def test_repr_redacts_every_secret(loader) -> None:
    """Claim 5, and the one most likely to be got wrong. A settings object that prints its own JWT
    secret into a traceback or a log line undoes the reason this Part exists."""
    fields = [
        loader.field("jwt_secret", str, secret=True),
        loader.field("port", int, default=8000),
    ]
    settings = loader.load(fields, {"JWT_SECRET": "s3kr1t-from-the-platform"})

    # STRENGTHENED after mutation testing. The original asserted only that the secret was ABSENT,
    # so a mutant changing the redaction marker '***' to 'XX***XX' survived: the secret was still
    # gone, and nothing checked what replaced it. Absence is half the property; the other half is
    # that a reader can see a value was withheld rather than that the field is missing.
    for rendered in (repr(settings), str(settings)):
        assert "s3kr1t-from-the-platform" not in rendered, "a secret leaked through a repr"
        # The marker must be EXACT. Accepting a substring would let a mutant widen '***' to
        # 'XX***XX' unnoticed, which is precisely what survived before this was tightened.
        # Either quoting style is allowed, because the port is language-agnostic and the
        # property is "an exact, recognisable marker", not "Python repr quoting".
        assert ("jwt_secret='***'" in rendered) or ("jwt_secret=***" in rendered), (
            f"the secret is not marked with an exact redaction marker: {rendered!r}"
        )
    assert "port=8000" in repr(settings), "redaction must not hide non-secrets too"
    assert repr(settings).startswith("Settings("), "the repr does not name its own type"
    assert repr(settings).endswith(")")


def test_the_secret_is_still_readable_through_the_attribute(loader) -> None:
    """Guard against over-correction: redaction is for representations, not for access."""
    fields = [loader.field("jwt_secret", str, secret=True)]
    settings = loader.load(fields, {"JWT_SECRET": "s3kr1t-from-the-platform"})
    assert settings.jwt_secret == "s3kr1t-from-the-platform"


# --- 4. immutability and read-once -------------------------------------------------------------


def test_settings_are_immutable(loader) -> None:
    """Inference I4. A value that can change under a running process is harder to reason about
    than a restart, and this Part chose the restart.

    STRENGTHENED 2026-08-10 after mutation testing. The original asserted only that
    `settings.port = 9999` raises, and it passed for the WRONG REASON: `port` is not a declared
    attribute, so assignment raises on a slots class whether or not it is frozen. Mutants that
    flipped `frozen=True` -> `False` and `slots=True` -> `False` both SURVIVED. A test that
    passes on a mutable class is not an immutability test.

    The property is asserted directly now, and assignment to a REAL declared attribute is what
    proves frozen-ness.
    """
    import dataclasses

    fields = [loader.field("port", int, default=8000)]
    settings = loader.load(fields, {})

    assert dataclasses.is_dataclass(settings)
    params = type(settings).__dataclass_params__
    assert params.frozen is True, "Settings is not frozen; its values can be rebound in place"

    # assignment to a DECLARED attribute: raises only because the class is frozen
    declared = [f.name for f in dataclasses.fields(settings)]
    assert declared, "Settings declares no fields, so frozen-ness cannot be exercised"
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(settings, declared[0], "rebound")

    # and an undeclared name is still refused. Narrow, not blind: a frozen dataclass raises
    # FrozenInstanceError, a slots class raises AttributeError, and either is a correct refusal.
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError, TypeError)):
        settings.port = 9999  # type: ignore[misc]


def test_the_declaration_type_is_frozen_and_slotted(loader) -> None:
    """The Field declaration must be immutable too. A mutable declaration means one caller can
    change another's field object after the fact, which makes the secret flag advisory."""
    import dataclasses

    declared = loader.field("jwt_secret", str, secret=True)
    assert dataclasses.is_dataclass(declared)
    assert type(declared).__dataclass_params__.frozen is True
    assert hasattr(type(declared), "__slots__"), "the declaration is not slotted"
    with pytest.raises(dataclasses.FrozenInstanceError):
        declared.secret = False  # type: ignore[misc]


def test_the_loaded_values_are_a_defensive_copy(loader) -> None:
    """A frozen wrapper around someone else's mutable dict is not immutable.

    Written twice. The first version asserted `settings["port"] = 9999` raises, and it passed for
    the WRONG REASON: the type defines no `__setitem__`, so item assignment raises whether or not
    the stored mapping is a copy. The mutant that renamed the internal attribute the constructor
    re-wraps SURVIVED it.

    The real property is a defensive copy: values are read ONCE at load, so a caller mutating the
    mapping it handed in afterwards cannot change what the process already validated. That is
    inference I4 (read once) made testable.
    """
    source = {"PORT": "8000"}
    settings = loader.load([loader.field("port", int, default=1)], source)

    source["PORT"] = "1234"
    assert settings.port == 8000, "settings changed when the caller mutated its own mapping"

    # Narrow, not blind: a mapping with no __setitem__ raises TypeError.
    with pytest.raises((TypeError, AttributeError)):
        settings["port"] = 9999  # type: ignore[index]


def test_loading_does_not_mutate_the_environment_it_was_given(loader) -> None:
    """A loader that writes back into the environment makes test isolation impossible and couples
    every consumer to import order."""
    environ = {"JWT_SECRET": "s3kr1t-from-the-platform"}
    before = dict(environ)
    loader.load([loader.field("jwt_secret", str, secret=True)], environ)
    assert environ == before


# --- 5. the sentinel is not a value ------------------------------------------------------------


def test_MISSING_is_distinct_from_None(loader) -> None:
    """None is a legitimate default. If MISSING were None, a field defaulting to None would be
    silently treated as required, which is a bug that only shows up in someone else's deploy."""
    field = loader.field("maybe", object, default=None)
    assert field.required is False
    assert field.default is None
    assert MISSING is not None
