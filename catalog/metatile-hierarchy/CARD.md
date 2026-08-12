+++
part_id = "PRT-0008"
canonical_name = "metatile-hierarchy"
capability = "Compose small tiles into reusable 16x16 and 32x32 metatiles, so maps store repeated visual structure once while collision and decoration remain aligned."
category = "Pattern"
maturity = "STUDIED"
failure_modes = ["misaligned collision when composition dimensions differ", "duplicate edits when a shared metatile is copied", "not yet characterised: runtime cache pressure"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0110)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
