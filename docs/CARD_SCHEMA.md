# The Hardware Card schema

A card is the `+++`-fenced TOML front-matter at the top of `catalog/<slug>/CARD.md`.
TOML because it parses with stdlib `tomllib` (no third-party YAML dependency); the
Markdown body below the front-matter is for humans. `registry.json` is the aggregated
index built from every card, and `store_check` proves the two agree exactly.

## Fields

| field | type | when required | meaning |
|---|---|---|---|
| `part_id` | string | always | permanent, unique identity (e.g. `PRT-0001`) |
| `canonical_name` | string | always | the stable snake_case name used in code/imports |
| `capability` | string | always | the **language-agnostic** capability statement (the index) |
| `category` | string | always | one of the capability categories below |
| `maturity` | string | always | `CANDIDATE` / `CERTIFIED` / `FLEET_CORE` / `DEPRECATED` |
| `contract` | string | always | path to the interface every implementation honors |
| `inputs` / `outputs` | string | recommended | the data in and out |
| `permissions` | string | recommended | what capability/authority it needs |
| `security` | string | recommended | security posture, secrets handling |
| `accessibility` | string | recommended | a11y notes (or `n/a` for a library primitive) |
| `performance` | string | recommended | complexity / benchmark summary |
| `failure_modes` | array | always | how it fails, observably |
| `[tests]` | table | always | `suite`, `mutation_score` (int %), `mutation_tool` |
| `[provenance]` | table | always | `origin`, `ai_generated`, `verified_by` |
| `[rd_certification]` | table | **CERTIFIED+** | `rd_id` (RD-####) + `verdict` (HARDWARE_STORE_PART) |
| `[[implementations]]` | array of tables | always (>=1) | `language`, `path`, `version`, `benchmark` |
| `[[current_consumers]]` | array of tables | **CERTIFIED+** (>=1) | `repo`, `path`, `version`, `adopted` |
| `migration` | string | on DEPRECATED | how to move off it |
| `deprecation_path` | string | on DEPRECATED | successor Part / timeline |

## Capability categories

`Domain`, `Application`, `Interface`, `Data`, `Client`, `Integration`, `AI`,
`Operations`, `Security`, `Accessibility`, `Validation`, `Generator`, `Development`,
`Game`, `Simulation`, `Pattern`.

## What `store_check` enforces

- Every card parses and carries the always-required fields with valid `category`/`maturity`.
- `registry.json` exactly mirrors `catalog/` (no ghost entries, no unlisted cards).
- Every `[[implementations]]` path exists on disk.
- Every Part has a `tests/` contract suite, and it passes (CMD: pytest).
- `CERTIFIED`/`FLEET_CORE` require: an `[rd_certification]` record, a non-empty
  `current_consumers`, and `tests.mutation_score >=` the fleet threshold (default 70).
- Every listed consumer path exists under the fleet root and actually imports the Part.
- No retired fleet vocabulary anywhere in the Store.
