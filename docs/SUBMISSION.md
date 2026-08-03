# Submission pipeline (in): candidate -> R&D -> catalog

A capability enters the Store one way only. No stream self-certifies; R&D's Factory
verdict is the sole gate.

## The steps (commands, not prose)

1. **Stage a candidate** in `intake/<capability-slug>/`, shaped exactly like a catalog
   entry (see `docs/CARD_SCHEMA.md`, start from `docs/CARD_TEMPLATE.md`):

   ```
   intake/<slug>/
     CARD.md        maturity = "CANDIDATE", [rd_certification] empty
     contract/      the interface every implementation honors
     impl/<lang>/   a working implementation
     tests/         contract conformance tests
     evidence/      a benchmark and any measurements
   ```

   A candidate is `implementation + draft card + contract tests + benchmark`. Anything
   less is not ready for the Factory.

2. **Hand it to the R&D Factory (Stream 3).** The Factory runs its pipeline
   (`rd/FACTORY.md`: intake -> claims -> experiment -> evidence -> verdict -> packet)
   and records the candidate in `rd/05-packets/HARDWARE_CANDIDATES.yaml`, gated by
   Proof-Before-Promotion (`rd/CHARTER.md`). The handoff note lives in
   `rd/05-packets/handoffs/`. R&D's decision is the verdict `HARDWARE_STORE_PART`
   with an `RD-####` id (one of the sixteen Factory verdicts in `rd/FACTORY.md`).

3. **On a HARDWARE_STORE_PART verdict**, R&D fills the card's `[rd_certification]`
   table (`rd_id`, `verdict = "HARDWARE_STORE_PART"`) and sets `maturity = "CERTIFIED"`.

4. **Promote it** into the catalog:

   ```bash
   store-promote <slug> --when $(date +%F)
   ```

   `store-promote` **refuses** unless the card carries a real `[rd_certification]`
   record with the `HARDWARE_STORE_PART` verdict (see the demo in this PR: it exits 1
   for a CANDIDATE, exits 0 for a certified card). The move is history-preserving
   (`git mv`) and leaves a pointer in `intake/PROMOTIONS.md`; it then rebuilds
   `registry.json`. Run `store-check` to confirm the Store is green.

## The enforcement

`store_check` fails any `catalog/` entry that reaches `CERTIFIED` without an
`[rd_certification]` record, without a real consumer, or with a mutation score below
the fleet threshold. So even a hand-moved directory cannot masquerade as certified.
The valve (`store-promote`) and the gate (`store-check`) enforce the same law from
both sides.
