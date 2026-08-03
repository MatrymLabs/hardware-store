"""CARD: lexicon_gate -- a prose-governance term-policy gate: find prohibited vocabulary in text.

Clean-room generalization of the fleet nomenclature guard (RD-2026-0004 FH-09; the mechanism is
proven in scripts/check_nomenclature.py, a natural consumer). Where HC-08 workflow_linter
lints the STRUCTURE of a GitHub Actions file, this gate lints the WORDS of any text against a policy
of prohibited-term patterns, and reports every offending line:column with a fix hint.

The reusable core is deliberately smaller than the ship's checker: it is pure and decoupled. It does
NOT read a YAML file, walk a filesystem, or own a CLI - those are the consumer's concern (the ship's
guard loads .nomenclature.yaml and rglob-walks the tree; another consumer might scan a commit
message, a doc string, or an API response). This part only compiles a policy from plain data and
scans text, returning a REPORT (a verdict with the offending findings), never a bare bool.

Two disciplines hold. Fail loud: a malformed rule (missing id/pattern, a non-mapping, or an invalid
regex) raises LexiconError rather than silently scanning nothing. Honest suppression: a caller may
declare a `suppress` pattern (e.g. `pragma: allowlist`) so a line that legitimately names
a prohibited term - a historical note, a rule documenting its own banned word - is exempt, and the
exemption is explicit in the text, not hidden in a path list. Stdlib only (re, dataclasses).
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass


class LexiconError(ValueError):
    """A malformed lexicon policy -- fail loud, never scan against an empty or broken rule set.

    Raised for an empty rule list, a rule that is not a mapping, a rule missing a non-empty `id` or
    `pattern`, or a `pattern` (or `suppress`) that is not a valid regex. A silently-empty policy
    would pass every text, which is the opposite of a gate."""


@dataclass(frozen=True)
class Rule:
    """One prohibited-term pattern and how to explain it: a stable `rule_id`, the compiled `regex`,
    a `hint` (why it is banned) and a `suggest` (what to use instead). Both hints default to ""."""

    rule_id: str
    regex: re.Pattern[str]
    hint: str = ""
    suggest: str = ""


@dataclass(frozen=True)
class Finding:
    """One prohibited term located in text: its `label` (the caller's name for the text, e.g. a
    path; "" when unlabeled), 1-based `line` and `column`, the `rule_id` that fired, the exact
    `matched` substring, and the rule's `suggest`/`hint`. A finding is evidence, never a guess."""

    label: str
    line: int
    column: int
    rule_id: str
    matched: str
    suggest: str = ""
    hint: str = ""

    def as_dict(self) -> dict[str, object]:
        """The finding as a plain dict, for a machine-readable (JSON) report."""
        return {
            "label": self.label,
            "line": self.line,
            "column": self.column,
            "rule": self.rule_id,
            "matched": self.matched,
            "suggest": self.suggest,
            "hint": self.hint,
        }


@dataclass(frozen=True)
class Lexicon:
    """A compiled term policy: the `rules` and an optional `suppress` pattern that exempts
    any line it matches (an inline allowlist, so a legitimate mention of a banned term is shown in
    the text). Build one with `build_lexicon`; it is frozen so a policy cannot drift mid-scan."""

    rules: tuple[Rule, ...]
    suppress: re.Pattern[str] | None = None


@dataclass(frozen=True)
class LexiconReport:
    """The gate's verdict on one text: `.clean` when nothing fired, else the `findings` in location
    order. A report, not a bare bool, so a caller logs the reason and CI renders the offenders."""

    findings: tuple[Finding, ...]

    @property
    def clean(self) -> bool:
        """True when no prohibited term was found (the findings carry the detail either way)."""
        return not self.findings

    def summary(self) -> str:
        """A one-line human summary of the verdict."""
        if self.clean:
            return "lexicon: CLEAN - no prohibited terms found"
        return f"lexicon: {len(self.findings)} prohibited term(s) found"


def _compile(pattern: object, *, case_sensitive: bool, what: str) -> re.Pattern[str]:
    """Compile one regex or fail loud (`LexiconError`) naming `what` broke (rule id / suppress)."""
    if not isinstance(pattern, str) or not pattern:
        raise LexiconError(f"{what} needs a non-empty string pattern")
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        return re.compile(pattern, flags)
    except re.error as exc:
        raise LexiconError(f"{what} has an invalid regex: {exc}") from exc


def build_lexicon(
    rules: Sequence[Mapping[str, object]],
    *,
    case_sensitive: bool = False,
    suppress: str | None = None,
) -> Lexicon:
    """Compile a validated `Lexicon` from plain rule data (the caller loads it from YAML/JSON/etc.).

    Each rule is a mapping with a non-empty `id` and `pattern`, optional `hint`/`suggest`, and an
    optional per-rule `case_sensitive` (else the policy default). A malformed rule fails loud
    (`LexiconError`) - an empty list, a non-mapping rule, a missing id/pattern, or a bad regex. The
    optional `suppress` regex, when given, exempts any line it matches (an inline allowlist)."""
    if not rules:
        raise LexiconError("a lexicon needs at least one rule")
    compiled: list[Rule] = []
    for raw in rules:
        if not isinstance(raw, Mapping):
            raise LexiconError(f"each rule must be a mapping, got {type(raw).__name__}")
        rule_id = raw.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            raise LexiconError("every rule needs a non-empty string 'id'")
        rule_cs = bool(raw.get("case_sensitive", case_sensitive))
        regex = _compile(raw.get("pattern"), case_sensitive=rule_cs, what=f"rule {rule_id!r}")
        compiled.append(
            Rule(
                rule_id=rule_id,
                regex=regex,
                hint=str(raw.get("hint", "")),
                suggest=str(raw.get("suggest", "")),
            )
        )
    suppress_re = (
        _compile(suppress, case_sensitive=case_sensitive, what="suppress")
        if suppress is not None
        else None
    )
    return Lexicon(rules=tuple(compiled), suppress=suppress_re)


def scan_text(text: str, lexicon: Lexicon, *, label: str = "") -> LexiconReport:
    """Scan `text` line by line against `lexicon`, returning a `LexiconReport`.

    Every rule is applied to every line; a line matching the lexicon's `suppress` pattern is skipped
    (the inline allowlist). Each match yields a `Finding` with a 1-based line/column and the
    `label` (a path or name for the text). Findings arrive in location order (line, then column).
    Pure: no I/O, no filesystem, no clock - the caller supplies the text and names it."""
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if lexicon.suppress is not None and lexicon.suppress.search(line):
            continue
        line_hits: list[Finding] = []
        for rule in lexicon.rules:
            for match in rule.regex.finditer(line):
                line_hits.append(
                    Finding(
                        label=label,
                        line=lineno,
                        column=match.start() + 1,
                        rule_id=rule.rule_id,
                        matched=match.group(0),
                        suggest=rule.suggest,
                        hint=rule.hint,
                    )
                )
        line_hits.sort(key=lambda f: f.column)  # stable location order within a line
        findings.extend(line_hits)
    return LexiconReport(findings=tuple(findings))
