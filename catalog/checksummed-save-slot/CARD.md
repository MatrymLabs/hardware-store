+++
part_id = "PRT-0015"
canonical_name = "checksummed-save-slot"
capability = "Validate a save slot with a checksum and treat any mismatch as an empty slot, ensuring corruption never presents as a playable character and the failure policy is deterministic."
category = "Data"
maturity = "STUDIED"
failure_modes = ["checksum covers different bytes on read and write", "corruption is mistaken for a valid empty save", "not yet characterised: recovery or backup policy"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0119)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
