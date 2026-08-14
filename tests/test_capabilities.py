import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "references" / "capabilities.yaml"


def load():
    return yaml.safe_load(REGISTRY.read_text())["capabilities"]


def test_registry_loads():
    assert len(load()) >= 10


def test_ids_are_unique():
    ids = [c["id"] for c in load()]
    assert len(ids) == len(set(ids))


def test_every_capability_has_group_and_summary():
    for cap in load():
        assert cap["group"], f"{cap['id']} missing group"
        assert cap["summary"], f"{cap['id']} missing summary"


def test_ids_are_kebab_case():
    import re

    for cap in load():
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", cap["id"]), cap["id"]
