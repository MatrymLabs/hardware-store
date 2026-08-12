+++
part_id = "PRT-0012"
canonical_name = "constrained-map-streaming"
capability = "Stream connected map regions through a bounded RAM window, loading the next region before traversal requires it and evicting safe regions without breaking connections."
category = "Pattern"
maturity = "STUDIED"
failure_modes = ["a transition requests an evicted region", "loading stalls the frame budget", "not yet characterised: minimum lookahead for arbitrary connections"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0116)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
