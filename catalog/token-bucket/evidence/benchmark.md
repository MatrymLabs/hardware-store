# token_bucket evidence

Status: certification gate passed 2026-08-04.

- Source: `impl/python/token_bucket.py`.
- Tests: `tests/test_contract.py`.
- Fleet reuse finding: codeforge, codeforge-client, federal-guidance-library, and saas-starter all
  carry token-bucket rate limiting variants.
- Contract tests: 24 passed.
- Mutation: `mutmut` 3.7.0 over a temp flat copy of `impl/python/token_bucket.py` imported as
  `token_bucket`: 24 mutants, 24 killed, 0 survived = 100% kill rate.
- Benchmark (Python 3.13): `consume()` ~2.56 us/call; `reserve()` ~0.82 us/call.
- Tool note: the temp flat copy keeps `mutmut`'s mutant keys aligned with the canonical import name;
  the file contents are byte-for-byte the Store implementation.
