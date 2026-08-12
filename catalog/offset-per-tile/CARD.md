+++
part_id = "PRT-0019"
canonical_name = "offset-per-tile"
capability = "Attach a small positional offset to each tile so one map representation can express effects such as shake, parallax, or irregular placement without rewriting the tile geometry."
category = "Pattern"
maturity = "STUDIED"
failure_modes = ["offsets accumulate across frames", "offset range causes clipping or overflow", "not yet characterised: interaction with collision coordinates"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0123)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
