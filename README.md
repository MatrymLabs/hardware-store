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
registry.json     machine-readable index; store_check proves it mirrors catalog/
intake/           submission staging: candidates awaiting an R&D verdict
tools/            store_search (find + log), store_check (the gate), consume (record adoption)
docs/             CARD_SCHEMA.md, CARD_TEMPLATE.md
tests/            proof the tooling works, incl. sabotage tests for every check
```

## Run it

```bash
make env          # create .venv, install dev tools (pytest, ruff, mypy)
make check        # lint + typecheck + test + store-check (the full gate)
make store-check  # just the integrity gate over the Store
make search q="rate limiting"
```

Zero runtime dependencies by design: cards are TOML (stdlib `tomllib`), the index is
JSON (stdlib `json`). Built with AI assistance under human direction; cards record
their own provenance.

## Status

Phase 1 complete: the Store core and its three tools exist and are proven on a
fixture (green fixture passes; sabotaged copies fail on the exact broken check). The
catalog is intentionally empty; real Parts arrive in Phase 3 as CANDIDATEs and are
certified by R&D.
