+++
part_id = "PRT-0003"
canonical_name = "source_monitor"
capability = "Classify what changed at a watched source (URL, config, dependency, doc, API) against its last snapshot - first_capture/unchanged/content_changed/broken_link - via an injected fetch seam, returning the new snapshot without persisting it (a source drift detector)."
category = "Operations"
maturity = "CERTIFIED"
contract = "contract/source_monitor.py"
inputs = "a source_id + locator, an injected fetch(locator)->bytes seam, the previous Snapshot|None, a now label"
outputs = "a Change (kind, new Snapshot|None, previous, action, detail); a Snapshot; a report line"
permissions = "none in the Part (the caller's fetch seam owns any network/auth)"
security = "the Part does no I/O of its own; the injected fetch is the only external reach and any failure is caught + classified, never propagated; detection is decoupled from mutation, so the monitor can never corrupt the source of truth"
accessibility = "n/a (library primitive)"
performance = "cost is sha256 hashing (scales with content size); classify + verdict negligible; the network fetch is the caller's; NEUTRAL"
failure_modes = [
  "a fetch failure (timeout, 4xx/5xx, SSL, DNS) is classified BROKEN_LINK with the error captured - never a crash",
  "MonitorError on an empty source_id",
  "MonitorError on a previous snapshot for a different source (comparing the wrong baselines would mis-classify)",
]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 89
mutation_tool = "mutmut"

[provenance]
origin = "clean-room generalization of federal-guidance-library fgl/diff.py + fetch.py (RD-2026-0004 FH-03 / EXP-35-change-monitor); NO code copied"
ai_generated = "implementation and tests are AI-assisted (Claude), human-reviewed and gated"
verified_by = "11 contract tests (100% coverage), mypy --strict, ruff, mutmut (89% kill rate); FGL make check green after the consumer refactor"

[rd_certification]
rd_id = "RD-2026-0004"
verdict = "HARDWARE_STORE_PART"

[[implementations]]
language = "python"
path = "impl/python/source_monitor.py"
version = "0.1.0"
benchmark = "check ~10 us at 1 KB, ~1.3 ms at 1 MB (sha256-bound)"

[[current_consumers]]
repo = "federal-guidance-library"
path = "federal-guidance-library/src/fgl/diff.py"
version = "0.1.0"
adopted = "2026-08-03"
+++

# source_monitor (CARD)

A **source drift detector**. Fetch a watched source via an injected seam, hash it, compare to the
last snapshot, and classify the change - `first_capture` / `unchanged` / `content_changed` /
`broken_link` - with an operator action. Two reusable properties: a dead link is a **classified
value**, not a crash; and **detection is decoupled from mutation** (it returns the new snapshot; the
caller persists it after review, so the source of truth stays human-owned). The network is a seam,
so tests are offline.

- **Contract:** `contract/source_monitor.py`. **Implementation:** `impl/python/source_monitor.py`.
- **Tests:** `tests/test_contract.py` - 11 cases, 100% coverage, 89% mutation kill rate.
- **Consumer:** FGL `src/fgl/diff.py` consumes the classifier + ChangeKind (its duplicate removed) -
  closing the harvest-then-reuse loop, since the Part was extracted from that very module.

Maturity: **CERTIFIED** (RD-2026-0004 HARDWARE_STORE_PART; one real consumer; mutation >= threshold).
