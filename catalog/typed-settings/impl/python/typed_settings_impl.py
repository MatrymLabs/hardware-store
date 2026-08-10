"""Standard-library implementation of the typed-settings contract."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from typed_settings import MISSING, SettingsError


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


def field(
    name: str,
    type_: type,
    *,
    default: Any = MISSING,
    secret: bool = False,
    env: str | None = None,
) -> _Field:
    """Declare a setting, rejecting an unsafe secret fallback immediately."""
    if secret and default is not MISSING:
        raise SettingsError(f"secret field {name!r} may not carry a default")
    return _Field(name=name, type=type_, default=default, secret=secret, env=env or name.upper())


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
