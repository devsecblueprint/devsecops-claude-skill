import json
import pathlib

import jsonschema
import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "rule.schema.json"

VALID_RULE = """
id: DSB-SCAN-004
title: Container image vulnerability scanning
family: SCAN
phase: scan
capability: container-image-scanning
requirement: Container images must be scanned before promotion.
rationale: Base images accumulate CVEs independently of application code.
applicability:
  all_of:
    - artifacts.container: true
framework_mappings:
  ssdf: [PW.4.1]
enforcement:
  default_level: BLOCK
  automatable: true
tooling:
  examples: [Trivy, Grype]
  prefer_existing_tool: true
dsb_curriculum: [module-2-6]
status: active
"""


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text())


def test_valid_rule_passes(schema):
    jsonschema.validate(yaml.safe_load(VALID_RULE), schema)


def test_bad_id_format_is_rejected(schema):
    rule = yaml.safe_load(VALID_RULE)
    rule["id"] = "SCAN-4"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(rule, schema)


def test_unknown_enforcement_level_is_rejected(schema):
    rule = yaml.safe_load(VALID_RULE)
    rule["enforcement"]["default_level"] = "MAYBE"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(rule, schema)


def test_missing_rationale_is_rejected(schema):
    rule = yaml.safe_load(VALID_RULE)
    del rule["rationale"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(rule, schema)


def test_extra_top_level_key_is_rejected(schema):
    rule = yaml.safe_load(VALID_RULE)
    rule["severity"] = "high"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(rule, schema)
