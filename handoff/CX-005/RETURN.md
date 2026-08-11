packet_id: CX-005
pr_url: https://github.com/MatrymLabs/hardware-store/pull/34
status: PARTIAL

summary: >
  Added a concurrent-claim contract case for PRT-0007. The case passes on the
  shipped SQLite adapter and fails when claim() is sabotaged into check-then-act.
  The implementation is complete locally; this return remains PARTIAL because
  the sandbox cannot resolve github.com to push the commit and update the PR.

precondition_verified:
  command: >
    git -C /home/josh/Projects/MatrymLabs/codeforge show
    origin/main:tests/test_reward_ledger_conforms.py
  result: >
    The named file exists in the locally cached origin/main at
    22732f549957c5e7e0c9d7dbccb7ec7ba781fb81 and contains
    test_only_one_of_many_concurrent_claimants_wins.

commands_run:
  - command: >
      /home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/pytest -q
      catalog/applied-once/tests/test_contract.py
    exit_code: 0
    output: "9 passed in 0.10s"
  - command: >
      runtime sabotage: replace SqliteAppliedOnce.claim with an in-memory
      check-then-act implementation and invoke the new contract test
    exit_code: 1
    output: >
      EXPECTED RED: 8 callers claimed one operation:
      [True, True, True, True, True, True, True, True]
  - command: >
      make check PY=/home/josh/Projects/MatrymLabs/hardware-store/.venv/bin/python
    exit_code: 0
    output: >
      All checks passed. Success: no issues found in 7 source files. 47 passed
      in 1.15s. Hardware Store integrity check: VERDICT: PASS (0 failing, 0 warning).

tests_passing: yes

files_touched:
  - catalog/applied-once/tests/test_contract.py
  - handoff/CX-005/RETURN.md

store_search: >
  Not required. This packet strengthens the contract suite of an existing Part
  and implements no capability.

audit:
  - part: PRT-0001 budget-gate
    central_property: "Within or breach verdicts use the configured ceiling and correct tally."
    suite_can_falsify: yes
    evidence: "Boundary, overage, default, tally, corrupt-ledger, and precision cases."
  - part: PRT-0002 circuit-breaker
    central_property: "Consecutive failures trip, open fast-fails, and one timed probe governs recovery."
    suite_can_falsify: yes
    evidence: "Trip, fast-fail without calling, half-open, probe-success, and probe-failure cases."
  - part: PRT-0003 lexicon-gate
    central_property: "Every prohibited term is located and reported under compiled policy."
    suite_can_falsify: yes
    evidence: "Location, ordering, case, suppression, literal matching, and malformed-policy cases."
  - part: PRT-0004 retry
    central_property: "One validated policy controls retry-on-exception and retry-on-result behavior."
    suite_can_falsify: yes
    evidence: "Backoff, success-after-failure, final re-raise, final result, and no-retry cases."
  - part: PRT-0005 source-monitor
    central_property: "A watched source is classified accurately without hidden persistence."
    suite_can_falsify: yes
    evidence: "First capture, unchanged, content change, broken link, pure classify, and no-persist cases."
  - part: PRT-0006 typed-settings
    central_property: "Secret defaults fail at declaration, loaded settings are safe and immutable."
    suite_can_falsify: yes
    evidence: "Secret-default, aggregate errors, redaction, frozen state, and defensive-copy cases."

blockers:
  - >
    Remote refresh and push are unavailable in this sandbox. The latest attempted fetch reported:
    ssh: Could not resolve hostname github.com: Temporary failure in name resolution.

extraction:
  reimplemented: none
  recurrence: >
    The same missing-concurrency-pressure shape appeared in the Store contract and the CodeForge
    consumer-conformance suite. This is the second occurrence: test the central guarantee under
    the concurrency model it claims to support.
  generalizable: >
    A contract-audit technique that pairs every CARD central property with a named test that goes
    red when that property is removed. Candidate only, pending R&D assessment.
  friction: >
    The dedicated worktree has no virtual environment, so the existing Hardware Store environment
    was used read-only for proof.
  dissent: none
