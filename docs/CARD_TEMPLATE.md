+++
part_id = "PRT-XXXX"
canonical_name = "your_capability_name"
capability = "A language-agnostic statement of the capability this Part provides."
category = "Pattern"
maturity = "CANDIDATE"
contract = "contract/your_interface.py"
inputs = "describe the inputs"
outputs = "describe the outputs"
permissions = "what authority it needs, or 'none'"
security = "security posture; how secrets are handled, or 'none'"
accessibility = "a11y notes, or 'n/a (library primitive)'"
performance = "complexity / benchmark summary"
failure_modes = ["how it fails, observably"]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 0        # set by R&D certification; must reach the threshold for CERTIFIED
mutation_tool = "mutmut"

[provenance]
origin = "where this came from"
ai_generated = "which portions were AI-generated"
verified_by = "how each was verified"

[rd_certification]
# empty for a CANDIDATE. On certification R&D fills:
# rd_id = "RD-2026-0000"
# verdict = "HARDWARE_STORE_PART"

[[implementations]]
language = "python"
path = "impl/python/your_module.py"
version = "0.1.0"
benchmark = ""

# On certification, add at least one:
# [[current_consumers]]
# repo = "consuming-repo"
# path = "consuming-repo/path/that/imports/it.py"
# version = "0.1.0"
# adopted = "YYYY-MM-DD"
+++

# your_capability_name (CARD)

One paragraph: what capability this Part provides, stated so a reader picks it
without caring which language implements it. Then the contract, the implementations,
the tests, and the maturity story.
