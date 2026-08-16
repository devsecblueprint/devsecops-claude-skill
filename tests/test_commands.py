import json
import pathlib
import re

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMMANDS = ROOT / "commands"
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
CHANGELOG = ROOT / "CHANGELOG.md"

EXPECTED = {"advise", "design", "assess"}


def command_files():
    return sorted(COMMANDS.glob("*.md"))


def frontmatter(path):
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.DOTALL)
    assert match, f"{path.name}: missing YAML frontmatter"
    return yaml.safe_load(match.group(1))


def body(path):
    return re.sub(r"^---\n.*?\n---\n", "", path.read_text(), flags=re.DOTALL)


@pytest.fixture(scope="module")
def manifest():
    return json.loads(MANIFEST.read_text())


def test_the_three_entry_points_exist():
    assert {p.stem for p in command_files()} == EXPECTED


def test_plugin_name_produces_the_documented_namespace(manifest):
    """Commands are invoked as /<plugin-name>:<command>. The name is the namespace,
    so renaming the plugin silently renames every documented command."""
    assert manifest["name"] == "devsecops-engineer"


def test_manifest_declares_release_metadata(manifest):
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]), manifest["version"]
    assert manifest["license"] == "MIT"
    assert manifest["description"]


def test_manifest_version_matches_the_changelog(manifest):
    """A release where the manifest and the changelog disagree is a release where
    nobody can tell which one shipped."""
    versions = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", CHANGELOG.read_text(), re.MULTILINE)
    assert versions, "CHANGELOG.md has no released version heading"
    assert versions[0] == manifest["version"]


@pytest.mark.parametrize("path", command_files(), ids=lambda p: p.stem)
def test_command_declares_a_description(path):
    """The description is what a user reads in the slash-command menu."""
    assert len(frontmatter(path).get("description") or "") >= 40


@pytest.mark.parametrize("path", command_files(), ids=lambda p: p.stem)
def test_command_loads_the_skill_rather_than_restating_it(path):
    assert "${CLAUDE_PLUGIN_ROOT}/SKILL.md" in body(path), (
        f"{path.name}: must point at SKILL.md, which is the single catalog"
    )


@pytest.mark.parametrize("path", command_files(), ids=lambda p: p.stem)
def test_command_takes_the_users_arguments(path):
    assert "$ARGUMENTS" in body(path), f"{path.name}: never receives what the user typed"


@pytest.mark.parametrize("path", command_files(), ids=lambda p: p.stem)
def test_command_contains_no_rule_logic(path):
    """Commands select a mode. They do not carry the catalog.

    A command that names rules or enforcement levels is a second copy of the
    catalog that no validator checks, so it drifts — and then the command and a
    plain-language request give different answers.
    """
    text = path.read_text()

    rule_ids = re.findall(r"DSB-[A-Z]+-\d{3}", text)
    assert not rule_ids, f"{path.name}: restates rules {sorted(set(rule_ids))}"

    levels = re.findall(r"\b(BLOCK|WARN|REPORT)\b", text)
    assert not levels, f"{path.name}: restates enforcement levels {sorted(set(levels))}"


@pytest.mark.parametrize("path", command_files(), ids=lambda p: p.stem)
def test_command_stays_short(path):
    """A thin wrapper that grew past a screen is no longer a wrapper."""
    lines = [ln for ln in body(path).splitlines() if ln.strip()]
    assert len(lines) <= 30, f"{path.name}: {len(lines)} lines — move content into SKILL.md"
