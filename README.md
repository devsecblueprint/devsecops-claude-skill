# DSB DevSecOps Engineering Skill

An AI-agent skill implementing The DevSec Blueprint's DevSecOps engineering
methodology. It advises on, designs, generates, and reviews CI/CD delivery pipelines.

> **Build what you need. Test what you built. Scan what can introduce meaningful
> risk. Deploy only what passed.**

**The DevSec Blueprint defines the required capabilities and engineering outcomes.
Your organization determines how those capabilities are implemented.**

---

## Licensing

PolyForm Noncommercial License 1.0.0.

**Commercial use requires prior written authorization from The DevSec Blueprint LLC.**
See [Commercial Licensing](docs/legal/COMMERCIAL-LICENSING.md).

Free for noncommercial use — learning, personal projects, and evaluation. If you want
to use this inside a company, start with the commercial licensing process.

The license covers the software in this repository only. It grants no rights to DSB
curriculum, walkthroughs, training materials, name, logos, or other branded assets.
See [Trademarks](docs/legal/TRADEMARKS.md).

---

## Install

The entire skill is one file. There is nothing to build and no dependencies.

**Claude Code:**

```bash
mkdir -p ~/.claude/skills/dsb-devsecops
curl -o ~/.claude/skills/dsb-devsecops/SKILL.md \
  https://raw.githubusercontent.com/devsecblueprint/devsecops-claude-skill/main/SKILL.md
```

Restart your agent, then ask it to design or review a pipeline. It loads on its own
when the topic matches — you do not need to name it.

**Other agents:** drop `SKILL.md` wherever your tool loads instructions from, or paste
its contents into the system prompt. It is plain Markdown with YAML frontmatter and no
external references.

---

## What it does

Three operating modes, all driven by the same reasoning procedure so they cannot
contradict each other:

| Mode | Use when |
|---|---|
| **Advise** | You describe your stack and constraints and want architecture guidance |
| **Design** | You want implementation-ready pipeline configuration |
| **Review** | You have a pipeline, workflow, or repository to assess against DSB requirements |

Repository access is never required. Given partial context it produces a partial plan
plus the specific questions it needs answered — it does not guess.

### Capability-based, not vendor-based

DSB requires Software Composition Analysis. It does not require Snyk, Black Duck,
Dependabot, or Trivy.

If you already have a capability, the skill **uses it** rather than recommending a
replacement:

```
Required capability:  Software Composition Analysis
Existing tool:        Black Duck
Decision:             REUSE — Black Duck satisfies this in the Scan phase
DSB requirement:      Satisfied
```

Tool names anywhere in this repository are illustrative examples. Presenting one as a
DSB requirement is a defect.

### No bloat

Controls are workload-driven, not checklist-driven:

- No container scanner when there is no container artifact
- No IaC scanner when there is no infrastructure-as-code
- No Kubernetes scanner when Kubernetes is not used
- No second SCA scanner when one already covers it

`Not Applicable` is a valid engineering outcome and is always stated with its reason.

---

## The methodology

```
BUILD → TEST → SCAN → DEPLOY
```

Logical engineering phases — not a mandated job structure, vendor, or platform.
Runtime-dependent controls such as DAST execute after deployment to a non-production
environment; that is a placement decision inside Scan, not a fifth phase.

The full methodology, the twenty baseline principles, and the rule catalog are in
[`SKILL.md`](SKILL.md).

---

## Rule catalog

42 rules across 11 families, each mapped to recognized industry guidance — NIST SSDF,
SLSA, OWASP CI/CD Security, OWASP SAMM, and CNCF supply chain guidance — and to the
DSB curriculum modules that teach the underlying concept.

| Family | Covers |
|---|---|
| `DSB-BUILD` | Build and artifact creation |
| `DSB-TEST` | Testing requirements |
| `DSB-SCAN` | Security scanning and validation |
| `DSB-IAC` | Infrastructure-as-code security |
| `DSB-SRC` | Source control security |
| `DSB-SC` | Software supply chain |
| `DSB-ART` | Artifacts, provenance, signing, registries |
| `DSB-DEPLOY` | Deployment and promotion |
| `DSB-ID` | Workload identity, authentication, authorization |
| `DSB-EVD` | Evidence, logging, observability |
| `DSB-EXC` | Exceptions and risk acceptance |

Rule IDs are permanent. A deprecated rule keeps its number forever, because IDs appear
in review output that ends up in audit records.

The rules are defined in [`SKILL.md`](SKILL.md) §3. To go the other way — from an SSDF
practice, SLSA level, or OWASP CI/CD risk to the DSB rules that carry it — see
[`references/framework-mappings.md`](references/framework-mappings.md).

---

## Repository contents

| Path | Purpose |
|---|---|
| `SKILL.md` | **The skill.** Self-contained — this is all a user needs |
| `examples/` | Worked scenarios and reference pipelines across four stacks |
| `rules/` | Machine-readable projection of the catalog — see [`rules/README.md`](rules/README.md) |
| `references/capabilities.yaml` | Machine-readable capability registry |
| `references/dsb-curriculum.yaml` | Curriculum index snapshot, for validating citations |
| `references/framework-mappings.md` | Framework-first index — generated, not hand-edited |
| `schema/` | JSON Schemas for the rule and workload-profile structures |
| `tools/validate_skill.py` | Consistency checks, run in CI |
| `tools/generate_mappings.py` | Regenerates the framework mapping index |
| `docs/legal/` | Licensing, trademark, and contributor terms |

[CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) ·
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) · [MAINTAINERS.md](MAINTAINERS.md)

---

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -r tools/requirements.txt

python tools/validate_skill.py     # consistency checks
python -m pytest                   # test suite
```

Install your working copy locally and iterate:

```bash
mkdir -p ~/.claude/skills/dsb-devsecops
cp SKILL.md ~/.claude/skills/dsb-devsecops/

ls ~/.claude/skills/dsb-devsecops/   # SKILL.md and nothing else
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

---

## Status

Advise, Design, and Review modes are implemented, with worked
[examples](examples/) for each — including complete rule-annotated reference
pipelines for GitHub Actions and Jenkins.

Related: [devsecblueprint#180](https://github.com/devsecblueprint/devsecblueprint/issues/180).

---

## Maintained by

The DevSec Blueprint. See [MAINTAINERS.md](MAINTAINERS.md) and join the
[Discord](https://discord.gg/enMmUNq8jc).
