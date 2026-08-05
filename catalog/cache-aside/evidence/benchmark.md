# cache_aside evidence

Status: certification gate passed 2026-08-04.

- Source: `impl/python/cache_aside.py`.
- Tests: `tests/test_contract.py`.
- Fleet reuse finding: codeforge and saas-starter carry close cache-aside variants with TTL,
  explicit invalidation, failed-load non-caching, and hit/miss stats.
- Contract tests: 15 passed.
- Mutation: `cosmic-ray` 8.4.6 over a temp flat copy of `impl/python/cache_aside.py` imported as
  `cache_aside`: 118 mutants, 102 killed, 16 survived = 86.44% kill rate.
- Survivor notes: most survivors are low-value operator substitutions in arithmetic/bitwise mutant
  families around stats math; the semantic comparison and TTL boundary mutants are killed by the
  contract tests.
- Benchmark (Python 3.13): fresh cache hit ~0.36 us/call.
- Tool note: `mutmut` 3.7.0 could not map method-only `CacheAside` mutants to tests, matching the
  limitation documented for `circuit_breaker`; `cosmic-ray` is the Store's accepted alternate.
