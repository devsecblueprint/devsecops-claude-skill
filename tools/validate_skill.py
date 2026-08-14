#!/usr/bin/env python3
"""Validate SKILL.md, the DSB DevSecOps skill.

SKILL.md is the product: a user needs that file and nothing else. This script
checks the properties that keep it correct and keep it standalone.

Usage:
    python tools/validate_skill.py
    python tools/validate_skill.py --quiet

Exits non-zero on any violation.
"""

import argparse
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
CAPABILITIES = ROOT / "references" / "capabilities.yaml"
CURRICULUM = ROOT / "references" / "dsb-curriculum.yaml"
RULES_DIR = ROOT / "rules"

FAMILIES = {
    "BUILD", "TEST", "SCAN", "DEPLOY", "ID",
    "SRC", "SC", "ART", "IAC", "EVD", "EXC",
}
LEVELS = {"BLOCK", "WARN", "REPORT"}
PHASES = {"build", "test", "scan", "deploy", "post-deploy", "cross-cutting"}

# A rule block opens with its bolded id and title, then a metadata line beginning
# with a middle dot, then prose, then an italic mappings line.
RULE_HEAD = re.compile(r"^\*\*(DSB-([A-Z]+)-(\d{3})) — (.+?)\*\*$", re.MULTILINE)
RULE_META = re.compile(r"^· (\S+) · `([^`]+)` · ([A-Z]+) · (.*)$")
MAPPINGS = re.compile(r"^\*(.+)\*$")


def load_registries():
    caps = {c["id"] for c in yaml.safe_load(CAPABILITIES.read_text())["capabilities"]}
    modules = {
        m["id"]: m["name"]
        for stage in yaml.safe_load(CURRICULUM.read_text())["stages"]
        for m in stage["modules"]
    }
    return caps, modules


SECTION_BREAK = re.compile(r"^(---|## )", re.MULTILINE)


def parse_rules(text):
    """Return a list of parsed rule dicts in document order."""
    rules = []
    matches = list(RULE_HEAD.finditer(text))

    for i, match in enumerate(matches):
        # A rule block ends at the next rule, or at the next section break —
        # otherwise the final rule swallows the remainder of the document.
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = SECTION_BREAK.search(text, match.end())
        if section and section.start() < end:
            end = section.start()
        block = text[match.end():end]
        lines = [ln for ln in block.splitlines() if ln.strip()]

        rule = {
            "id": match.group(1),
            "family": match.group(2),
            "number": match.group(3),
            "title": match.group(4),
            "phase": None,
            "capability": None,
            "level": None,
            "applicability": None,
            "mappings": None,
            "has_requirement": "**Requirement.**" in block,
            "has_why": "**Why.**" in block,
        }

        if lines:
            meta = RULE_META.match(lines[0])
            if meta:
                rule["phase"] = meta.group(1)
                rule["capability"] = meta.group(2)
                rule["level"] = meta.group(3)
                rule["applicability"] = meta.group(4)

        for line in reversed(lines):
            mapped = MAPPINGS.match(line)
            if mapped:
                rule["mappings"] = mapped.group(1)
                break

        rules.append(rule)

    return rules


def check(text, rules, caps, modules):
    """Return (violations, warnings)."""
    violations = []
    warnings = []

    # --- frontmatter -----------------------------------------------------
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not fm_match:
        violations.append("SKILL.md must open with YAML frontmatter")
    else:
        try:
            fm = yaml.safe_load(fm_match.group(1))
        except yaml.YAMLError as exc:
            violations.append(f"frontmatter is not valid YAML: {exc}")
            fm = {}
        if fm.get("name") != "dsb-devsecops":
            violations.append(f"frontmatter name must be 'dsb-devsecops', got {fm.get('name')!r}")
        if len(fm.get("description") or "") < 80:
            violations.append("frontmatter description is too short to trigger reliably")

    # --- standalone guarantee -------------------------------------------
    # A user copies SKILL.md alone. Any pointer at a sibling file breaks that.
    for ref in re.findall(r"`(references/[\w./-]+|schema/[\w./-]+|tools/[\w./-]+)`", text):
        violations.append(f"SKILL.md references a repository file, breaking standalone use: {ref}")
    for link in re.findall(r"\]\((?!https?://|#)([^)]+)\)", text):
        violations.append(f"SKILL.md contains a relative link, breaking standalone use: {link}")

    # --- rules -----------------------------------------------------------
    if not rules:
        violations.append("no rules parsed from SKILL.md — has the rule format changed?")

    seen = {}
    for rule in rules:
        rid = rule["id"]

        if rid in seen:
            violations.append(f"{rid}: duplicate rule id")
        seen[rid] = True

        if rule["family"] not in FAMILIES:
            violations.append(f"{rid}: unknown family '{rule['family']}'")

        if rule["phase"] is None:
            violations.append(f"{rid}: missing or malformed metadata line (· phase · `capability` · LEVEL · ...)")
            continue

        if rule["phase"] not in PHASES:
            violations.append(f"{rid}: unknown phase '{rule['phase']}'")

        if rule["capability"] not in caps:
            violations.append(f"{rid}: capability '{rule['capability']}' is not in the registry")

        if rule["level"] not in LEVELS:
            violations.append(f"{rid}: unknown enforcement level '{rule['level']}'")

        if not rule["applicability"]:
            violations.append(f"{rid}: no applicability stated")

        # Ownership and existing_controls decide who satisfies a control, not
        # whether it applies. Allowing them here would destroy the DELEGATED
        # outcome and erase the record that the control matters.
        for forbidden in ("ownership.", "existing_controls."):
            if forbidden in (rule["applicability"] or ""):
                violations.append(
                    f"{rid}: applicability references '{forbidden}' — that is a "
                    "resolution concern, not an applicability one"
                )

        if not rule["has_requirement"]:
            violations.append(f"{rid}: missing **Requirement.**")
        if not rule["has_why"]:
            violations.append(f"{rid}: missing **Why.** — rules must explain themselves")

        mappings = rule["mappings"] or ""
        if not mappings:
            violations.append(f"{rid}: missing framework/curriculum mappings line")
            continue

        cited = re.findall(r"module-\d+-\d+", mappings)
        if not cited:
            violations.append(f"{rid}: cites no DSB curriculum module")
        for module in cited:
            if module not in modules:
                violations.append(f"{rid}: curriculum module '{module}' is not in the snapshot")

        # Every citation must carry the module's real title. Without it the
        # agent invents a plausible-sounding name, and a learner goes looking
        # for a module that does not exist under that name.
        for module, title in re.findall(r"(module-\d+-\d+) \(([^)]+)\)", mappings):
            actual = modules.get(module)
            if actual and title != actual:
                violations.append(
                    f"{rid}: {module} is titled '{actual}', cited as '{title}'"
                )
        untitled = [m for m in cited if f"{m} (" not in mappings]
        if untitled:
            violations.append(
                f"{rid}: curriculum citation(s) missing the module title: "
                f"{', '.join(untitled)}"
            )

        if not re.search(r"SSDF|SLSA|OWASP|CNCF", mappings):
            violations.append(f"{rid}: cites no external framework")

    # --- cited but undefined ---------------------------------------------
    defined = set(seen)
    for cited_id in set(re.findall(r"DSB-[A-Z]+-\d{3}", text)):
        if cited_id not in defined:
            violations.append(f"{cited_id} is cited in SKILL.md but never defined")

    # --- family coverage --------------------------------------------------
    empty = sorted(FAMILIES - {r["family"] for r in rules})
    if empty:
        warnings.append(f"families with no rules: {', '.join(empty)}")

    # --- derived YAML drift ----------------------------------------------
    if RULES_DIR.exists():
        yaml_ids = {p.stem for p in RULES_DIR.rglob("*.yaml")}
        if yaml_ids and yaml_ids != defined:
            missing = len(defined - yaml_ids)
            warnings.append(
                f"rules/ holds {len(yaml_ids)} YAML rules but SKILL.md defines "
                f"{len(defined)} ({missing} not yet extracted). SKILL.md is the "
                "normative catalog; see rules/README.md for what blocks the rest."
            )

    return violations, warnings


def main():
    parser = argparse.ArgumentParser(
        description="Validate SKILL.md for the DSB DevSecOps skill.",
        epilog="Example: python tools/validate_skill.py",
    )
    parser.add_argument("--quiet", action="store_true", help="only print on failure")
    args = parser.parse_args()

    text = SKILL.read_text()
    caps, modules = load_registries()
    rules = parse_rules(text)
    violations, warnings = check(text, rules, caps, modules)

    if violations:
        print(f"FAIL: {len(violations)} violation(s)\n")
        for v in violations:
            print(f"  - {v}")
        return 1

    if not args.quiet:
        families = sorted({r["family"] for r in rules})
        print(f"OK: {len(rules)} rules across {len(families)} families, no violations")
        print(f"    {SKILL.name}: {len(text.splitlines())} lines, {len(text)} bytes")
        for w in warnings:
            print(f"    warning: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
