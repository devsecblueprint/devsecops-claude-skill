import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "references" / "dsb-curriculum.yaml"


def load():
    return yaml.safe_load(SNAPSHOT.read_text())


def test_snapshot_has_four_stages():
    assert len(load()["stages"]) == 4


def test_module_ids_are_unique_and_well_formed():
    ids = [m["id"] for s in load()["stages"] for m in s["modules"]]
    assert len(ids) == len(set(ids))
    for mid in ids:
        assert re.fullmatch(r"module-\d+-\d+", mid), mid


def test_snapshot_records_its_source_and_date():
    data = load()
    assert data["source"]
    assert data["snapshot_date"] == "2026-08-12"
