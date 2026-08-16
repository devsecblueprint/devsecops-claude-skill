import json
import pathlib
import re

import jsonschema
import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "workload-profile.schema.json"
SKILL_PATH = ROOT / "SKILL.md"
EXAMPLES = ROOT / "examples"

PROFILE_BLOCK = re.compile(
    r"^## Workload profile\s*\n+```yaml\n(.*?)\n```", re.MULTILINE | re.DOTALL
)


def example_profiles():
    """The workload profiles published in the example READMEs."""
    found = []
    for path in sorted(EXAMPLES.rglob("README.md")):
        match = PROFILE_BLOCK.search(path.read_text())
        if match:
            found.append((str(path.relative_to(ROOT)), yaml.safe_load(match.group(1))))
    return found


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text())


def test_minimal_profile_validates(schema):
    profile = yaml.safe_load(
        """
        artifacts:
          container: true
        """
    )
    jsonschema.validate(profile, schema)


def test_tristate_unknown_is_accepted(schema):
    profile = yaml.safe_load(
        """
        artifacts:
          container: unknown
        """
    )
    jsonschema.validate(profile, schema)


def test_unknown_top_level_field_is_rejected(schema):
    profile = {"not_a_real_field": True}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(profile, schema)


def test_every_documented_profile_field_is_in_the_schema(schema):
    """SKILL.md §2 publishes the closed vocabulary; the schema enforces it.

    The schema sets `additionalProperties: false`, so a field documented in
    SKILL.md but absent here is a field a user is told to state and that then
    fails validation.
    """
    vocabulary = re.search(
        r"The vocabulary is closed.*?```yaml\n(.*?)\n```", SKILL_PATH.read_text(), re.DOTALL
    )
    assert vocabulary, "SKILL.md §2 no longer publishes the closed vocabulary block"

    documented = set(re.findall(r"^(\w+):", vocabulary.group(1), re.MULTILINE))
    missing = documented - set(schema["properties"])
    assert not missing, f"documented in SKILL.md but rejected by the schema: {sorted(missing)}"


@pytest.mark.parametrize("name,profile", example_profiles(), ids=lambda v: v if isinstance(v, str) else "")
def test_published_example_profiles_validate(schema, name, profile):
    """An example profile that fails its own schema teaches the wrong shape."""
    jsonschema.validate(profile, schema)


def test_example_profiles_were_actually_found():
    assert len(example_profiles()) >= 3


def test_array_fields_accept_unknown(schema):
    """SKILL.md: 'Every field is tri-state'. That has to include list fields —
    'we deploy somewhere, I do not know where' is a real answer."""
    jsonschema.validate({"deploy": {"environments": "unknown"}}, schema)
    jsonschema.validate({"languages": "unknown"}, schema)


def test_fields_rules_depend_on_are_accepted(schema):
    """Each of these carries a rule's applicability and was missing before."""
    jsonschema.validate({"source": {"fork_prs_allowed": True}}, schema)      # DSB-SRC-003
    jsonschema.validate({"policy": {"signing_required": True}}, schema)      # DSB-ART-002
    jsonschema.validate({"policy": {"provenance_required": True}}, schema)   # DSB-ART-003
    jsonschema.validate({"registry": {"controlled_proxy": True}}, schema)    # DSB-SC-001
    jsonschema.validate({"cicd": {"shared_library": True}}, schema)


def test_existing_controls_accepts_multiple_tools_per_capability(schema):
    profile = yaml.safe_load(
        """
        existing_controls:
          software-composition-analysis:
            - tool: Black Duck
              owner: appsec-team
              scope: full
            - tool: Snyk
              owner: platform-team
              scope: full
        """
    )
    jsonschema.validate(profile, schema)
