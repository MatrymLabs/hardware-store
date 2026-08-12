+++
part_id = "PRT-0017"
canonical_name = "bank-and-memory-map"
capability = "Assign data and code to explicit banks and memory regions, framing payloads so consumers can locate, load, and address them without hidden locality assumptions."
category = "Pattern"
maturity = "STUDIED"
failure_modes = ["a pointer crosses a bank boundary without a switch", "payload alignment wastes or overlaps memory", "not yet characterised: optimal packing strategy"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0121)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
