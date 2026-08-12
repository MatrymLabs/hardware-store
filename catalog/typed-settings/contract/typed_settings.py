"""Contract: typed-settings -- the interface every implementation of this Part honors.

Language-agnostic in intent (stated here as Python Protocols and signatures). An implementation in
any language provides the same surfaces with the same semantics: a DECLARATION of what the process
needs from its environment, and a LOADER that turns the environment into a validated, immutable
view of it, or fails loud naming what is missing.

  Field(name, type, default=MISSING, secret=False, env=None, dev_default_ok=False)
      One declared setting. `name` is the attribute; `env` is the environment variable (defaulting
      to the upper-cased name). `type` is the target type for coercion.

      A field with no `default` is REQUIRED.
  A field with `secret=True` MAY NOT carry a default unless the declaration also sets the explicit
  `dev_default_ok=True` escape hatch. Without that opt-out, construction FAILS LOUD (SettingsError).
  With it, the field remains redacted in every representation.

  load(fields, environ) -> Settings
      Read `environ` ONCE, coerce each declared field to its type, and return an immutable
      Settings. Raises SettingsError, naming EVERY problem found rather than only the first, when:
        - a required field is absent from the environment
        - a value cannot be coerced to the declared type
      The error message names the ENVIRONMENT VARIABLE, not the attribute, because the operator
      reading it is looking at a deploy config and not at this source.

  Settings
      An immutable mapping-like view. `settings.name` and `settings["name"]` both work.
      Its repr and str MUST redact every field declared `secret=True`. A settings object that
      prints a JWT secret into a traceback undoes the reason this Part exists.

WHAT THIS IS NOT. Not secret storage, rotation, or distribution: it reads what the platform
provides. Not file-format configuration (TOML/YAML profiles are a different capability). Not
feature flags. Not hot reload: the environment is read once, deliberately, so a value cannot
change under a running process.

Provenance: RD-2026-0014. Sources are specifications, not implementations: 12factor III (config in
the environment), OWASP ASVS 2.10.4 (secrets are not hardcoded), and pydantic-settings docs for
library behaviour. No copyleft implementation was studied and no clean-room wall is claimed,
because none was required.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

MISSING: Any = ...
"""Sentinel: this field has no default and is therefore required.

A distinct sentinel rather than None, because None is a legitimate default value.
"""


class SettingsError(Exception):
    """Raised when a declaration is invalid, or the environment does not satisfy it.

    Fails loud on purpose. The alternative -- returning a partially-populated object -- moves the
    failure from startup to whenever the missing value is first touched, which in an auth path
    means a request rather than a deploy.
    """


@runtime_checkable
class Field(Protocol):
    """One declared setting."""

    name: str
    env: str
    type: type
    default: Any
    secret: bool

    @property
    def required(self) -> bool:
        """True when this field has no default and must come from the environment."""
        ...


@runtime_checkable
class Settings(Protocol):
    """An immutable, validated view of the environment."""

    def __getattr__(self, item: str) -> Any: ...

    def __getitem__(self, item: str) -> Any: ...

    def __repr__(self) -> str:
        """MUST redact every field declared secret. Enforced by the contract suite."""
        ...


@runtime_checkable
class SettingsLoader(Protocol):
    """The loader surface an implementation provides."""

    def field(
        self,
        name: str,
        type_: type,
        *,
        default: Any = MISSING,
        secret: bool = False,
        env: str | None = None,
        dev_default_ok: bool = False,
    ) -> Field:
        """Declare one field. Secret defaults require explicit dev_default_ok."""
        ...

    def load(self, fields: list[Field], environ: dict[str, str]) -> Settings:
        """Validate `environ` against `fields`, or raise SettingsError naming every problem."""
        ...
