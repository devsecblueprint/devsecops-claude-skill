# Example — Advise: Terraform-only repository

The N/A-heavy case. Most baseline controls do not apply, and saying so explicitly is
the correct output.

## Input

> We have a Terraform-only repository that manages our AWS accounts. No application
> code, no containers. It runs through GitLab CI. What does our pipeline need?

## Workload profile

```yaml
source:            { host: gitlab }
languages:         []                       # stated: no application code
package_managers:  []
artifacts:         { container: false, package: false, binary: false,
                     iac_plan: true, helm_chart: false }
iac:               { present: true, tools: [terraform] }
runtime:           { kubernetes: false, serverless: false, vm: true, paas: false }
deploy:            { targets: [aws], environments: unknown, promotion_model: unknown }
cicd:              { platform: gitlab-ci, runners: unknown }
identity:          { mechanism: unknown }
testing:           { unit: unknown, infrastructure: unknown }
policy:            { enforcement_posture: unknown }
```

"No application code, no containers" is a **stated** fact, not an inference. That is
what makes confident N/A determinations possible here.

## Build → Test → Scan → Deploy

The four phases still apply. They express differently.

**Build** — `terraform plan` produces the deployment artifact. That plan *is* the
build output, and it is what everything downstream should validate and apply. This is
a complete and correct Build phase; there is no compilation step to invent.

**Test** — `terraform validate`, format checks, and any module tests (DSB-TEST-002).

**Scan** — IaC static analysis and policy-as-code (DSB-IAC-001, DSB-IAC-003), plus
secret scanning (DSB-SCAN-003).

**Deploy** — `terraform apply` against a reviewed plan (DSB-IAC-004).

## Applicable

| Rule | Capability | Enforcement |
|---|---|---|
| DSB-IAC-001 | `iac-scanning` | BLOCK (default) |
| DSB-IAC-003 | `policy-as-code-enforcement` | WARN (default) |
| DSB-IAC-004 | `deployment-gating` | BLOCK (default) |
| DSB-TEST-002 | `automated-testing` | BLOCK (default) |
| DSB-SCAN-003 | `secret-scanning` | BLOCK (default) |
| DSB-SCAN-005 | `pipeline-configuration-scanning` | WARN (default) |
| DSB-SRC-001 | `source-control-hardening` | BLOCK (default) |
| DSB-SRC-002 | `source-control-hardening` | BLOCK (default) |
| DSB-SC-002 | `pipeline-configuration-scanning` | BLOCK (default) |
| DSB-BUILD-001 | `build-traceability` | BLOCK (default) |
| DSB-EVD-001 | `pipeline-evidence-retention` | REPORT (default) |
| DSB-EVD-002 | `pipeline-evidence-retention` | REPORT (default) |
| DSB-EXC-003 | `pipeline-configuration-scanning` | BLOCK (default) |

Secret scanning matters more here than in a typical application repository, not less
— Terraform repositories accumulate provider credentials, connection strings, and
occasionally state fragments.

## Not applicable

Each with the stated fact that produced it:

| Rule | Reason |
|---|---|
| DSB-SCAN-001 (SAST) | `languages` is empty — no first-party application code to analyse |
| DSB-SCAN-002 (SCA) | no application package manager — no dependency tree |
| DSB-SCAN-004 (container scanning) | `artifacts.container` is false — no image exists |
| DSB-SCAN-006 (DAST) | no running application surface this repository produces |
| DSB-SCAN-007 (API testing) | no API surface produced |
| DSB-SCAN-008 (licensing) | no application dependencies to license-check |
| DSB-IAC-002 (Kubernetes config) | `runtime.kubernetes` is false, no Helm chart |
| DSB-BUILD-002 (dependency pinning) | no application package manager; Terraform provider pinning is covered by DSB-IAC-001 tooling |
| DSB-BUILD-003 (SBOM) | no application artifact to describe |
| DSB-TEST-001 (application tests) | no application code; DSB-TEST-002 covers infrastructure validation |
| DSB-ART-001–004 (artifacts) | no published artifact — the plan is applied, not published |
| DSB-DEPLOY-002 (promote not rebuild) | Terraform re-plans per environment by design; there is no artifact to promote |

**Twelve rules do not apply.** Listing them is the deliverable, not filler — it is the
difference between a considered engineering decision and an omission. It also
pre-empts an auditor asking why there is no container scanning.

A skill that recommended container scanning, SAST, and SBOM generation here would be
producing exactly the checklist-driven bloat this methodology exists to prevent.

## Undetermined

Not N/A — genuinely unknown, and neither implemented nor dismissed:

- **DSB-ID-001, DSB-ID-002, DSB-ID-004** — how does GitLab CI authenticate to AWS?
  This is the highest-value unanswered question here. A Terraform pipeline holds
  account-wide privileges by nature, so its identity mechanism matters more than in
  most application pipelines.
- **DSB-DEPLOY-003** — is there a non-production account to apply against first?
- **DSB-EXC-001** — is there an exception process for accepted findings?

## What I need to know

1. How does the pipeline authenticate to AWS — static access keys, OIDC federation,
   or an assumed role? (DSB-ID-001)
2. Do you apply to a non-production account before production? (DSB-DEPLOY-003)
3. Where is Terraform state stored, and is access to it restricted? State frequently
   contains secrets in plaintext.
4. Do you already own an IaC scanning or cloud posture capability? Many
   organizations have one through an existing cloud security platform — if so,
   DSB-IAC-001 resolves to REUSE rather than a gap. (DSB-IAC-001)
5. What is your enforcement posture — should a HIGH IaC finding block the apply, or
   warn? (Determines real BLOCK/WARN levels)
6. Is there a policy-as-code capability in use, or would that be new? (DSB-IAC-003)

## Curriculum

Relevant DSB modules: module-3-7 (IaC Security), module-3-2 (IAM Fundamentals),
module-3-4 (Secrets Management In The Cloud).
