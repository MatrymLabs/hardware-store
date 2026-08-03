"""Test twin for lexicon_gate (EXP-34) -- acceptance AND refusal/hostile cases.

Acceptance: a policy finds prohibited terms with correct line/column/rule/suggest; multiple hits per
line arrive in column order; case-insensitivity is the default and a per-rule override works; a
suppress pattern exempts a line; clean text reports clean; findings serialize to dicts. Refusal/
hostile: an empty rule list, a non-mapping rule, a missing id/pattern, and an invalid regex all fail
loud; a regex-special banned term is matched literally when escaped; unicode text is handled.
"""

from __future__ import annotations

import pytest
from lexicon_gate import Finding, LexiconError, LexiconReport, build_lexicon, scan_text

RULES = [
    {
        "id": "no-master",
        "pattern": r"\bmaster\b",
        "suggest": "main",
        "hint": "deprecated branch term",
    },
    {"id": "no-blacklist", "pattern": r"\bblacklist\b", "suggest": "blocklist"},
]


# --- acceptance -----------------------------------------------------------------------------------


def test_a_prohibited_term_is_found_with_full_location_and_fix() -> None:
    lex = build_lexicon(RULES)
    report = scan_text("push to master now", lex, label="README.md")
    assert isinstance(report, LexiconReport) and report.clean is False
    (f,) = report.findings
    assert isinstance(f, Finding)
    assert f.label == "README.md" and f.line == 1 and f.column == 9
    assert f.rule_id == "no-master" and f.matched == "master" and f.suggest == "main"
    assert f.hint == "deprecated branch term"


def test_clean_text_reports_clean() -> None:
    report = scan_text("push to main now", build_lexicon(RULES))
    assert report.clean is True and report.findings == ()
    assert "CLEAN" in report.summary()


def test_a_dirty_report_summary_counts_the_findings() -> None:
    report = scan_text("master and blacklist", build_lexicon(RULES))
    assert report.summary() == "lexicon: 2 prohibited term(s) found"


def test_multiple_hits_on_one_line_arrive_in_column_order() -> None:
    report = scan_text("blacklist the master branch", build_lexicon(RULES))
    cols = [(f.column, f.rule_id) for f in report.findings]
    assert cols == [
        (1, "no-blacklist"),
        (15, "no-master"),
    ]  # sorted by column within the line


def test_line_numbers_are_one_based_across_lines() -> None:
    report = scan_text("clean line\nthen master here", build_lexicon(RULES))
    (f,) = report.findings
    assert f.line == 2 and f.column == 6


def test_case_insensitive_is_the_default() -> None:
    report = scan_text("MASTER and Blacklist", build_lexicon(RULES))
    assert {f.rule_id for f in report.findings} == {"no-master", "no-blacklist"}


def test_a_per_rule_case_sensitive_override_is_honored() -> None:
    rules = [{"id": "cs", "pattern": r"Foo", "case_sensitive": True}]
    lex = build_lexicon(rules)
    assert scan_text("Foo", lex).clean is False
    assert scan_text("foo", lex).clean is True  # lowercase does not match a case-sensitive rule


def test_a_policy_wide_case_sensitive_flag_applies_to_rules_without_their_own() -> None:
    lex = build_lexicon([{"id": "cs", "pattern": r"Foo"}], case_sensitive=True)
    assert scan_text("foo", lex).clean is True and scan_text("Foo", lex).clean is False


def test_a_suppress_pattern_exempts_a_line() -> None:
    lex = build_lexicon(RULES, suppress=r"lexicon: allow")
    text = "master here is banned\nmaster here is fine  # lexicon: allow"
    report = scan_text(text, lex)
    lines = [f.line for f in report.findings]
    assert lines == [1]  # line 2 is suppressed inline, so its 'master' is exempt


def test_findings_serialize_to_dicts() -> None:
    (f,) = scan_text("master", build_lexicon(RULES)).findings
    d = f.as_dict()
    assert d["rule"] == "no-master" and d["matched"] == "master" and d["suggest"] == "main"


def test_a_regex_special_term_matches_literally_when_escaped() -> None:
    import re

    lex = build_lexicon([{"id": "dollar", "pattern": re.escape("$scope")}])
    assert scan_text("the $scope var", lex).findings[0].matched == "$scope"


def test_unicode_text_is_scanned_without_error() -> None:
    lex = build_lexicon([{"id": "cafe", "pattern": r"café"}])
    report = scan_text("visit the café today", lex)
    assert report.clean is False and report.findings[0].matched == "café"


# --- refusal / hostile ----------------------------------------------------------------------------


def test_an_empty_rule_list_fails_loud() -> None:
    with pytest.raises(LexiconError, match="at least one rule"):
        build_lexicon([])


@pytest.mark.parametrize(
    "bad_rules, match",
    [
        ([{"pattern": r"x"}], "non-empty string 'id'"),
        ([{"id": "", "pattern": r"x"}], "non-empty string 'id'"),
        ([{"id": "no-pat"}], "non-empty string pattern"),
        ([{"id": "empty", "pattern": ""}], "non-empty string pattern"),
        ([{"id": "bad", "pattern": r"("}], "invalid regex"),
        (["not-a-mapping"], "must be a mapping"),
    ],
)
def test_a_malformed_rule_fails_loud(bad_rules, match) -> None:
    with pytest.raises(LexiconError, match=match):
        build_lexicon(bad_rules)


def test_an_invalid_suppress_regex_fails_loud() -> None:
    with pytest.raises(LexiconError, match="suppress has an invalid regex"):
        build_lexicon(RULES, suppress=r"(")


def test_a_rule_id_that_is_not_a_string_fails_loud() -> None:
    with pytest.raises(LexiconError, match="non-empty string 'id'"):
        build_lexicon([{"id": 123, "pattern": r"x"}])
