# intake/ - submission staging

A candidate Part waits here until R&D issues a verdict. Nothing self-certifies.

- A **candidate** = a working implementation + a draft `CARD.md` + contract tests +
  a benchmark. Stage it as `intake/<capability-slug>/` (same shape as a `catalog/`
  entry) with `maturity = "CANDIDATE"`.
- The **only** thing that moves a candidate from `intake/` to `catalog/` at
  `CERTIFIED` is Stream 3's Factory verdict `HARDWARE_STORE_PART` and its `RD-####`
  id, recorded in the card's `[rd_certification]` table. `store_check` fails any
  `catalog/` entry that reaches CERTIFIED without one. (Pipeline wiring: Phase 2.)
- `search_log.jsonl` (generated, git-ignored) records every `store_search` query,
  so "we looked before we built" is a record, not a claim.
