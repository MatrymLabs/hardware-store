+++
part_id = "PRT-0006"
canonical_name = "token_bucket"
capability = "Rate-limit work with a token bucket: allow bursts up to capacity, refill at a sustained rate, and expose both consumer shapes already present in the fleet - deny/return retry_after and pace/return wait seconds."
category = "Operations"
maturity = "CERTIFIED"
contract = "contract/token_bucket.py"
inputs = "a finite capacity, a finite non-negative refill rate, an optional injected monotonic clock, and a finite cost per action"
outputs = "ThrottleDecision(allowed, tokens_left, retry_after, reason) for check/consume; wait seconds for reserve/take; bool/int retry-after tuple for per-tenant limiting"
permissions = "none (pure in-memory state; caller injects the clock and performs any sleep or I/O)"
security = "no I/O of its own; fail-loud validation prevents impossible buckets, non-finite costs, and pacing with no refill when a wait would be required"
accessibility = "n/a (library primitive)"
performance = "consume() ~2.56 us/call; reserve() ~0.82 us/call; O(1) per check/consume/reserve"
failure_modes = [
  "RateLimitError at construction on non-finite, bool, negative rate, or non-positive capacity",
  "RateLimitError when cost is non-finite, bool, negative, or exceeds capacity for a deny-style consume/check",
  "consume/check with rate == 0 can deny forever and reports retry_after = infinity",
  "reserve/take raises RateLimitError if rate == 0 and the requested tokens are not currently available",
]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 100
mutation_tool = "mutmut"

[provenance]
origin = "clean-room consolidation of the standard token-bucket pattern. Fleet evidence found the same capability in codeforge kernel/shelf, codeforge-client command throttling, federal-guidance-library fetch pacing, and saas-starter tenant rate limiting; this Part unifies those consumer shapes."
ai_generated = "implementation and tests are AI-assisted, human-reviewed and gated"
verified_by = "24 contract tests; mutmut 3.7.0 killed 24/24 mutants (100%) over the flat canonical module copy; benchmarked consume() ~2.56 us/call and reserve() ~0.82 us/call"

[rd_certification]
rd_id = "RD-2026-0011"
verdict = "HARDWARE_STORE_PART"

[[implementations]]
language = "python"
path = "impl/python/token_bucket.py"
version = "0.1.0"
benchmark = "consume() ~2.56 us/call; reserve() ~0.82 us/call"

[[current_consumers]]
repo = "codeforge"
path = "codeforge/kernel/shelf/token_bucket.py"
version = "0.1.0"
adopted = "2026-08-04"

[[current_consumers]]
repo = "codeforge-client"
path = "codeforge-client/src/codeforge/mudclient/core/throttle.py"
version = "0.1.0"
adopted = "2026-08-04"

[[current_consumers]]
repo = "federal-guidance-library"
path = "federal-guidance-library/src/fgl/ratelimit.py"
version = "0.1.0"
adopted = "2026-08-04"

[[current_consumers]]
repo = "saas-starter"
path = "saas-starter/app/ratelimit.py"
version = "0.1.0"
adopted = "2026-08-04"
+++

# token_bucket (CARD)

Rate-limit work with a **token bucket**. A bucket starts full, allows a burst up to `capacity`,
then refills at `rate` tokens per second. The Part exposes both shapes already present in the
fleet:

- `check` / `consume` return a `ThrottleDecision` with `allowed`, `tokens_left`, `retry_after`,
  and a reason. This is the "deny now, tell the caller when to retry" shape used by CodeForge.
- `reserve` / `take` return the wait seconds required before an action can proceed. This is the
  pacing shape used by fetchers and transports that should slow down instead of dropping work.
- `PerTenantRateLimiter` keeps one bucket per tenant key and returns `(allowed, retry_after_seconds)`.

The clock is injected, so tests drive refill behavior without sleeping. The Part is in-memory,
single-process, and stdlib only; distributed deployments map the same contract onto an atomic
shared store.

- **Contract:** `contract/token_bucket.py`.
- **Implementation:** `impl/python/token_bucket.py`.
- **Tests:** `tests/test_contract.py`.

Maturity: **CERTIFIED** (R&D verdict RD-2026-0011 HARDWARE_STORE_PART; four real consumers;
mutation >= threshold). The direct fleet audit found four independent token-bucket variants and
this Part publishes the common core with both deny-style and pacing-style surfaces.
