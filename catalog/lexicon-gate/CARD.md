+++
part_id = "PRT-0002"
canonical_name = "lexicon_gate"
capability = "Find prohibited vocabulary in any text against a compiled term policy, reporting each offending line:column with a fix - a pure, reusable prose-governance gate (a sibling of a CI-YAML linter, for words not structure)."
category = "Validation"
maturity = "CERTIFIED"
contract = "contract/lexicon_gate.py"
inputs = "a list of rule mappings (id/pattern/hint/suggest/case_sensitive), an optional suppress pattern; a text to scan + a label"
outputs = "a Lexicon (compiled policy); a LexiconReport (.clean + located Findings + .summary())"
permissions = "none (pure; no I/O, no filesystem, no auth surface)"
security = "no I/O to exploit; fail-loud on a malformed policy stops a silently-empty gate from passing every text; regexes are caller-supplied and compiled once (a bad regex fails at build time, not per line)"
accessibility = "n/a (library primitive)"
performance = "a 10,000-line scan is ~60-110 ms; scales with rules x lines; NEUTRAL"
failure_modes = [
  "LexiconError on an empty rule list (a silently-empty policy passes every text - the opposite of a gate)",
  "LexiconError on a non-mapping rule or a missing/blank id or pattern",
  "LexiconError on an invalid rule or suppress regex",
]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 88
mutation_tool = "mutmut"

[provenance]
origin = "clean-room generalization of scripts/check_nomenclature.py (RD-2026-0004 FH-09 / EXP-34-lexicon-gate); source read to capture the mechanism, NO code copied"
ai_generated = "implementation and tests are AI-assisted (Claude), human-reviewed and gated"
verified_by = "21 contract tests (100% coverage), mypy --strict, ruff, mutmut (88% kill rate); consumer check_nomenclature 21-test twin unchanged"

[rd_certification]
rd_id = "RD-2026-0004"
verdict = "HARDWARE_STORE_PART"

[[implementations]]
language = "python"
path = "impl/python/lexicon_gate.py"
version = "0.1.0"
benchmark = "10k-line scan ~60-110 ms"

[[current_consumers]]
repo = "ship"
path = "scripts/check_nomenclature.py"
version = "0.1.0"
adopted = "2026-08-03"
+++

# lexicon_gate (CARD)

A **prose-governance term-policy gate**: compile a policy of prohibited-term patterns, scan any text,
and get a **report** of every offending line:column with a fix suggestion and an optional inline
`suppress` pragma. Pure and decoupled - it does NOT read a YAML file, walk a filesystem, or own a CLI
(those are the consumer's concern); it only compiles a policy and scans text.

- **Contract:** `contract/lexicon_gate.py`. **Implementation:** `impl/python/lexicon_gate.py`.
- **Tests:** `tests/test_contract.py` - 21 cases, 100% coverage, 88% mutation kill rate.
- **Consumer:** the ship nomenclature guard (`scripts/check_nomenclature.py`) refactored onto it,
  its duplicated compile+scan core removed.

Maturity: **CERTIFIED** (RD-2026-0004 HARDWARE_STORE_PART; one real consumer; mutation >= threshold).
