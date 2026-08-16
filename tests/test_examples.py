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
    """The examples must obey DSB-SC-002, which they teach.

    Deliberately not anchored to end-of-line: every pinned `uses:` in the
    example carries a trailing `# v4.2.2` comment, so an end anchor would let
    `uses: foo/bar@v1  # whatever` through — the exact thing this checks for.
    """
    workflow = (EXAMPLES / "generate-github-actions" / "delivery.yml").read_text()
    unpinned = re.findall(
        r"uses:\s*([^@\s]+@(?:v[\d.]+|main|master))\b", workflow
    )
    assert not unpinned, f"unpinned action references: {unpinned}"


def test_jenkins_example_pins_its_shared_library():
    """DSB-SC-002 covers shared libraries too, not only GitHub Actions.

    A Jenkins shared library executes inside the pipeline with its credentials.
    `@Library('x@v3')` is a mutable reference and is the same defect as an
    unpinned action.
    """
    jenkinsfile = (EXAMPLES / "generate-jenkins" / "Jenkinsfile").read_text()
    for library, version in re.findall(r"@Library\(['\"]([^@'\"]+)@([^'\"]+)['\"]", jenkinsfile):
        assert re.fullmatch(r"[0-9a-f]{40}", version), (
            f"shared library {library!r} pinned to mutable reference {version!r} "
            "— DSB-SC-002 requires an immutable commit"
        )


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
