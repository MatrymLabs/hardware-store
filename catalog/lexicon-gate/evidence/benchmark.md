# lexicon_gate - evidence

## Isolation proof (EXP-34-lexicon-gate, RD-2026-0004 FH-09)
- 21 contract tests (acceptance + refusal/hostile: empty rules, non-mapping rule, missing id/pattern,
  invalid regex, non-string id, invalid suppress; column-order, case, suppression, unicode, regex
  escape); 100% coverage; mypy --strict + ruff clean.

## Mutation testing
- tool: mutmut 3.7.0 ; 125 mutants, 111 killed, 14 survived -> 88% kill rate (>= 70%).

## Benchmark
- a 10,000-line scan is ~60-110 ms (scales with rules x lines); a real PR diff is far smaller, so
  gating is imperceptible. Honest label: NEUTRAL.

## Real consumer
- scripts/check_nomenclature.py (the fleet nomenclature guard) consumes build_lexicon + scan_text;
  its own Rule/_compile_rule/scan-loop were removed. Its 21-test twin passes unchanged.
