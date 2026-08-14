import pathlib
import re
import sys

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(ROOT / "tools"))

from validate_skill import parse_rules  # noqa: E402

DEFINED = {r["id"] for r in parse_rules((ROOT / "SKILL.md").read_text())}


def example_files():
    return sorted(p for p in EXAMPLES.rglob("*") if p.is_file())


def test_examples_exist():
    dirs = [p for p in EXAMPLES.iterdir() if p.is_dir()]
    assert len(dirs) >= 4, "expected examples covering design, review, and N/A cases"


@pytest.mark.parametrize("path", example_files(), ids=lambda p: str(p.relative_to(EXAMPLES)))
def test_every_cited_rule_is_defined(path):
    """An example citing a rule that does not exist is worse than no example."""
    cited = set(re.findall(r"DSB-[A-Z]+-\d{3}", path.read_text()))
    undefined = cited - DEFINED
    assert not undefined, f"{path.name} cites undefined rules: {sorted(undefined)}"


def test_github_actions_example_is_valid_yaml():
    workflow = EXAMPLES / "generate-github-actions" / "delivery.yml"
    assert yaml.safe_load(workflow.read_text())


def test_github_actions_example_pins_third_party_actions():
    """The examples must obey DSB-SC-002, which they teach."""
    workflow = (EXAMPLES / "generate-github-actions" / "delivery.yml").read_text()
    unpinned = re.findall(r"uses:\s*(\S+@(?:v[\d.]+|main|master))\s*$", workflow, re.MULTILINE)
    assert not unpinned, f"unpinned action references: {unpinned}"


def test_no_example_suppresses_a_security_step():
    """The examples must obey DSB-EXC-003, which they teach.

    The non-compliant review example is exempt: demonstrating the anti-pattern
    is its entire purpose.
    """
    for path in example_files():
        if "review-non-compliant" in str(path):
            continue

        is_markdown = path.suffix == ".md"

        for line in path.read_text().splitlines():
            stripped = line.strip()

            # A comment discusses the pattern rather than executing it. This is
            # the ONLY exemption in an executable file — note that YAML steps
            # begin with '-', so treating '-' as prose would silently disable
            # this check on every pipeline file.
            if stripped.startswith(("#", "//")):
                continue

            if is_markdown:
                # In prose, an occurrence inside an inline code span is a
                # quotation. Fenced blocks in non-exempt markdown are still
                # checked, since those are presented as recommended output.
                stripped = re.sub(r"`[^`]*`", "", stripped)

            assert "|| true" not in stripped, (
                f"{path.relative_to(EXAMPLES)}: suppressed security step -> {line.strip()}"
            )


def test_examples_cover_reuse_and_not_applicable():
    """The two behaviors most likely to regress are demonstrated somewhere."""
    corpus = "\n".join(p.read_text() for p in example_files())
    assert "REUSE" in corpus
    assert "Not applicable" in corpus or "NOT APPLICABLE" in corpus
