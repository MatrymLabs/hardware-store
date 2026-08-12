"""Proof for store_check: it passes a well-formed CANDIDATE and fails a sabotage.

A checker you never watched fail is unproven (OUTPUT DISCIPLINE). So every check
gets a sabotage here: we stage the good fixture into a tmp dir, break exactly one
thing, and assert store_check fails on that specific check.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from hardware_store import store_check as sc
from hardware_store import store_lib as sl

PASS_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pass"
PART = "example-reverser"


def _stage(tmp_path: Path) -> Path:
    """Copy the good fixture into tmp so a test can sabotage it in isolation."""
    root = tmp_path / "store"
    shutil.copytree(PASS_FIXTURE, root)
    return root


def _card(root: Path) -> Path:
    return root / "catalog" / PART / "CARD.md"


def _sync_registry(root: Path) -> None:
    """Regenerate the fixture's registry from its own cards. registry.json is GENERATED."""
    import json as _json
    reg = sl.build_registry(sl.load_cards(root / "catalog"))
    (root / "registry.json").write_text(_json.dumps(reg, indent=2) + "\n", encoding="utf-8")


def _checks(report: sl.Report) -> set[str]:
    return {f.check for f in report.failures}


# --- The good fixture passes, tests actually run (CMD) ------------------------

def test_pass_fixture_is_clean_and_tests_run() -> None:
    report = sc.run_check(PASS_FIXTURE, PASS_FIXTURE.parent, threshold=70, run_tests=True)
    assert report.verdict == "PASS", [f.__dict__ for f in report.failures]


def test_empty_store_passes(tmp_path: Path) -> None:
    (tmp_path / "catalog").mkdir()
    (tmp_path / "registry.json").write_text("[]", encoding="utf-8")
    report = sc.run_check(tmp_path, tmp_path.parent, threshold=70, run_tests=False)
    assert report.verdict == "PASS"


# --- The three mandated sabotages --------------------------------------------

def test_sabotage_card_without_impl(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    (root / "catalog" / PART / "impl" / "python" / "example_reverser.py").unlink()
    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)
    assert report.verdict == "FAIL"
    assert "impl-exists" in _checks(report)


def test_sabotage_impl_without_tests(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    shutil.rmtree(root / "catalog" / PART / "tests")
    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)
    assert report.verdict == "FAIL"
    assert "tests-exist" in _checks(report)


def test_sabotage_certified_without_consumer(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    # Promote to CERTIFIED with a cert record + biting mutation score, but no consumer.
    text = _card(root).read_text(encoding="utf-8")
    text = text.replace('maturity = "CANDIDATE"', 'maturity = "CERTIFIED"')
    text = text.replace("mutation_score = 0", "mutation_score = 85")
    text = text.replace(
        "[rd_certification]\n# empty on purpose: a CANDIDATE has not been through R&D's gate yet",
        '[rd_certification]\nrd_id = "RD-2026-0000"\nverdict = "HARDWARE_STORE_PART"',
    )
    _card(root).write_text(text, encoding="utf-8")
    reg = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    reg[0]["maturity"] = "CERTIFIED"
    (root / "registry.json").write_text(json.dumps(reg, indent=2), encoding="utf-8")

    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)
    assert report.verdict == "FAIL"
    consumer_fails = [f for f in report.failures if f.check == "certified-gate"]
    assert any("current_consumers" in f.message for f in consumer_fails), \
        [f.__dict__ for f in report.failures]


# --- Extra sabotages: one per remaining check --------------------------------

def test_sabotage_ghost_registry_entry(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    reg = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    reg.append({"part_id": "PRT-GHOST", "slug": "ghost", "canonical_name": "ghost",
                "capability": "", "category": "Pattern", "maturity": "CANDIDATE",
                "languages": [], "consumers": [], "version": ""})
    (root / "registry.json").write_text(json.dumps(reg, indent=2), encoding="utf-8")
    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)
    assert report.verdict == "FAIL"
    assert "registry-mirror" in _checks(report)


def test_sabotage_unlisted_card(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    (root / "registry.json").write_text("[]", encoding="utf-8")
    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)
    assert "registry-mirror" in _checks(report)


def test_sabotage_missing_required_field(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    text = _card(root).read_text(encoding="utf-8")
    text = text.replace('capability = "Example fixture capability: reverse a string, '
                        'proving the checker (not real content)."', 'capability = ""')
    _card(root).write_text(text, encoding="utf-8")
    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)
    assert "card-schema" in _checks(report)


def test_sabotage_deprecated_vocab(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    banned = sl.DEPRECATED_VOCAB[0]  # inject without spelling it in this test file
    with _card(root).open("a", encoding="utf-8") as fh:
        fh.write(f"\n\nThis card mentions {banned}, which is retired vocabulary.\n")
    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)
    assert "no-deprecated-vocab" in _checks(report)


def test_sabotage_certified_below_mutation_threshold(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    text = _card(root).read_text(encoding="utf-8")
    text = text.replace('maturity = "CANDIDATE"', 'maturity = "CERTIFIED"')
    text = text.replace(
        "[rd_certification]\n# empty on purpose: a CANDIDATE has not been through R&D's gate yet",
        '[rd_certification]\nrd_id = "RD-2026-0000"\nverdict = "HARDWARE_STORE_PART"',
    )
    consumer = ('\n[[current_consumers]]\nrepo = "demo"\npath = "demo/x.py"\n'
                'version = "0.1.0"\n')
    text = text.replace("+++\n\n# example_reverser",
                        consumer + "+++\n\n# example_reverser")
    _card(root).write_text(text, encoding="utf-8")
    reg = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    reg[0]["maturity"] = "CERTIFIED"
    reg[0]["consumers"] = ["demo"]
    (root / "registry.json").write_text(json.dumps(reg, indent=2), encoding="utf-8")
    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)
    fails = [f for f in report.failures if f.check == "certified-gate"]
    assert any("mutation score" in f.message for f in fails), [f.__dict__ for f in fails]


# --- Consumer resolution is a unit (its live proof is Phase 4) ----------------

def test_consumer_resolution_detects_real_and_fake_import(tmp_path: Path) -> None:
    real = tmp_path / "real.py"
    real.write_text(
        '"""VENDORED from the Matrym Labs Hardware Store: part example_reverser (PRT-0005)."""\n',
        encoding="utf-8",
    )
    fake = tmp_path / "fake.py"
    fake.write_text("x = 1\n", encoding="utf-8")
    card = sl.Card(slug="example-reverser", path=tmp_path / "CARD.md",
                   data={"canonical_name": "example_reverser", "part_id": "PRT-0005"})
    assert sc._path_imports_part(real, card) is True
    assert sc._path_imports_part(fake, card) is False


def _certify_with_unresolvable_consumer(root: Path) -> None:
    """Turn the staged CANDIDATE fixture into a CERTIFIED card whose only defect is a consumer
    path that does not resolve under the fleet root (so consumer-resolves is the sole failure)."""
    text = _card(root).read_text(encoding="utf-8")
    text = text.replace('maturity = "CANDIDATE"', 'maturity = "CERTIFIED"')
    text = text.replace("mutation_score = 0", "mutation_score = 90")
    text = text.replace(
        "[rd_certification]\n# empty on purpose: a CANDIDATE has not been through R&D's gate yet",
        '[rd_certification]\nrd_id = "RD-2026-0000"\nverdict = "HARDWARE_STORE_PART"',
    )
    consumer = ('\n[[current_consumers]]\nrepo = "demo"\npath = "demo/does_not_exist.py"\n'
                'version = "0.1.0"\n')
    text = text.replace("+++\n\n# example_reverser", consumer + "+++\n\n# example_reverser")
    _card(root).write_text(text, encoding="utf-8")
    reg = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    reg[0]["maturity"] = "CERTIFIED"
    reg[0]["consumers"] = ["demo"]
    (root / "registry.json").write_text(json.dumps(reg, indent=2), encoding="utf-8")


def test_no_fleet_skips_consumer_resolution(tmp_path: Path) -> None:
    # consumer-resolution needs the fleet on disk; CI runs with check_consumers=False (--no-fleet).
    root = _stage(tmp_path)
    _certify_with_unresolvable_consumer(root)
    parent = root.parent
    (parent / "demo").mkdir()
    with_fleet = sc.run_check(root, parent, threshold=70, run_tests=False, check_consumers=True)
    assert "consumer-resolves" in _checks(with_fleet)  # the fleet-aware gate catches it
    no_fleet = sc.run_check(root, parent, threshold=70, run_tests=False, check_consumers=False)
    assert "consumer-resolves" not in _checks(no_fleet)  # CI skips it, and nothing else breaks
    assert no_fleet.verdict == "PASS", [f.__dict__ for f in no_fleet.failures]


def _certify_with_consumer(root: Path, content: str, *, part_id: str = "PRT-0005",
                           path: str = "demo/consumer.py") -> None:
    """Make the fixture certified and place one claimed consumer under its fleet root."""
    text = _card(root).read_text(encoding="utf-8")
    text = text.replace('part_id = "PRT-EX01"', f'part_id = "{part_id}"')
    text = text.replace('maturity = "CANDIDATE"', 'maturity = "CERTIFIED"')
    text = text.replace("mutation_score = 0", "mutation_score = 90")
    text = text.replace(
        "[rd_certification]\n# empty on purpose: a CANDIDATE has not been through R&D's gate yet",
        '[rd_certification]\nrd_id = "RD-2026-0000"\nverdict = "HARDWARE_STORE_PART"',
    )
    consumer = f'\n[[current_consumers]]\nrepo = "demo"\npath = "{path}"\nversion = "0.1.0"\n'
    text = text.replace("+++\n\n# example_reverser", consumer + "+++\n\n# example_reverser")
    _card(root).write_text(text, encoding="utf-8")

    reg = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    reg[0]["part_id"] = part_id
    reg[0]["maturity"] = "CERTIFIED"
    reg[0]["consumers"] = ["demo"]
    (root / "registry.json").write_text(json.dumps(reg, indent=2), encoding="utf-8")

    consumer_path = root.parent / path
    consumer_path.parent.mkdir(parents=True, exist_ok=True)
    consumer_path.write_text(content, encoding="utf-8")


def _consumer_findings(report: sl.Report) -> list[sl.Finding]:
    return [f for f in report.findings if f.check == "consumer-resolves"]


def test_consumer_without_provenance_citation_is_reported(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    _certify_with_consumer(
        root,
        "EXAMPLE_REVERSER = 1\nexample_reverser_alias = EXAMPLE_REVERSER\n",
    )

    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)

    findings = _consumer_findings(report)
    assert findings, [f.__dict__ for f in report.findings]
    assert any("demo/consumer.py" in f.message for f in findings)


def test_consumer_with_matching_prt_citation_is_accepted(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    _certify_with_consumer(
        root,
        '"""VENDORED from the Matrym Labs Hardware Store: part example_reverser (PRT-0005)."""\n',
    )

    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)

    assert not _consumer_findings(report), [f.__dict__ for f in report.findings]


def test_consumer_citing_a_different_part_id_is_reported(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    _certify_with_consumer(
        root,
        "# VENDORED from the Matrym Labs Hardware Store: part example_reverser (PRT-0009)\n",
    )

    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)

    findings = _consumer_findings(report)
    assert findings, [f.__dict__ for f in report.findings]
    assert any("PRT-0005" in f.message for f in findings)


def test_consumer_citing_only_rd_provenance_id_is_accepted(tmp_path: Path) -> None:
    real = tmp_path / "real.py"
    real.write_text('"""extracted from RD-2026-0009"""\n', encoding="utf-8")
    card = sl.Card(slug="example-reverser", path=tmp_path / "CARD.md", data={
        "canonical_name": "example_reverser",
        "part_id": "PRT-0005",
        "provenance": {"rd_id": "RD-2026-0009"},
    })
    assert sc._path_imports_part(real, card) is True


def test_consumer_citing_neither_part_identity_is_rejected(tmp_path: Path) -> None:
    fake = tmp_path / "fake.py"
    fake.write_text("x = 1\n", encoding="utf-8")
    card = sl.Card(slug="example-reverser", path=tmp_path / "CARD.md", data={
        "canonical_name": "example_reverser",
        "part_id": "PRT-0005",
        "provenance": {"rd_id": "RD-2026-0009"},
    })
    assert sc._path_imports_part(fake, card) is False


def test_an_uncited_consumer_FAILS_rather_than_warns(tmp_path: Path) -> None:
    """This test previously asserted the opposite, and that is how the defect survived.

    It read `provenance findings are warnings not failures`, so a Part could list a consumer that
    had never cited it and the Store still reported PASS. Four of seven Parts did exactly that, and
    every one of those entries was an ORIGIN filed in the adopters' column: the Part had been
    extracted FROM that code, not adopted BY it. As a warning, the gate said so quietly enough that
    nobody acted on it for as long as the catalogue has existed.

    A consumer that does not cite the Part is a reuse claim with no evidence, and evidenced reuse
    is the Store's entire assertion. Origins belong in `extracted_from`; what stays in `consumers`
    must earn the word.
    """
    root = _stage(tmp_path)
    _certify_with_consumer(root, "x = example_reverser\n")  # uses the code, cites no part id

    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)

    assert report.verdict == "FAIL"
    assert any(f.check == "consumer-resolves" for f in report.failures)
    assert any("does not cite" in f.message for f in report.failures)


def test_missing_fleet_root_reports_unverified_rather_than_silently_passing(
    tmp_path: Path,
) -> None:
    root = _stage(tmp_path)
    _certify_with_consumer(root, "from example_reverser import example_reverser\n")

    report = sc.run_check(root, tmp_path / "missing-fleet", threshold=70,
                          run_tests=False, check_consumers=False)

    assert report.verdict == "PASS"
    assert any("not verified" in f.message.lower() for f in report.warnings), \
        [f.__dict__ for f in report.findings]


def test_missing_sibling_is_unverified_not_a_false_failure(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    _certify_with_consumer(root, '"""VENDORED (PRT-0005)."""\n')
    shutil.rmtree(tmp_path / "demo")

    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)

    findings = _consumer_findings(report)
    assert not report.failures
    assert len(findings) == 1
    assert findings[0].severity == "unverified"
    assert "demo" in findings[0].message
    assert "VERDICT: UNVERIFIED (0 failing, 0 warning, 1 unverified)" in sc.render(report, root)


def test_missing_consumer_file_under_present_sibling_still_fails(tmp_path: Path) -> None:
    root = _stage(tmp_path)
    _certify_with_consumer(root, '"""VENDORED (PRT-0005)."""\n')
    (tmp_path / "demo" / "consumer.py").unlink()

    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)

    findings = _consumer_findings(report)
    assert report.verdict == "FAIL"
    assert len(findings) == 1
    assert findings[0].severity == "fail"
    assert "does not exist" in findings[0].message


def test_consumer_claims_are_checked_on_every_card_not_just_certified_ones(tmp_path: Path) -> None:
    """The check ran on `c.is_certified` only, and skipped the population the error lived in.

    Four CANDIDATE Parts listed consumers that had never cited them. Every one was an ORIGIN filed
    in the adopters' column, and none was ever inspected, because the gate only looked at Parts
    that had already been through the Verdict Gate. It reported clean about what it had checked and
    said nothing about the rest.
    """
    root = _stage(tmp_path)
    _certify_with_consumer(root, "x = example_reverser\n")
    card = _card(root)
    card.write_text(card.read_text(encoding="utf-8").replace("CERTIFIED", "CANDIDATE"),
                    encoding="utf-8")
    _sync_registry(root)

    report = sc.run_check(root, root.parent, threshold=70, run_tests=False)
    assert any(f.check == "consumer-resolves" for f in report.failures), (
        "a CANDIDATE listing an uncited consumer makes the same unevidenced claim as a "
        "CERTIFIED one"
    )


def test_a_stale_checkout_is_UNVERIFIED_not_a_false_failure(tmp_path: Path) -> None:
    """The other half of the same defect: the gate asked the filesystem, not git.

    On 2026-08-12 it failed `typed-settings` because a `recall` checkout sat two commits behind,
    while the file was on origin/main the whole time. "The record points at something that no
    longer exists" and "this checkout cannot see it" are different findings.
    """
    root = _stage(tmp_path)
    _certify_with_consumer(root, "from example_reverser import example_reverser\n")
    _sync_registry(root)

    # a sibling that is not a git repository at all: git cannot answer, so neither may the gate
    report = sc.run_check(root, tmp_path / "no-such-fleet", threshold=70, run_tests=False)
    assert not any(f.check == "consumer-resolves" and f.severity == "fail"
                   for f in report.failures), "an unreadable environment is not a false claim"
