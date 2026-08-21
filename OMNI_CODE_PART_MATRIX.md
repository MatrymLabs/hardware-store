# Omni-Code Part Matrix

Canon: `MATRYM_WORKSHOP_CANON.md` section 16. Machine-readable record:
`OMNI_CODE_PART_MATRIX.yaml`. Instrument: `make language-lanes`.

Every trusted Part is described first by its **invariant**, then its contract, inputs, outputs,
failure modes, and Proof Run. Implementation language is secondary. A Part is a promise about
behaviour; the language is how the promise is currently kept.

## The schema

Each Part carries `part_id`, `name`, `invariant`, `reference_language`, and one
`supported_language_lanes` entry per runtime that consumes it. Lane statuses are the canon's:

```text
not_started · candidate · reference · adapter · verified · consumer_proven · retired
not_applicable
```

A Part does not need every language on day one. It needs every language it is *actually used from*
to be visible, with an honest status and a Proof Run.

## Why this matrix is short, stated rather than implied

One Part is filed: `FH-09 lexicon_gate`, whose Python lane is `consumer_proven` because
`scripts/check_nomenclature.py` genuinely consumes it and `scripts/test_lexicon_gate.py` proves it
from inside this repository today.

The Certified Tier catalogue lives in the `hardware-store` repository, which is outside this Work
Order's allowlist; canon section 7 requires multi-repository work to be split or explicitly
approved. `complete: false` in the YAML says so in a field an instrument can read, rather than in
prose a reader can miss. Mirroring the rest of the catalogue is a follow-on Work Order in the
Store.

## Adding a language lane to a Part

A second-language lane follows a **second real consumer**, never a prediction. Canon section 15:
a capability with one consumer is a watch-list entry, not a Part. Port behaviour when the product
requires it, prove equivalence with shared fixtures, then register the lane here.
