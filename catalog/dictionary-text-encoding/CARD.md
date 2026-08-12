+++
part_id = "PRT-0016"
canonical_name = "dictionary-text-encoding"
capability = "Store repeated dialogue phrases as dictionary tokens and expand them during rendering, trading a compact data stream for a controlled decode path and editable phrase vocabulary."
category = "Data"
maturity = "STUDIED"
failure_modes = ["token tables disagree between encoder and decoder", "a phrase expansion exceeds the destination buffer", "not yet characterised: localization effects on dictionary ratio"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0120)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
