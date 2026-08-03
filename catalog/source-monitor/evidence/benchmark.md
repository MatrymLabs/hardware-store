# source_monitor - evidence

## Isolation proof (EXP-35-change-monitor, RD-2026-0004 FH-03)
- 11 contract tests (all four change kinds; a no-persist proof; fail-loud on empty id + wrong-source
  previous; fetch faked so tests are offline); 100% coverage; mypy --strict + ruff clean.

## Mutation testing
- tool: mutmut 3.7.0 ; 56 mutants, 50 killed, 6 survived -> 89% kill rate (>= 70%).

## Benchmark
- cost is sha256 hashing (scales with content size: ~10 us at 1 KB, ~1.3 ms at 1 MB); the classify +
  verdict logic is negligible; the real cost is the caller's network fetch (mocked here). NEUTRAL.

## Real consumer
- federal-guidance-library/src/fgl/diff.py consumes ChangeKind + classify (its duplicate enum +
  classifier removed); closes the harvest-then-reuse loop (the Part was extracted from fgl/diff.py).
