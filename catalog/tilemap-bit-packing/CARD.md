+++
part_id = "PRT-0009"
canonical_name = "tilemap-bit-packing"
capability = "Pack tile index, palette selection, priority, and horizontal or vertical flip into one fixed-width map word, making tilemap storage compact and decoding deterministic."
category = "Data"
maturity = "STUDIED"
failure_modes = ["field masks overlap and corrupt neighboring flags", "endianness is assumed instead of declared", "not yet characterised: malformed-word recovery"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0111)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
