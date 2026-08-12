"""Standard-library implementation of the typed-settings contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from typed_settings import MISSING, SettingsError


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


@dataclass(frozen=True, slots=True)
class _Field:
    """One setting declaration, validated before any process can load it."""

    name: str
    type: type
    default: Any
    secret: bool
    env: str

    @property
    def required(self) -> bool:
        return self.default is MISSING


@dataclass(frozen=True)
class _Settings(Mapping[str, Any]):
    """An immutable settings view that redacts only declared secrets in representations."""

    _values: Mapping[str, Any]
    _secret_names: frozenset[str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "_values", MappingProxyType(dict(self._values)))

    def __getitem__(self, item: str) -> Any:
        return self._values[item]

    def __iter__(self):
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __getattr__(self, item: str) -> Any:
        try:
            return self._values[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def __repr__(self) -> str:
        rendered = ", ".join(
            f"{name}={'***' if name in self._secret_names else value!r}"
            for name, value in self._values.items()
        )
        return f"Settings({rendered})"

    __str__ = __repr__
mutants_x_field__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_field__mutmut)
def field(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_orig(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_1(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = True,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_2(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = True,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_3(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING or not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_4(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret or default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_5(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_6(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_7(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(None)
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_8(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=None, type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_9(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=None, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_10(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=None, secret=secret, env=env or name.upper())


def x_field__mutmut_11(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=None, env=env or name.upper())


def x_field__mutmut_12(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=None)


def x_field__mutmut_13(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(type=type_, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_14(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, default=default, secret=secret, env=env or name.upper())


def x_field__mutmut_15(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, secret=secret, env=env or name.upper())


def x_field__mutmut_16(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, env=env or name.upper())


def x_field__mutmut_17(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, )


def x_field__mutmut_18(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env and name.upper())


def x_field__mutmut_19(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
    dev_default_ok: bool = False,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback unless explicitly opted out."""
    if secret and default is not MISSING and not dev_default_ok:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.lower())

mutants_x_field__mutmut['_mutmut_orig'] = x_field__mutmut_orig # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_1'] = x_field__mutmut_1 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_2'] = x_field__mutmut_2 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_3'] = x_field__mutmut_3 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_4'] = x_field__mutmut_4 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_5'] = x_field__mutmut_5 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_6'] = x_field__mutmut_6 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_7'] = x_field__mutmut_7 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_8'] = x_field__mutmut_8 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_9'] = x_field__mutmut_9 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_10'] = x_field__mutmut_10 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_11'] = x_field__mutmut_11 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_12'] = x_field__mutmut_12 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_13'] = x_field__mutmut_13 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_14'] = x_field__mutmut_14 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_15'] = x_field__mutmut_15 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_16'] = x_field__mutmut_16 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_17'] = x_field__mutmut_17 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_18'] = x_field__mutmut_18 # type: ignore # mutmut generated
mutants_x_field__mutmut['x_field__mutmut_19'] = x_field__mutmut_19 # type: ignore # mutmut generated
mutants_x_load__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_load__mutmut)
def load(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_orig(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_1(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = None
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_2(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = None
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_3(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = None
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_4(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(None)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_5(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = None
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_6(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(None, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_7(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, None)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_8(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_9(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, )
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_10(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is not MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_11(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(None)
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_12(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = None
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_13(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            break
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_14(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = None
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_15(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(None)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_16(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                None
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_17(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError(None)
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_18(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(None))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_19(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("XX; XX".join(errors))
    return _Settings(values, frozenset(secret_names))


def x_load__mutmut_20(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(None, frozenset(secret_names))


def x_load__mutmut_21(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, None)


def x_load__mutmut_22(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(frozenset(secret_names))


def x_load__mutmut_23(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, )


def x_load__mutmut_24(fields: list[_Field], environ: Mapping[str, str]) -> _Settings:
    """Validate and coerce one environment mapping, reporting every discovered problem."""
    values: dict[str, Any] = {}
    errors: list[str] = []
    secret_names: set[str] = set()
    for declared in fields:
        if declared.secret:
            secret_names.add(declared.name)
        raw = environ.get(declared.env, MISSING)
        if raw is MISSING:
            if declared.required:
                errors.append(f"missing required environment variable {declared.env}")
            else:
                values[declared.name] = declared.default
            continue
        try:
            values[declared.name] = declared.type(raw)
        except (TypeError, ValueError):
            errors.append(
                f"environment variable {declared.env} cannot be coerced to {declared.type.__name__}"
            )
    if errors:
        raise SettingsError("; ".join(errors))
    return _Settings(values, frozenset(None))

mutants_x_load__mutmut['_mutmut_orig'] = x_load__mutmut_orig # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_1'] = x_load__mutmut_1 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_2'] = x_load__mutmut_2 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_3'] = x_load__mutmut_3 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_4'] = x_load__mutmut_4 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_5'] = x_load__mutmut_5 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_6'] = x_load__mutmut_6 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_7'] = x_load__mutmut_7 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_8'] = x_load__mutmut_8 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_9'] = x_load__mutmut_9 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_10'] = x_load__mutmut_10 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_11'] = x_load__mutmut_11 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_12'] = x_load__mutmut_12 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_13'] = x_load__mutmut_13 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_14'] = x_load__mutmut_14 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_15'] = x_load__mutmut_15 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_16'] = x_load__mutmut_16 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_17'] = x_load__mutmut_17 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_18'] = x_load__mutmut_18 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_19'] = x_load__mutmut_19 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_20'] = x_load__mutmut_20 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_21'] = x_load__mutmut_21 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_22'] = x_load__mutmut_22 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_23'] = x_load__mutmut_23 # type: ignore # mutmut generated
mutants_x_load__mutmut['x_load__mutmut_24'] = x_load__mutmut_24 # type: ignore # mutmut generated
