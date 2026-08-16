# DSB DevSecOps Engineering Skill

**Turn a description of your stack into a delivery pipeline with the right security
controls in the right places — and no scanners you did not need.**

By [The DevSec Blueprint](https://github.com/devsecblueprint) · MIT ·
**v0.1.0 (pre-1.0)**

> Build what you need. Test what you built. Scan what can introduce meaningful risk.
> Deploy only what passed.

---

## Contents

- [What is this?](#what-is-this)
- [Why use it](#why-use-it)
- [Install in 60 seconds](#install-in-60-seconds)
- [Try it](#try-it)
- [Common workflows](#common-workflows)
- [How it works](#how-it-works)
  - [The rule catalog](#the-rule-catalog)
- [Documentation](#documentation)
  - [Repository contents](#repository-contents)
- [Development](#development)
- [Status](#status)
- [License and ownership](#license-and-ownership)

---

## What is this?

A skill for AI coding agents that encodes how The DevSec Blueprint teaches DevSecOps
engineering. Give it your stack — or point it at a pipeline you already have — and it
reasons from a fixed rule catalog to a **Control Plan**: which security controls apply
to *this* workload, which are already covered by tools you own, where each one belongs
in the pipeline, and whether it should block delivery or just report.

It is not a pipeline generator with a scanner list bolted on. It decides what applies
before it writes anything.

**DSB defines the required capabilities and engineering outcomes. Your organization
determines how those capabilities are implemented.**

---

## Why use it

**It reuses what you already own.** Tell it you have Checkmarx and Black Duck and it
resolves SAST and SCA to *satisfied*, by name, and moves on. It does not propose Snyk
alongside Black Duck. Zero new scanners is a correct answer, and the most common one
in an enterprise.

**It says what does not apply, and why.** A Terraform-only repository gets container
scanning marked Not Applicable with the stated fact that produced it — not silently
dropped, and not recommended "to be safe". Twelve explicit N/A determinations are the
deliverable, not filler.

**It asks instead of assuming.** Partial context produces a partial plan plus the
specific unresolved fields, phrased as questions. It does not infer that you build
containers because you mentioned Java.

**It explains the engineering.** Every recommendation carries a rule ID, the reason
that placement is the earliest technically valid one, and whether the enforcement
level came from DSB or from your own policy.

**It refuses the dangerous default.** Active DAST against production requires explicit
authorization. Unknown is treated as no.

---

## Install in 60 seconds

**As a skill** — one file, no dependencies, works in any agent that loads Markdown
instructions:

```bash
mkdir -p ~/.claude/skills/dsb-devsecops
curl -o ~/.claude/skills/dsb-devsecops/SKILL.md \
  https://raw.githubusercontent.com/devsecblueprint/devsecops-claude-skill/main/SKILL.md
```

Restart your agent. It loads on its own when the topic matches — you never name it.

**As a Claude Code plugin**, if you also want the `/devsecops-engineer:*` commands:

```bash
/plugin install devsecblueprint/devsecops-claude-skill
```

**Any other agent:** drop `SKILL.md` wherever your tool loads instructions from, or
paste it into the system prompt. Plain Markdown with YAML frontmatter, no external
references.

---

## Try it

Three prompts, one per operating mode. Slash commands are shown where the plugin is
installed; the plain-language version does the same thing with the skill alone.

**Advise — where do controls belong, given what we already own?**

```
/devsecops-engineer:advise We use Jenkins, Java, Maven, Artifactory, Checkmarx,
Black Duck, Prisma Cloud, and OpenShift. How should our pipeline be designed?
```

You should get Checkmarx → SAST, Black Duck → SCA, Prisma → container scanning, all
resolved as reuse; SBOM generation flagged as a real gap; and questions about the
things it genuinely cannot know. Compare with
[`examples/generate-jenkins/`](examples/generate-jenkins/).

**Design — give me the pipeline.**

```
/devsecops-engineer:design A Node.js service that builds a container and deploys to
AWS ECS. Terraform for infrastructure, staging and production.
```

Container scan before push, deploy by digest, OIDC instead of static keys, actions
pinned to SHAs, DAST against staging only. Compare with
[`examples/generate-github-actions/delivery.yml`](examples/generate-github-actions/delivery.yml).

**Assess — what is wrong with the pipeline we have?**

```
/devsecops-engineer:assess .github/workflows/deploy.yml
```

Findings ordered by what an attacker reaches first. Compare with
[`examples/review-non-compliant/`](examples/review-non-compliant/).

---

## Common workflows

| You want to… | Do this |
|---|---|
| Decide which scanners a new service actually needs | Advise with your stack and existing tools |
| Justify *not* buying another scanner | Advise — the reuse resolution names the tool that already covers it |
| Stand up a pipeline for a new repository | Design, after answering the platform/language/target questions |
| Audit a pipeline you inherited | Assess, pointed at the workflow file |
| Prepare for an SSDF or SLSA conversation | Assess, then [`docs/framework-mappings.md`](docs/framework-mappings.md) |
| Explain a control to a team that pushed back | Ask why a rule exists — every rule carries its engineering reason |

---

## How it works

All three modes run the same procedure and produce the same intermediate artifact, so
Advise, Design, and Assess cannot disagree about what applies to a workload.

```
Your description, a pipeline file, a repository, or any mix
        ↓
1. WORKLOAD PROFILE      only stated facts; everything else is `unknown`
        ↓
2. APPLICABILITY         each rule → APPLIES | NOT APPLICABLE (+reason) | UNKNOWN (+question)
        ↓
3. CAPABILITY RESOLUTION reuse existing | delegated elsewhere | gap | duplicate
        ↓
4. ENFORCEMENT + PLACEMENT   block/warn/report, at the earliest valid phase
        ↓
   ══ CONTROL PLAN ══
        ↓
 Advise (explain)    Design (render)    Assess (diff against what exists)
```

Everything you did not state is `unknown`, which is what lets it work without
repository access — and what turns the unresolved fields into its questions instead
of its assumptions.

The four phases:

```
BUILD → TEST → SCAN → DEPLOY
```

Logical engineering phases, not a mandated job structure. One GitHub Actions job can
satisfy all four; twelve Jenkins stages can satisfy the same four. Runtime-dependent
controls such as DAST run after deployment to a non-production environment — that is a
placement decision inside Scan, not a fifth phase.

### The rule catalog

42 rules across 11 families, each mapped to NIST SSDF, SLSA, OWASP CI/CD Security,
OWASP SAMM, and CNCF supply chain guidance, and to the DSB curriculum modules that
teach the concept.

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

Rules require **capabilities, never vendors**. Every product name in this repository
is illustrative; presenting one as a DSB requirement is a defect. Your internal or
proprietary tools satisfy rules with no rule changes — declare them against the
capability they provide.

Rule IDs are permanent. A retired rule keeps its number forever, because IDs end up in
audit records.

---

## Documentation

**Start here**

| Document | What it covers |
|---|---|
| [`SKILL.md`](SKILL.md) | The skill itself — methodology, twenty baseline principles, all 42 rules, and the three operating modes |
| [`examples/`](examples/) | Worked scenarios across four stacks, including two complete reference pipelines |
| [`CHANGELOG.md`](CHANGELOG.md) | What shipped in each release, and what pre-1.0 means for stability |

**In [`docs/`](docs/)**

| Document | What it covers |
|---|---|
| [`docs/framework-mappings.md`](docs/framework-mappings.md) | Framework-first index: an SSDF practice, SLSA level, or OWASP CI/CD risk → the DSB rules that carry it. Generated from `SKILL.md`, never hand-edited |
| [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) | How to add or change a rule, the vendor-neutrality constraint, the commands-stay-thin policy, and how to refresh the curriculum snapshot |
| [`docs/TESTING.md`](docs/TESTING.md) | The two testing layers — automated consistency checks, and the behavioral tests that prove a change actually moved agent behavior |
| [`docs/MAINTAINERS.md`](docs/MAINTAINERS.md) | Ownership, maintainer responsibilities, and the review and release rules |
| [`docs/SECURITY.md`](docs/SECURITY.md) | How to report a vulnerability, and what counts as one in a repository that ships guidance rather than a running service |
| [`docs/CODE_OF_CONDUCT.md`](docs/CODE_OF_CONDUCT.md) | Community standards, including where vendor advocacy stops being a technical discussion |

**Legal, in [`docs/legal/`](docs/legal/)**

| Document | What it covers |
|---|---|
| [`LICENSE.md`](LICENSE.md) | MIT. Commercial use permitted, no separate authorization |
| [`docs/legal/TRADEMARKS.md`](docs/legal/TRADEMARKS.md) | DSB names, logos, and curriculum sit outside the MIT license — what you may and may not call your fork |
| [`docs/legal/CLA.md`](docs/legal/CLA.md) | Contributor License Agreement covering the rights you grant when you submit a change |

### Repository contents

| Path | Purpose |
|---|---|
| `SKILL.md` | **The skill.** Self-contained — this is all a user needs |
| `commands/` | `/devsecops-engineer:*` entry points — thin wrappers over `SKILL.md` |
| `examples/` | Worked scenarios and reference pipelines across four stacks |
| `rules/` | Machine-readable projection of the catalog — see [`rules/README.md`](rules/README.md) |
| `references/` | Capability registry and DSB curriculum snapshot |
| `schema/` | JSON Schemas for the rule and workload-profile structures |
| `tools/` | Consistency checks and the mapping-index generator, both run in CI |
| `docs/` | Contributing, testing, project policy, and framework mappings |

---

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -r tools/requirements.txt

python tools/validate_skill.py     # consistency checks
python -m pytest                   # test suite
```

Install your working copy and iterate:

```bash
mkdir -p ~/.claude/skills/dsb-devsecops
cp SKILL.md ~/.claude/skills/dsb-devsecops/
ls ~/.claude/skills/dsb-devsecops/   # SKILL.md and nothing else
```

A `SKILL.md` change that reads well but does not change agent behavior has not landed.
[`docs/TESTING.md`](docs/TESTING.md) covers how to verify that; read
[`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) before opening a pull request.

---

## Status

**v0.1.0 — pre-1.0.** All three modes are implemented, with worked examples for each
and complete rule-annotated reference pipelines for GitHub Actions and Jenkins.

The catalog and output structure will evolve based on real usage before 1.0. Rule IDs
are already stable. See [`CHANGELOG.md`](CHANGELOG.md).

Feedback from real pipelines is the most useful thing you can contribute right now —
open an issue or bring it to the [Discord](https://discord.gg/enMmUNq8jc).

Related: [devsecblueprint#180](https://github.com/devsecblueprint/devsecblueprint/issues/180).

---

## License and ownership

MIT — see [`LICENSE.md`](LICENSE.md). Commercial use is permitted, no separate
authorization required.

The license covers the software in this repository. It grants no rights to DSB
curriculum, walkthroughs, training materials, names, logos, or other branded assets —
see [Trademarks](docs/legal/TRADEMARKS.md).

Owned and maintained by The DevSec Blueprint. This skill implements DSB knowledge; it
is not the source of that knowledge. Where the skill and the curriculum disagree, the
curriculum wins and the skill is a defect.

[Contributing](docs/CONTRIBUTING.md) · [Testing](docs/TESTING.md) ·
[Security](docs/SECURITY.md) · [Code of Conduct](docs/CODE_OF_CONDUCT.md) ·
[Maintainers](docs/MAINTAINERS.md) · [Changelog](CHANGELOG.md)
