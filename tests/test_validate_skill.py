import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_skill import check, load_registries, parse_rules  # noqa: E402

SKILL_TEXT = (ROOT / "SKILL.md").read_text()

GOOD_RULE = """**DSB-SCAN-099 — Example control**
· scan · `sast` · BLOCK · applies when `languages exists`
**Requirement.** Something must be true about the workload before promotion.
**Why.** Because leaving it unchecked hides a defect class nothing else catches.
*SSDF PW.7.1 · Curriculum: module-2-2 (What is Application Security?)*
"""

HEADER = """---
name: dsb-devsecops
description: >
  A description long enough to clear the minimum length check that guards against
  a skill that never triggers because nobody can match its description text.
---

## 3. The DSB rule catalog

"""


def build(rule_block):
    return HEADER + rule_block + "\n---\n"


def run(rule_block):
    text = build(rule_block)
    caps, modules = load_registries()
    return check(text, parse_rules(text), caps, modules)[0]


def test_real_skill_has_no_violations():
    caps, modules = load_registries()
    violations, _ = check(SKILL_TEXT, parse_rules(SKILL_TEXT), caps, modules)
    assert violations == []


def test_real_skill_defines_all_eleven_families():
    families = {r["family"] for r in parse_rules(SKILL_TEXT)}
    assert len(families) == 11


def test_good_rule_passes():
    assert run(GOOD_RULE) == []


def test_unregistered_capability_is_caught():
    bad = GOOD_RULE.replace("`sast`", "`telepathy-scanning`")
    assert any("telepathy-scanning" in v for v in run(bad))


def test_unknown_curriculum_module_is_caught():
    bad = GOOD_RULE.replace("module-2-2", "module-9-9")
    assert any("module-9-9" in v for v in run(bad))


def test_missing_curriculum_is_caught():
    bad = GOOD_RULE.replace(
        " · Curriculum: module-2-2 (What is Application Security?)", ""
    )
    assert any("curriculum" in v.lower() for v in run(bad))


def test_wrong_module_title_is_caught():
    """Without the real title the agent invents one, and learners chase a
    module that does not exist under that name."""
    bad = GOOD_RULE.replace(
        "(What is Application Security?)", "(security scanning in the pipeline)"
    )
    violations = run(bad)
    assert any("is titled" in v for v in violations)


def test_untitled_module_citation_is_caught():
    bad = GOOD_RULE.replace(" (What is Application Security?)", "")
    assert any("missing the module title" in v for v in run(bad))


def test_real_skill_titles_every_curriculum_citation():
    caps, modules = load_registries()
    for rule in parse_rules(SKILL_TEXT):
        mappings = rule["mappings"] or ""
        for module in __import__("re").findall(r"module-\d+-\d+", mappings):
            assert f"{module} (" in mappings, f"{rule['id']}: {module} has no title"


def test_missing_framework_is_caught():
    bad = GOOD_RULE.replace("SSDF PW.7.1 · ", "")
    assert any("framework" in v.lower() for v in run(bad))


def test_bad_enforcement_level_is_caught():
    bad = GOOD_RULE.replace("· BLOCK ·", "· MAYBE ·")
    assert any("MAYBE" in v for v in run(bad))


def test_bad_phase_is_caught():
    bad = GOOD_RULE.replace("· scan ·", "· whenever ·")
    assert any("whenever" in v for v in run(bad))


def test_missing_why_is_caught():
    bad = GOOD_RULE.replace("**Why.** Because leaving", "Because leaving")
    assert any("Why" in v for v in run(bad))


def test_missing_requirement_is_caught():
    bad = GOOD_RULE.replace("**Requirement.** Something", "Something")
    assert any("Requirement" in v for v in run(bad))


def test_duplicate_rule_id_is_caught():
    assert any("duplicate" in v.lower() for v in run(GOOD_RULE + "\n" + GOOD_RULE))


def test_ownership_in_applicability_is_caught():
    """Ownership decides who satisfies a control, never whether it applies."""
    bad = GOOD_RULE.replace(
        "applies when `languages exists`",
        "applies when `ownership.sast` is not external-governed",
    )
    violations = run(bad)
    assert any("resolution concern" in v for v in violations)


def test_existing_controls_in_applicability_is_caught():
    bad = GOOD_RULE.replace(
        "applies when `languages exists`",
        "applies when `existing_controls.sast` is empty",
    )
    assert any("resolution concern" in v for v in run(bad))


def test_cited_but_undefined_rule_is_caught():
    bad = GOOD_RULE + "\nSee also DSB-SCAN-777 for details.\n"
    assert any("DSB-SCAN-777" in v for v in run(bad))


def test_reference_to_repo_file_breaks_standalone():
    bad = GOOD_RULE + "\nSee `references/capabilities.yaml` for the registry.\n"
    assert any("standalone" in v for v in run(bad))


def test_relative_link_breaks_standalone():
    bad = GOOD_RULE + "\nSee [the catalog](docs/catalog.md).\n"
    assert any("standalone" in v for v in run(bad))


def test_absolute_link_is_allowed():
    ok = GOOD_RULE + "\nSee [DSB](https://github.com/devsecblueprint).\n"
    assert run(ok) == []


def test_cli_exits_zero_on_real_skill():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_skill.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "42 rules across 11 families" in result.stdout
