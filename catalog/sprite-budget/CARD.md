+++
part_id = "PRT-0014"
canonical_name = "sprite-budget"
capability = "Manage sprite and OAM residency under fixed per-frame and VRAM budgets, prioritizing visible or gameplay-critical actors when demand exceeds capacity."
category = "Game"
maturity = "STUDIED"
failure_modes = ["sprite overflow causes missing actors", "VRAM updates tear or exceed the frame", "not yet characterised: fair eviction policy"]

[provenance]
source_studied = "INTAKE RUN 01 BODY 3, the ROM Hacking Research Lane Charter (RD-2026-0118)"
taint_class = "SAFE"
clean_room = "No proprietary source was read; no separation was required."
+++
