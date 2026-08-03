# The Matrym Labs Hardware Store

The fleet's certified catalog of reusable engineering capability. Every stream
consumes from it, every stream feeds into it (through R&D certification only), and
every future product is assembled from it. When CodeForge designs a game, a
classroom, or a course, it discovers Parts here first. The Store is multi-stack and
language-extensible by design.

This charter is enforced by tooling, not by memory. `hardware_store/store_check.py`
(the `store-check` verb) is the law; a red check is a fleet alarm, not a warning.

## The five laws (each is a mechanism, not a slogan)

1. **Capability over technology.** A Part is catalogued by the engineering
   *capability* it provides, not the technology it happens to use. The card's
   `capability` field is a language-agnostic statement ("bounded rate limiting with
   observable failure behavior"); the technology is a field on an *implementation*.
   Capability is the index; technology is a detail.
2. **R&D locks patterns in.** The Store has exactly one certification gate: Stream
   3's Factory verdict `HARDWARE_STORE_PART`. No stream self-certifies, R&D
   included. `store_check` fails any `catalog/` entry that reaches `CERTIFIED`
   without an `[rd_certification]` record.
3. **Consume first, and prove you looked.** Before a stream builds a capability it
   runs `store_search`, which logs the query to `intake/search_log.jsonl`.
   Reimplementing a catalogued capability without a documented reason is a
   CI-detectable defect (pipeline wiring: Phase 2).
4. **No graveyard.** A stable (`CERTIFIED`) Part requires: a real implementation +
   tests that bite (mutation-tested at/above the fleet threshold) + at least one
   genuine consumer + a stable contract + provenance. Cards without implementations,
   and implementations without cards, are both defects `store_check` surfaces.
5. **Language-extensible.** The card schema supports any implementation language; a
   capability may carry several implementations sharing one contract. Adding a
   language implementation goes through the same R&D gate with the same evidence bar
   (languages are admitted by evidence, never by fashion).

## The lifecycle

```
build a candidate      -> intake/<slug>/   (impl + draft CARD + contract tests + benchmark)
R&D issues a verdict    -> HARDWARE_STORE_PART + RD-#### (Stream 3 Factory; nobody else)
promote                 -> catalog/<slug>/  at maturity CERTIFIED, [rd_certification] recorded
a stream consumes it    -> consume.py appends the repo to current_consumers (pinned version)
store_check stays green  -> continuously, in CI and on a Fleet Ops heartbeat (Phase 4)
```

Maturity ladder: `CANDIDATE -> CERTIFIED -> FLEET_CORE -> DEPRECATED`. A CANDIDATE may
legally lack a certification, consumers, and a mutation score; those become mandatory
at CERTIFIED. FLEET_CORE (two products agreeing on one contract) needs founder
approval.

## How to consume a Part (full pipeline: `docs/CONSUMPTION.md`)

1. `store-search "<capability>" --repo <you> --log-file .hardware-store/search_log.jsonl`
   and commit the log. The query is recorded ("prove you looked"). If a Part matches,
   depend on it at a pinned version.
2. Record your adoption so the card tells the truth about who relies on it:
   `store-consume <slug> --repo <you> --path <path/that/imports/it> --version <v>`
3. Add the consume-first gate to your CI: copy `ci/consume-first.yml` (see
   `docs/STREAM_INTEGRATION.md`). It fails a PR that rebuilds a catalogued capability
   without a logged search or a `DECISION:` override.

## How to submit a Part (full pipeline: `docs/SUBMISSION.md`)

Stage `intake/<slug>/` as a full candidate (implementation + draft `CARD.md` +
`contract/` + `tests/` + a benchmark), then hand it to the R&D Factory. See
`docs/CARD_SCHEMA.md` for the card contract and `docs/CARD_TEMPLATE.md` to start one.
R&D's `HARDWARE_STORE_PART` verdict is the only thing that promotes it, via
`store-promote <slug>` (which refuses anything R&D has not certified).

## The card contract

Each Part is `catalog/<capability-slug>/` with:

```
CARD.md        +++-fenced TOML front-matter (the machine-readable card) + a human body
contract/      the interface every implementation must satisfy (types, schemas, protocols)
impl/<lang>/   one directory per certified language implementation
tests/         the contract conformance suite - runs against EVERY implementation
evidence/      the certification record: RD id, verdict, benchmark, mutation score
```

`registry.json` at the root is the machine-readable index (`store_check` proves it
exactly mirrors `catalog/`). Full field list: `docs/CARD_SCHEMA.md`.

## Provenance and honesty

This Store was stood up with AI assistance under human direction; cards record their
own provenance (including AI-generated portions and how each was verified). It uses
zero runtime dependencies on purpose (stdlib `tomllib` + `json`), consistent with the
fleet's stdlib-first law. Retired fleet vocabulary (see
`codeforge/docs/python/style_guide.md`) is banned Store-wide and `store_check`
enforces it.
