+++
part_id = "PRT-0010"
canonical_name = "layer-composition"
capability = "Resolve visible pixels from ordered tile layers by priority, transparency, and occlusion, keeping background, foreground, and effect composition deterministic."
category = "Pattern"
maturity = "STUDIED"
failure_modes = ["incorrect priority hides gameplay-critical tiles", "transparent pixels are treated as opaque", "not yet characterised: worst-case layer traversal cost"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0112)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
