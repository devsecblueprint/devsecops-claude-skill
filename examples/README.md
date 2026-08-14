# Examples

Worked scenarios across different organizational stacks, covering compliant,
non-compliant, and Not Applicable outcomes.

| Example | Mode | Stack | Demonstrates |
|---|---|---|---|
| [`generate-github-actions/`](generate-github-actions/) | Design | Node.js, container, Terraform, AWS ECS, GitHub Actions | Greenfield — every capability is a gap, full control set implemented |
| [`generate-jenkins/`](generate-jenkins/) | Design | Java, Maven, Artifactory, OpenShift, Jenkins | **Existing toolchain reuse** — three capabilities satisfied by tools already owned, zero new scanners |
| [`review-non-compliant/`](review-non-compliant/) | Review | GitHub Actions | Findings on a pipeline with real defects, ordered by exploitability |
| [`advise-terraform-only/`](advise-terraform-only/) | Advise | Terraform, GitLab CI | **N/A handling** — twelve rules explicitly do not apply |

## Reading them in order

The two Design examples are deliberately opposite cases.

**GitHub Actions** is greenfield: no existing security products, so every applicable
capability resolves to a GAP and gets implemented. It shows the complete control set.

**Jenkins** is the common enterprise case: Checkmarx, Black Duck, and Prisma Cloud
are already owned, so three capabilities resolve to REUSE and **no additional scanner
is introduced.** The interesting property of that output is what it does not contain.

**Terraform-only** shows the other half of workload-driven selection. Twelve baseline
rules are Not Applicable, each with the stated fact that produced it. A skill that
recommended container scanning here would be producing the checklist-driven bloat
this methodology exists to prevent.

**Non-compliant review** shows Review mode against a pipeline with defects that are
common in the wild — `pull_request_target` with secret access, a scanner neutralized
by `|| true`, deployment by mutable tag.

## A note on the tools named in these examples

Every product name is illustrative. DSB requires **capabilities**, never vendors.

If your organization already has a capability, use it — that is what the Jenkins
example demonstrates. Presenting any tool in these files as a DSB requirement is a
defect.

## A note on pinning

The GitHub Actions example pins third-party actions to commit SHAs, per DSB-SC-002.
Those SHAs correspond to the tagged versions in their comments at time of writing;
re-verify before adopting. Scanner container images are pinned by version tag for
readability — pin by digest in production.
