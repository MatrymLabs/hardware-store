"""Contract: lexicon_gate -- the interface every implementation of the term-policy gate honors.

build_lexicon(rules, *, case_sensitive=False, suppress=None) -> Lexicon
    Compile a validated policy from plain rule data (each a mapping with a non-empty id + pattern,
    optional hint/suggest/case_sensitive). FAILS LOUD (LexiconError) on an empty list, a bad rule
    rule, a missing id/pattern, or an invalid rule/suppress regex.
scan_text(text, lexicon, *, label="") -> LexiconReport
    Scan text line by line; a line matching the lexicon's suppress pattern is exempt (inline
    allowlist). Returns a REPORT (.clean + located Findings in line/column order + .summary()),
    never a bare bool. Pure: no I/O, no filesystem.
Finding: label, line, column, rule_id, matched, suggest, hint (+ .as_dict()).
LexiconError(ValueError): raised on a malformed policy.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol


class FindingContract(Protocol):
    label: str
    line: int
    column: int
    rule_id: str
    matched: str
    suggest: str
    hint: str


class ReportContract(Protocol):
    findings: tuple[FindingContract, ...]

    @property
    def clean(self) -> bool: ...
    def summary(self) -> str: ...


class BuildLexicon(Protocol):
    def __call__(
        self,
        rules: Sequence[Mapping[str, object]],
        *,
        case_sensitive: bool = False,
        suppress: str | None = None,
    ) -> object: ...


class ScanText(Protocol):
    def __call__(self, text: str, lexicon: object, *, label: str = "") -> ReportContract: ...
