import pathlib

from generate_mappings import OUTPUT, parse_mappings, render
from validate_skill import SKILL, parse_rules

ROOT = pathlib.Path(__file__).resolve().parents[1]


def rules():
    return parse_rules(SKILL.read_text())


def test_generated_file_is_committed_and_current():
    """The whole point of a generated index is that it never lies.

    If this fails, run: python tools/generate_mappings.py
    """
    assert OUTPUT.exists(), f"{OUTPUT} is missing — run tools/generate_mappings.py"
    assert OUTPUT.read_text() == render(rules()), (
        "docs/framework-mappings.md is out of date — "
        "run python tools/generate_mappings.py"
    )


def test_every_rule_maps_to_at_least_one_framework():
    for rule in rules():
        mapped = parse_mappings(rule["mappings"])
        assert any(mapped.values()), f"{rule['id']} maps to no external framework"


def test_all_five_frameworks_are_represented():
    seen = set()
    for rule in rules():
        for key, controls in parse_mappings(rule["mappings"]).items():
            if controls:
                seen.add(key)
    assert seen == {"ssdf", "slsa", "owasp_samm", "owasp_cicd", "cncf"}


def test_curriculum_is_not_parsed_as_a_framework():
    """'Curriculum:' shares the separator with framework tokens — it is not one."""
    for rule in rules():
        for controls in parse_mappings(rule["mappings"]).values():
            assert not any("module-" in c for c in controls)


def test_owasp_samm_is_not_swallowed_by_the_owasp_cicd_prefix():
    """Both start with 'OWASP '. Prefix order in FRAMEWORKS keeps them apart."""
    mapped = parse_mappings("SSDF PW.7.2 · OWASP SAMM verification-testing")
    assert mapped["owasp_samm"] == ["verification-testing"]
    assert mapped["owasp_cicd"] == []


def test_multi_control_tokens_split_on_commas():
    mapped = parse_mappings("SSDF PS.1.1, PS.3.1 · OWASP CICD-SEC-1, CICD-SEC-5")
    assert mapped["ssdf"] == ["PS.1.1", "PS.3.1"]
    assert mapped["owasp_cicd"] == ["CICD-SEC-1", "CICD-SEC-5"]
