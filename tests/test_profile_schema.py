import json
import pathlib

import jsonschema
import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "workload-profile.schema.json"


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
