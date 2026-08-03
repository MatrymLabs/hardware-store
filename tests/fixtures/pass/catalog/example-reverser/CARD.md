+++
part_id = "PRT-EX01"
canonical_name = "example_reverser"
capability = "Example fixture capability: reverse a string, proving the checker (not real content)."
category = "Pattern"
maturity = "CANDIDATE"
contract = "contract/reverser.py"
inputs = "a str"
outputs = "the reversed str"
permissions = "none"
security = "pure function; no I/O, no secrets"
accessibility = "n/a (library primitive)"
performance = "O(n) in the string length"
failure_modes = ["TypeError on non-string input"]
migration = ""
deprecation_path = ""

[tests]
suite = "tests/test_contract.py"
mutation_score = 0
mutation_tool = "mutmut"

[provenance]
origin = "hand-written fixture for store_check"
ai_generated = "scaffold drafted with AI assistance, human-reviewed"
verified_by = "store_check contract-test run"

[rd_certification]
# empty on purpose: a CANDIDATE has not been through R&D's gate yet

[[implementations]]
language = "python"
path = "impl/python/example_reverser.py"
version = "0.1.0"
benchmark = ""
+++

# example_reverser (CARD)

**This is a fixture, not real catalog content.** It exists only to prove
`store_check`: a well-formed CANDIDATE passes, and a sabotaged copy fails on the
exact check that was broken. Real Parts enter the catalog through R&D
certification (Phase 3+), never by hand.

- **Capability:** reverse a string (language-agnostic statement above).
- **Contract:** `contract/reverser.py` (the shape every implementation honors).
- **Implementation:** `impl/python/example_reverser.py`.
- **Tests:** `tests/test_contract.py` (acceptance + refusal + hostile cases).
- **Maturity:** CANDIDATE. No `rd_certification`, no consumers, `mutation_score = 0`
  are all legal here; they become mandatory only at CERTIFIED.
