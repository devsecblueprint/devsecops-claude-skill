# What this changes

<!-- One paragraph. What is different after this merges? -->

## Engineering reasoning

<!-- Why this is the right change. For rule changes this is the important section:
     what workload or failure mode motivated it. -->

## Type of change

- [ ] New rule
- [ ] Change to an existing rule
- [ ] Example or reference pipeline
- [ ] Tooling, schema, or tests
- [ ] Documentation

## Checks

- [ ] `python tools/validate_skill.py` passes
- [ ] `python -m pytest` passes
- [ ] No specific product is presented as a DSB requirement
- [ ] `SKILL.md` remains standalone — no links or references to sibling files

## If this adds or changes a rule

- [ ] Rule ID is new and has never been used
- [ ] Capability exists in `references/capabilities.yaml`
- [ ] Applicability references only Workload Profile fields, and never
      `ownership` or `existing_controls`
- [ ] Enforcement default is justified in the reasoning above
- [ ] At least one framework mapping and one curriculum module, both real
- [ ] `python tools/generate_mappings.py` re-run if mappings changed

## Behavior verified against a live agent

<!-- A SKILL.md change that reads well but does not change agent behavior has not
     landed. What did you ask it, and what changed? Write "n/a" for tooling-only
     changes. -->
