# Contributing

Thanks for wanting to improve the DSB DevSecOps Engineering Skill.

This repository is maintained by The DevSec Blueprint. Contributions are welcome, with
one constraint that shapes everything below: **DSB rules define capabilities and
outcomes, never vendors.**

---

## Before you start

By contributing you agree to the [Contributor License Agreement](docs/legal/CLA.md).
Contributions are licensed under PolyForm Noncommercial 1.0.0, matching the repository.

For anything larger than a typo, open an issue first. A rule change is a change to
engineering guidance that other people will apply to production pipelines — it
deserves discussion before implementation.

---

## The one rule that is not negotiable

**Never make a specific product a requirement.**

```
Wrong:  "Projects must use Trivy to scan container images."
Right:  "Container images must be scanned for known vulnerabilities.
         Examples: Trivy, Grype, Prisma Cloud, Black Duck, Wiz."
```

If a contribution requires a named product, it will be rejected regardless of how good
that product is. Organizations already own security tooling; the skill's job is to use
what they have, not to sell them something else.

---

## Setup

```bash
git clone https://github.com/devsecblueprint/devsecops-claude-skill.git
cd devsecops-claude-skill

uv venv && source .venv/bin/activate
uv pip install -r tools/requirements.txt

python tools/validate_skill.py
python -m pytest
```

Install your working copy to test it against a live agent:

```bash
mkdir -p ~/.claude/skills/dsb-devsecops
cp SKILL.md ~/.claude/skills/dsb-devsecops/
```

Then start a fresh agent session and exercise it. `SKILL.md` changes are only real if
they change agent behavior — verify that, do not assume it.

---

## Adding or changing a rule

Rules live in `SKILL.md` under section 3, grouped by family.

### Format

```markdown
**DSB-SCAN-004 — Container image vulnerability scanning**
· scan · `container-image-scanning` · BLOCK · applies when `artifacts.container`, and not `runtime.serverless`
**Requirement.** What must be true. Written as an outcome, not an implementation.
**Why.** The engineering reason. This is the part people actually read.
*SSDF PW.4.1 · SLSA build-L2 · OWASP CICD-SEC-4 · Curriculum: module-2-6*
```

### Checklist

- [ ] **ID is new and permanent.** Never reuse a retired ID — they appear in audit
      records. Take the next free number in the family.
- [ ] **Family is correct.** `DSB-SCAN` is application-layer scanning; IaC scanning
      belongs in `DSB-IAC`; pipeline security belongs in `DSB-SRC`, `DSB-ID`, or
      `DSB-SC`.
- [ ] **Capability exists** in `references/capabilities.yaml`. Add it there first if
      genuinely new — and check it is not an existing capability under another name.
- [ ] **Applicability references only closed-vocabulary fields** from the Workload
      Profile in `SKILL.md` §2.
- [ ] **Applicability never references `ownership` or `existing_controls`.** Those
      decide *who satisfies* a control, not *whether it applies*. Putting them in
      applicability destroys the DELEGATED outcome and erases the record that the
      control matters.
- [ ] **Enforcement default is justified.** BLOCK means delivery genuinely should stop.
      Reserve it for controls where shipping past a finding is the wrong outcome.
- [ ] **At least one framework mapping** — SSDF, SLSA, OWASP CI/CD, OWASP SAMM, or CNCF.
- [ ] **At least one curriculum module**, and it must exist in
      `references/dsb-curriculum.yaml`.
- [ ] **Tooling examples are plural and vendor-neutral.** Never one product.
- [ ] `python tools/validate_skill.py` passes.
- [ ] `python tools/generate_mappings.py` re-run, and the result committed.

### Applicability, precisely

Applicability answers one question: **does this risk exist for this workload?**

It is evaluated with three-valued logic, so state predicates in terms that can come
back TRUE, FALSE, or UNKNOWN. A rule that can never be FALSE is a rule that will be
recommended to everyone, which is the checklist thinking this methodology rejects.

Ask yourself: *what workload would make this rule Not Applicable?* If you cannot
answer, the rule is probably too broad.

---

## Changing the methodology

The four phases, the twenty baseline principles, and the enforcement model come from
DSB curriculum. They are not changed through pull requests to this repository — open
an issue in
[devsecblueprint/devsecblueprint](https://github.com/devsecblueprint/devsecblueprint)
instead.

This skill implements DSB teaching. It is not the source of it, and it must never
diverge from it.

---

## Generated files

`references/framework-mappings.md` is generated from the mappings lines in `SKILL.md`.
Do not edit it by hand:

```bash
python tools/generate_mappings.py           # rewrite it
python tools/generate_mappings.py --check   # exit 1 if it is out of date
```

`tests/test_mappings.py` fails when the committed file drifts, so a rule change that
touches mappings will fail CI until it is regenerated.

The YAML files under `rules/` are a partial projection of the catalog with a
deliberately limited scope — read [`rules/README.md`](rules/README.md) before adding
to them.

---

## Refreshing the curriculum snapshot

`references/dsb-curriculum.yaml` mirrors `frontend/lib/curriculum-data.ts` from the
platform repository. It is refreshed manually so this repository stays self-contained
with no cross-repository CI coupling.

When the curriculum changes:

1. Read the current `CURRICULUM_STAGES` in the platform repo.
2. Update stage and module IDs and names here. **Quote every name** — several contain
   `?`, which YAML flow mappings reject.
3. Update `snapshot_date`.
4. Run `python tools/validate_skill.py` — it fails if any rule cites a module that no
   longer exists.

---

## Keeping SKILL.md loadable

`SKILL.md` is the entire product. A user should need nothing else.

- **No references to other files in this repository.** No relative links, no "see
  `references/…`". If a user copies `SKILL.md` alone, it must be complete.
- **Keep tables narrow.** Agent output is often read in an 80-column terminal. Wide
  tables render as unreadable overlapping text.
- **Watch the size.** Every invocation loads the whole file. Prefer tightening existing
  prose over appending.

An installed skill directory must contain `SKILL.md` and nothing else:

```bash
ls ~/.claude/skills/dsb-devsecops/
```

Anything alongside it is a file a user would also have to download, which breaks the
distribution model.

---

## Pull requests

- One logical change per PR. A new rule family is several PRs, not one.
- Explain the engineering reasoning, not just what changed.
- Note any behavior change you observed when testing against a live agent.
- CI must pass.

---

## Questions

Open an issue, or ask in the [DSB Discord](https://discord.gg/enMmUNq8jc).
