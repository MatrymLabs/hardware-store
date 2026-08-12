+++
part_id = "PRT-0011"
canonical_name = "compression-as-data-design"
capability = "Choose LZSS, run-length encoding, or dictionary compression as part of data modeling, balancing decode cost, repetition, and storage budget instead of treating compression as a final opaque step."
category = "Data"
maturity = "STUDIED"
failure_modes = ["decoder cannot represent the encoder's stream", "compression saves bytes but exceeds frame or startup budget", "not yet characterised: corpus-dependent ratio bounds"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0113)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
