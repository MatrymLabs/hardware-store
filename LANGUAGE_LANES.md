# Hardware Store Language Lanes

Canon: `MATRYM_WORKSHOP_CANON.md` section 16. Machine-readable record: `LANGUAGE_LANES.yaml`.
Instrument: `make language-lanes` (`scripts/language_lane_gate.py`).

Matrym Labs is an omni-coding Workshop. The Hardware Store is the reusable capability system for
all of it, and it must not become a single-language shelf. This record makes every language the
Workshop actually uses visible, because invisible language use becomes drift.

## What a lane is, and what it is not

A lane is a language the Workshop **uses**. Canon section 21 names 33 Rider language and framework
lanes; an IDE supporting a language is capability, not use. A register that lists aspiration cannot
detect drift, because everything is always already on it.

So the lane list is **derived from the census**, never hand-copied. `scripts/language_census.py`
counts every distinct repository, and `make language-lanes` refuses two things:

- a language present in the tree with no lane here
- a lane claiming `governed` that the census measures as only partially inspected

The second is the load-bearing one. A record that may claim more than was measured is not a record,
it is a preference, and the defect this Workshop keeps rediscovering is a verdict reported over a
property nobody measured.

## Statuses

| status | meaning |
|---|---|
| `governed` | every repository holding this language inspects it |
| `partial` | at least one repository holds it and does not inspect it. A gap, named |
| `ungoverned` | present in the tree with no instrument at all |
| `deferred` | no code yet; the toolchain arrives with the rung that needs it |

`deferred` is honest and `ungoverned` is a Known Fault carried in the open. Neither is hidden.

## What the register currently says

Two lanes are `ungoverned`, C and protobuf, and both were invisible before this record existed:
the prior doctrine table named six languages, measured inside one repository, while the tree held
eight. Naming them does not fix them. It makes them fixable.

## Adding a lane

1. Write the code. A lane follows a consumer; it never precedes one.
2. Run `make languages`. If the census sees it, `make language-lanes` is already red.
3. Add the lane with its honest status. Do not claim `governed` before an instrument runs.
4. Where the language consumes a Hardware Store Part, add its lane to
   `OMNI_CODE_PART_MATRIX.yaml`.

## Execution-environment ruling - 2026-08-20

A lane is an execution environment, not a language. A language name alone is not a Gate: the
programs that parse, migrate, diff, apply DDL, and explain SQL differ by engine.

The measured correction is:

| record | before | after | reason |
|---|---:|---:|---|
| lane count | 1 PROVEN / 6 GATED | 1 PROVEN / 7 GATED | SQL was one language label covering two execution environments |

The SQL lanes are distinct and both GATED, neither PROVEN:

- `sql-sqlite` - SQLite through the SQLAlchemy path; its Gate is separate from PostgreSQL.
- `sql-postgres` - the PostgreSQL CI execution environment; its Gate is separate from SQLite.
- `sql-sqlserver` is intentionally absent. There is no SQL Server code in the measured tree, and
the toolchain arrives with the rung that needs it. Declaring it from a research table would be a
claim without code or a failing Gate.

The measured C/C++ label is corrected to `c`: the tree contains one `.c` file and zero `.cpp`
files. The JVM lane remains one environment: nine `.kt` and two `.kts` files, zero `.java`. The
TypeScript lane is not re-statused here; its separate measurement is required before a ruling.

The gate must refuse a declared lane with no corresponding code or execution evidence, and it must
refuse a PROVEN claim without a shipped Target Product. A passing record names `sql-sqlite` and
`sql-postgres` separately.