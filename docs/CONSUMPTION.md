# Consumption pipeline (out): depend on a Part, and record it

A stream consumes a certified capability instead of rebuilding it. Two things make
that real: a pinned dependency, and a consumer record on the Part's card.

## Depend on the Store

The Store is an outward-facing dependency. A stream installs it (pinned):

```bash
pip install "matrym-hardware-store @ git+https://github.com/MatrymLabs/hardware-store@<tag>"
```

That puts the `store-*` verbs on PATH and vendors `registry.json` (the index a stream
queries). Individual Parts are consumed from `catalog/<slug>/impl/<lang>/` at a pinned
Part `version` from the card.

## The steps (commands, not prose)

1. **Search first, and record the look** (law #3). Write the query into your repo's
   own committed log:

   ```bash
   store-search "rate limiting" --repo <your-repo> \
       --log-file .hardware-store/search_log.jsonl
   git add .hardware-store/search_log.jsonl
   ```

2. **Depend on the Part** at a pinned version; import it from the catalog impl (or the
   Part's own published package where one exists, e.g. `matrym-hashchain`).

3. **Record your adoption** so the Part's card tells the truth about who relies on it:

   ```bash
   store-consume <slug> --repo <your-repo> \
       --path <path/in/your/repo/that/imports/it.py> --version <part-version>
   ```

   This appends a `[[current_consumers]]` row to `catalog/<slug>/CARD.md` and rebuilds
   `registry.json`. A CERTIFIED Part needs at least one such consumer, and `store_check`
   verifies each recorded consumer path actually imports the Part.

## The CI hook

Add the consume-first gate to your repo (see `docs/STREAM_INTEGRATION.md` and
`ci/consume-first.yml`). It fails a PR that reimplements a catalogued capability
without a logged `store_search` or a documented `DECISION:` override.
