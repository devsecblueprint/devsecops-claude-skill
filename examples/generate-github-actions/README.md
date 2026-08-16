# Example — Design/Generate: Node.js service on GitHub Actions

A complete, rule-annotated delivery pipeline generated from a workload profile.
See [`delivery.yml`](delivery.yml).

## Workload profile

```yaml
source:            { host: github, protected_branches: true, review_required: true }
languages:         [javascript]
package_managers:  [npm]
artifacts:         { container: true, package: false }
iac:               { present: true, tools: [terraform] }
runtime:           { vm: false, paas: true }          # AWS ECS
deploy:            { targets: [aws-ecs], environments: [staging, production],
                     promotion_model: promote }
cicd:              { platform: github-actions, runners: hosted }
identity:          { mechanism: oidc }
testing:           { unit: true, integration: true }
existing_controls: {}                                  # greenfield
policy:            { enforcement_posture: strict, dast_prod_authorized: false }
```

Nothing here is inferred. Every field was stated by the requester.

## Control Plan

| Rule | Capability | Resolution | Phase | Enforcement |
|---|---|---|---|---|
| DSB-BUILD-001 | `build-traceability` | GAP → implemented | build | BLOCK (default) |
| DSB-BUILD-002 | `dependency-resolution-control` | GAP → `npm ci` | build | BLOCK (default) |
| DSB-BUILD-003 | `sbom-generation` | GAP → CycloneDX | build | WARN (default) |
| DSB-BUILD-004 | `build-environment-isolation` | SATISFIED by hosted runners | build | WARN (default) |
| DSB-TEST-001 | `automated-testing` | GAP → unit + integration | test | BLOCK (default) |
| DSB-TEST-002 | `automated-testing` | GAP → `terraform validate` | test | BLOCK (default) |
| DSB-SCAN-001 | `sast` | GAP → SAST scanner | scan | BLOCK (default) |
| DSB-SCAN-002 | `software-composition-analysis` | GAP → dependency audit | scan | BLOCK (default) |
| DSB-SCAN-003 | `secret-scanning` | GAP → history scan | scan | BLOCK (default) |
| DSB-SCAN-004 | `container-image-scanning` | GAP → pre-push image scan | scan | BLOCK (default) |
| DSB-SCAN-005 | `pipeline-configuration-scanning` | GAP → workflow assertions | scan | WARN (default) |
| DSB-SCAN-006 | `dast` | GAP → staging DAST | post-deploy | WARN (default) |
| DSB-IAC-001 | `iac-scanning` | GAP → Terraform config scan | scan | BLOCK (default) |
| DSB-SC-002 | `pipeline-configuration-scanning` | GAP → SHA-pin assertion | cross-cutting | BLOCK (default) |
| DSB-ART-001 | `artifact-integrity-verification` | GAP → ECR push | deploy | BLOCK (default) |
| DSB-ART-003 | `build-provenance` | GAP → attestation | build | WARN (default) |
| DSB-ART-004 | `artifact-integrity-verification` | GAP → deploy by digest | deploy | BLOCK (default) |
| DSB-DEPLOY-001 | `deployment-gating` | GAP → job `needs` graph | deploy | BLOCK (default) |
| DSB-DEPLOY-002 | `deployment-gating` | GAP → one build, two deploys | deploy | BLOCK (default) |
| DSB-DEPLOY-003 | `deployment-gating` | GAP → job ordering | deploy | WARN (default) |
| DSB-ID-001 | `workload-identity-management` | GAP → OIDC role assumption | cross-cutting | WARN (default) |
| DSB-ID-002 | `workload-identity-management` | GAP → scoped `permissions` | cross-cutting | BLOCK (default) |
| DSB-ID-004 | `workload-identity-management` | GAP → per-environment roles | cross-cutting | BLOCK (default) |
| DSB-EVD-001 | `pipeline-evidence-retention` | GAP → 90-day artifacts | cross-cutting | REPORT (default) |
| DSB-EXC-003 | `pipeline-configuration-scanning` | GAP → suppression assertion | cross-cutting | BLOCK (default) |

**Not applicable:**

- **DSB-IAC-002** — `runtime.kubernetes` is false and no Helm chart is produced. ECS
  is not Kubernetes; a Kubernetes configuration scanner would be bloat.
- **DSB-SCAN-008** — no organizational licensing policy was stated, so there is
  nothing to enforce against.
- **DSB-SRC-003** — `source.fork_prs_allowed` is false. Private repository, no
  untrusted contributions.

**Undetermined**, and therefore neither implemented nor dismissed: `artifact-signing`
(DSB-ART-002) and `api-security-testing` (DSB-SCAN-007). Signing requires a stated
organizational requirement; API testing requires knowing whether the service exposes
a specified API surface.

## Decisions worth reading

**Container scan runs before push.** Scanning a registry after the fact means the
vulnerable image already exists and is pullable. The pipeline scans the local image,
then pushes only on success (DSB-SCAN-004).

**SCA runs against the lockfile, not the built bundle.** Bundling destroys the
transitive dependency graph that makes composition analysis accurate (DSB-SCAN-002).

**One build, two deployments.** Production consumes the same digest staging
validated. Rebuilding per environment would mean every scan result describes a
different artifact than the one running (DSB-DEPLOY-002, DSB-ART-004).

**DAST targets staging only.** `policy.dast_prod_authorized` is false, so production
is never targeted. Under DSB, unknown is treated as false — absence of information
is not authorization (DSB-SCAN-006).

**No long-lived cloud credentials.** OIDC federation with per-environment roles.
A static key in CI is a permanent, copyable credential to production
(DSB-ID-001, DSB-ID-004).

**Tests gate the scans.** The three scan jobs run in parallel with each other but
all depend on `test`. Scanning alongside testing would spend scanner capacity and
wall-clock time on an artifact a failing unit test already disqualified
(DSB-TEST-001).

**The pipeline audits itself.** Two assertions fail the build if a third-party action
is unpinned (DSB-SC-002) or if any security step has been neutralized with
`|| true` or `continue-on-error` (DSB-EXC-003).

Both hold their patterns in `env` and bracket-escape them, so neither assertion
matches its own source. A self-matching check fails on a clean repository, which
looks identical to a real finding and is how these checks end up deleted. The
suppression check also allows a line annotated `# DSB-WARN: <rule-id>`, because
`continue-on-error` is how this platform expresses a WARN-level control (§5.2) —
what DSB-EXC-003 forbids is the undeclared kind.

## Before using this

- **Set the repository variables it reads.** `ECR_REGISTRY` (the registry host,
  which is what makes `docker push` reach the controlled registry rather than the
  public default), `AWS_ECR_PUBLISH_ROLE`, `AWS_DEPLOY_ROLE_STAGING`,
  `AWS_DEPLOY_ROLE_PRODUCTION`, and `STAGING_URL`. The publish role is deliberately
  separate from the deployment roles — the build job has no reason to hold either
  (DSB-ID-002).
- **Pin the scanner images by digest.** This example pins them by version tag for
  readability. Production use should pin by digest.
- **Verify the action SHAs.** Those shown correspond to the tagged versions in
  comments at time of writing. Re-verify before adopting.
- **Substitute your own capabilities.** The scanners here are illustrative. If your
  organization already has SAST or SCA, use that instead — DSB requires the
  capability, not the product.
