# Matrym Labs Hardware Store

The fleet's certified catalog of reusable engineering capability. A Part is
catalogued by the *capability* it provides (not the technology it uses); it becomes
`CERTIFIED` only through the R&D Factory's `HARDWARE_STORE_PART` verdict; and it may
carry implementations in more than one language behind a single contract.

The full charter, laws, and lifecycle live in **[STORE.md](STORE.md)**. The card
contract is **[docs/CARD_SCHEMA.md](docs/CARD_SCHEMA.md)**.

## Layout

```
STORE.md          charter: the five laws, lifecycle, how to consume / submit
catalog/          the certified Parts (one dir per capability; empty until Phase 3)
registry.json     machine-readable index; store-check proves it mirrors catalog/
intake/           submission staging: candidates awaiting an R&D verdict
hardware_store/   the installable package: the store-* console verbs
docs/             CARD_SCHEMA, CARD_TEMPLATE, SUBMISSION, CONSUMPTION, STREAM_INTEGRATION
ci/               consume-first.yml, the drop-in gate each stream repo adds
tests/            proof the tooling works, incl. sabotage tests for every check
```

## Verbs (installable console scripts)

| verb | what it does |
|---|---|
| `store-search` | search the catalog by capability; logs the query (prove you looked) |
| `store-check` | the integrity gate (the no-graveyard law) |
| `store-consume` | record a repo's adoption on a Part's card |
| `store-promote` | move an R&D-certified candidate from `intake/` to `catalog/` |
| `store-consume-first` | the stream-side CI gate against silent reimplementation |

## Run it

```bash
make env          # create .venv, install the package + dev tools
make check        # lint + typecheck + test + store-check (the full gate)
pip install -e .  # or install the package; the store-* verbs land on PATH
make search q="rate limiting"
```

Zero runtime dependencies by design: cards are TOML (stdlib `tomllib`), the index is
JSON (stdlib `json`). Built with AI assistance under human direction; cards record
their own provenance.

## Status

Phase 2 complete: the Store core and five console verbs exist and are proven. The
integrity gate passes a good fixture and fails a sabotaged copy on the exact broken
check; the submission pipeline (`store-promote`) refuses uncertified candidates and
promotes certified ones; the consume-first CI gate (`store-consume-first`) fails a
probable reimplementation unless a logged search or a `DECISION:` override resolves
it. The catalog is intentionally empty; real Parts arrive in Phase 3 as CANDIDATEs and
are certified by R&D (Phase 4 walks the retry + circuit-breaker pair through the full
loop and consolidates the ai-log-triage / FGL duplicates).

## License

MIT (see `LICENSE`), matching the rest of the Matrym Labs fleet.

Every Part in `catalog/` records its own `[provenance]` block, and all five declare **clean-room
reconstruction with no code copied** from the systems that inspired them. The MIT grant therefore
covers original work and contradicts no upstream licence. A Part whose provenance ever cited copied
code would need its own notice before it could ship under this grant.
