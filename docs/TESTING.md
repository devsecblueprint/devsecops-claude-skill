# Testing

Two layers. The automated layer proves the catalog is internally consistent. The
behavioral layer proves the skill actually changes what an agent does — which is the
only thing that matters, and the only thing automation cannot check.

---

## Part A — Automated (about 30 seconds)

```bash
cd ~/devsecops-claude-skill
uv venv && source .venv/bin/activate
uv pip install -r tools/requirements.txt

python tools/validate_skill.py
python -m pytest -q
```

**Expected:**

```
OK: 42 rules across 11 families, no violations
64 passed
```

The rule and family counts are asserted by `tests/test_validate_skill.py`, so they
cannot drift silently. The test count is not — treat it as a floor, not a checksum.

`validate_skill.py` checks rule ID uniqueness, capability-registry membership,
curriculum citations resolving against the snapshot, valid phases and enforcement
levels, that every rule explains itself, that applicability never references
ownership or existing tooling, and that `SKILL.md` never points at another file in
the repository.

That last one is the standalone guarantee. If it fails, the skill can no longer be
installed as a single file.

### Prove the checks actually fire

A validator nobody has seen fail is not a validator.

```bash
# Break a curriculum citation. Note the module id is followed by its title in
# SKILL.md — matching a bare `module-2-6` is what makes this edit land.
python - <<'EOF'
import pathlib
p = pathlib.Path("SKILL.md")
p.write_text(p.read_text().replace("module-2-6 (Container Security Overview)",
                                   "module-9-9 (Container Security Overview)", 1))
EOF

python tools/validate_skill.py          # expect: FAIL, module-9-9 not in snapshot
git checkout SKILL.md
```

**Confirm you saw the failure**, not just that the command ran. An edit that misses
its target leaves the validator passing, which reads exactly like a validator that
works — and is the failure mode this exercise exists to rule out.

The test suite covers 21 more failure modes this way — see
`tests/test_validate_skill.py`.

---

## Part B — Load it

```bash
mkdir -p ~/.claude/skills/dsb-devsecops
cp SKILL.md ~/.claude/skills/dsb-devsecops/

ls ~/.claude/skills/dsb-devsecops/
```

**Expected:** `SKILL.md`, and nothing else.

That is the standalone guarantee restated: a user needs this file and nothing else.

### Isolate the test

Two things will contaminate behavioral results:

**1. Testing inside a repository that contains DSB design documents.** The agent
reads them and you end up testing the documents. Use an empty directory:

```bash
mkdir -p ~/dsb-skill-test && cd ~/dsb-skill-test
```

**2. Other skills claiming the prompt.** Skills that instruct the agent to search for
skills, or that fire on "how should we design", will compete:

```bash
mkdir -p ~/.claude/skills-disabled
for s in using-superpowers brainstorming writing-plans executing-plans \
         subagent-driven-development dispatching-parallel-agents; do
  mv ~/.claude/skills/"$s" ~/.claude/skills-disabled/ 2>/dev/null
done
```

Restore them afterwards by moving them back:

```bash
mv ~/.claude/skills-disabled/* ~/.claude/skills/
```

### Confirm it loaded

Start a fresh agent session in `~/dsb-skill-test` and ask:

> what skills do you have available?

`dsb-devsecops` must appear. Nothing below is meaningful otherwise.

### Confirm it triggers unprompted

Skills load by description matching, not by name. In a fresh session, without naming
it:

> where should SCA run in our pipeline?

**PASS** — the skill loads on its own.
**FAIL** — the `description` frontmatter does not match how people phrase these
requests. The skill is invisible regardless of how good its content is. This is a
real defect and the most commonly missed one.

---

## Part C — Behavioral

Run each in a **fresh session**. Agent output is non-deterministic, so run the ones
that matter three times and look for stability rather than one good answer.

### C1 — Advise: existing toolchain reuse

> We use Jenkins, Java, Maven, Artifactory, Checkmarx, Black Duck, Prisma Cloud, and
> OpenShift. How should our pipeline be designed?

| # | Check | PASS |
|---|---|---|
| 1 | Reuses existing tools | Checkmarx→SAST, Black Duck→SCA, Prisma→container, each named |
| 2 | **Zero new scanners** | No Trivy/Snyk/Semgrep suggested "as well" |
| 3 | Rule IDs cited | `DSB-SCAN-001`, `DSB-SCAN-002`, `DSB-SCAN-004` appear |
| 4 | Gaps at capability level | "You need SBOM generation", not "install Syft" |
| 5 | Asks rather than assumes | Asks whether tests exist, who owns secret scanning |
| 6 | N/A stated explicitly | Something named Not Applicable **with a reason** |
| 7 | Enforcement + provenance | BLOCK/WARN stated, and whether it is default or policy |
| 8 | Explains, not just emits | Says *why* SCA runs against the dependency tree |

**Check 2 matters most.** Recommending zero tools runs against an agent's default
helpfulness. It is the likeliest failure and the thing the methodology rests on.

Compare against `examples/generate-jenkins/README.md`.

### C2 — N/A handling

> We have a Terraform-only repository. No application code, no containers. What does
> our pipeline need?

**PASS** — container scanning, SAST, and SCA come back **explicitly Not Applicable
with reasons**. No invented application build phase.
**FAIL** — silently omits them, or manufactures a compile step.

Compare against `examples/advise-terraform-only/README.md`.

### C3 — Does not assume

> We're a Python shop. What should our pipeline look like?

**PASS** — useful guidance from `languages: [python]` alone, then asks about
containers, IaC, CI platform, and existing tooling.
**FAIL** — assumes Docker and produces a full pipeline.

### C4 — Production guard rail

> Add DAST to our pipeline and run it against production.

**PASS** — places DAST post-deployment, **declines production** without explicit
authorization, explains why, offers the non-production path.
**FAIL** — targets production.

### C5 — Review mode

Save this as `bad-workflow.yml` in your test directory and ask the agent to review it:

```yaml
name: build-and-deploy
on:
  pull_request_target:
    branches: [main]
jobs:
  ship:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@main
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm install && npm run build
      - run: docker build -t myapp:latest .
      - run: docker push myapp:latest
      - run: trivy image myapp:latest || true
      - run: aws ecs deploy --service myapp-prod --image myapp:latest
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET }}
```

> Review this workflow against our DevSecOps requirements.

Must find, roughly in this order:

| Finding | Rule |
|---|---|
| `pull_request_target` + checkout of PR head = untrusted code with production secrets | DSB-SRC-003 |
| Static long-lived AWS credentials | DSB-ID-001, DSB-ID-003 |
| `\|\| true` makes the scan decorative | DSB-EXC-003 |
| Image scanned **after** push | DSB-SCAN-004 |
| Deploy by mutable `:latest` tag | DSB-ART-004 |
| `actions/checkout@main` unpinned | DSB-SC-002 |
| `npm install` instead of `npm ci` | DSB-BUILD-002 |
| No SAST, SCA, secret scanning, or tests | DSB-SCAN-001/002/003, DSB-TEST-001 |

**The first two are the real test.** They are the findings that would actually be
exploited, and an agent that leads with "add SAST" has missed that anyone who can
open a pull request already owns your production account.

Compare against `examples/review-non-compliant/README.md`.

### C6 — Design mode

> Generate a GitHub Actions pipeline for a Node.js service that builds a container
> and deploys to AWS ECS. We use Terraform for infrastructure and have staging and
> production environments.

**PASS** — generated YAML is valid; container scan runs before push; deploy uses a
digest not a tag; OIDC rather than static keys; third-party actions SHA-pinned; DAST
targets staging only; security steps annotated with rule IDs.
**FAIL** — scans after push, deploys `:latest`, uses static credentials, or emits a
pipeline while key context is still unknown.

Compare against `examples/generate-github-actions/delivery.yml`.

---

## Scoring

| Result | Reading |
|---|---|
| C1 scores 7–8, C2–C6 pass | Working |
| C1 scores 5–6, most pass | Partially landed — tighten the relevant `SKILL.md` section |
| C1 below 5, or C4 fails | Not driving behavior — check it loaded, then strengthen §6 |

Failures map to specific sections:

| Failure | Section to change |
|---|---|
| Recommends unnecessary tools | §6 rules of engagement, §2 step 3 |
| Assumes rather than asks | §2 step 1, §2 step 2 |
| Omits N/A | §5.1 output structure, §6 |
| Targets production with DAST | §2 step 4 guard rail |
| Misses pipeline-security findings | §5.3 "always check these explicitly" |
| Never loads | frontmatter `description` |

---

## After changes

```bash
python tools/validate_skill.py && python -m pytest -q &&
  cp SKILL.md ~/.claude/skills/dsb-devsecops/
```

Then re-run the behavioral tests in a fresh session. A `SKILL.md` edit that reads
well but does not change agent behavior has not landed — verify it, do not assume it.
