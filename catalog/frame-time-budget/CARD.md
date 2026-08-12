+++
part_id = "PRT-0018"
canonical_name = "frame-time-budget"
capability = "Give each frame a fixed execution budget and schedule work so rendering, input, streaming, and simulation meet that budget instead of allowing one subsystem to monopolize a frame."
category = "Pattern"
maturity = "STUDIED"
failure_modes = ["work overruns and causes visible frame drops", "deferred work grows without a bound", "not yet characterised: budget allocation under variable load"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0122)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
