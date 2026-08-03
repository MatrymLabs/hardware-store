# The Hardware Store Loop (per-stream integration)

Every consuming stream (today: **codeforge**, **ai-log-triage**,
**federal-guidance-library**) runs the same loop. This is the canonical text a
stream adopts; there is no separate `STREAM.md` to keep in sync, only these
commands.

> Note: the original task named per-repo `STREAM.md` files. None exist in the fleet,
> so the loop lives here as one canonical, command-first document each stream links,
> rather than three drifting copies.

## The loop

```
SEARCH   store-search "<capability>" --repo <repo> --log-file .hardware-store/search_log.jsonl
         (commit the log; this is "prove you looked")
CONSUME  depend on the Part at a pinned version; import it
RECORD   store-consume <slug> --repo <repo> --path <file> --version <v>
BUILD    only build new when the search returns nothing, or write a DECISION: why not
GATE     the consume-first CI job fails a PR that rebuilds a catalogued capability
         without a logged search or a DECISION: override
```

## Wire the CI gate (one file per stream)

Copy `ci/consume-first.yml` from this repo into the stream's
`.github/workflows/consume-first.yml`. It:

1. installs the Hardware Store (`pip install matrym-hardware-store @ git+...@main`),
2. reads the Store's `registry.json` and the repo-local `.hardware-store/search_log.jsonl`,
3. computes the PR's changed `*.py` files, and
4. runs `store-consume-first`, failing the build on an unresolved reimplementation.

Passing and failing runs are demonstrated in the Phase 2 PR of this repo.

## Per-stream first adoption (the duplication these repos already carry)

Phase 0 found retry, circuit-breaker, and hash-chain reimplemented in
**ai-log-triage** and **federal-guidance-library** instead of consumed. Phase 4 walks
the resilience pair (retry + circuit-breaker) through the full loop end to end and
replaces those local copies with the certified Part. Until then, each stream adds the
CI gate above so no *new* duplication lands silently.

## Applying this to the three repos

Wiring `consume-first.yml` into codeforge, ai-log-triage, and FGL touches three repos
(two private), each needing its own branch, PR, and green CI. That cross-repo rollout
is a founder-ratified step; this document plus `ci/consume-first.yml` is the ready
artifact it applies.
