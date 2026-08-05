+++
part_id = "PRT-0007"
canonical_name = "cache_aside"
capability = "Cache reads lazily with a TTL, explicit key invalidation, failed-load non-caching, and hit/miss stats so consumers can bound staleness and measure whether the cache is worthwhile."
category = "Data"
maturity = "CERTIFIED"
contract = "contract/cache_aside.py"
inputs = "a finite positive ttl_seconds, an optional injected monotonic clock, a cache key, and a zero-argument loader for misses or expired entries"
outputs = "the cached or freshly loaded value; bool from invalidate/is_cached; stats snapshot with hits, misses, hit_rate, and size"
permissions = "none (pure in-memory cache; caller owns the loader and any I/O it performs)"
security = "does not hide source failures: loader exceptions propagate and are never cached; non-finite/non-positive TTLs fail loud to avoid unbounded staleness"
accessibility = "n/a (library primitive)"
performance = "cache hit ~0.36 us/call; O(1) get/invalidate/clear"
failure_modes = [
  "CacheError at construction on non-finite, bool, or non-positive ttl_seconds",
  "a loader exception propagates and stores nothing, so the next read retries the source",
  "entries expire at the exact TTL boundary; stale data is not served at expires_at == now",
  "clear(reset_stats=False) evicts entries but preserves stats; reset_stats=True resets counters too",
]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 86
mutation_tool = "cosmic-ray"

[provenance]
origin = "clean-room consolidation of the public cache-aside/lazy-loading pattern. Fleet evidence found close variants in codeforge kernel/shelf/cache_aside.py and saas-starter/app/cache.py; this Part unifies the TTL, explicit invalidation, failed-load, and stats semantics."
ai_generated = "implementation and tests are AI-assisted, human-reviewed and gated"
verified_by = "15 contract tests; cosmic-ray 8.4.6 killed 102/118 mutants (86.44%) over the flat canonical module copy; benchmarked cache hit ~0.36 us/call"

[rd_certification]
rd_id = "RD-2026-0011"
verdict = "HARDWARE_STORE_PART"

[[implementations]]
language = "python"
path = "impl/python/cache_aside.py"
version = "0.1.0"
benchmark = "cache hit ~0.36 us/call"

[[current_consumers]]
repo = "codeforge"
path = "codeforge/kernel/shelf/cache_aside.py"
version = "0.1.0"
adopted = "2026-08-04"

[[current_consumers]]
repo = "saas-starter"
path = "saas-starter/app/cache.py"
version = "0.1.0"
adopted = "2026-08-04"
+++

# cache_aside (CARD)

Cache reads lazily with a TTL and explicit invalidation. On `get(key, loader)`, a fresh cache hit
returns without touching the source; a miss or expired entry calls `loader`, stores the returned
value with a new expiry, and returns it. If the loader raises, nothing is cached and the exception
propagates.

The Part also tracks hit/miss stats so consumers can measure whether the cache pays for itself.
`clear()` preserves stats by default to match CodeForge's long-lived measurement shape, while
`clear(reset_stats=True)` supports the SaaS starter's test/reset shape.

- **Contract:** `contract/cache_aside.py`.
- **Implementation:** `impl/python/cache_aside.py`.
- **Tests:** `tests/test_contract.py`.

Maturity: **CERTIFIED** (R&D verdict RD-2026-0011 HARDWARE_STORE_PART; two real consumers;
mutation >= threshold). The direct fleet audit found cache-aside in CodeForge and saas-starter,
and this Part publishes the shared TTL/invalidation/stats core.
