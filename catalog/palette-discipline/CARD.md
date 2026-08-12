+++
part_id = "PRT-0013"
canonical_name = "palette-discipline"
capability = "Treat fifteen visible colours plus transparent as a hard palette budget, assigning roles deliberately so art variation fits the target display and transparency remains unambiguous."
category = "Game"
maturity = "STUDIED"
failure_modes = ["an asset exceeds the palette and silently quantizes", "transparent is reused as visible colour", "not yet characterised: perceptual loss from quantization"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0117)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
