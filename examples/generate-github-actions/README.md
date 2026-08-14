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
| DSB-BUILD-001 | traceable build | GAP → implemented | build | BLOCK (default) |
| DSB-BUILD-002 | pinned dependencies | GAP → `npm ci` | build | BLOCK (default) |
| DSB-BUILD-003 | `sbom-generation` | GAP → CycloneDX | build | WARN (default) |
| DSB-BUILD-004 | ephemeral build env | SATISFIED by hosted runners | build | WARN (default) |
| DSB-TEST-001 | `automated-testing` | GAP → unit + integration | test | BLOCK (default) |
| DSB-TEST-002 | infra validation | GAP → `terraform validate` | test | BLOCK (default) |
| DSB-SCAN-001 | `sast` | GAP → SAST scanner | scan | BLOCK (default) |
| DSB-SCAN-002 | `software-composition-analysis` | GAP → dependency audit | scan | BLOCK (default) |
| DSB-SCAN-003 | `secret-scanning` | GAP → history scan | scan | BLOCK (default) |
| DSB-SCAN-004 | `container-image-scanning` | GAP → pre-push image scan | scan | BLOCK (default) |
| DSB-SCAN-005 | `pipeline-configuration-scanning` | GAP → workflow assertions | scan | WARN (default) |
| DSB-SCAN-006 | `dast` | GAP → staging DAST | post-deploy | WARN (default) |
| DSB-IAC-001 | `iac-scanning` | GAP → Terraform config scan | scan | BLOCK (default) |
| DSB-SC-002 | pinned pipeline components | GAP → SHA-pin assertion | cross-cutting | BLOCK (default) |
| DSB-ART-001 | controlled registry | GAP → ECR push | deploy | BLOCK (default) |
| DSB-ART-003 | `build-provenance` | GAP → attestation | build | WARN (default) |
| DSB-ART-004 | deploy by immutable id | GAP → deploy by digest | deploy | BLOCK (default) |
| DSB-DEPLOY-001 | gated deployment | GAP → job `needs` graph | deploy | BLOCK (default) |
| DSB-DEPLOY-002 | promote, don't rebuild | GAP → one build, two deploys | deploy | BLOCK (default) |
| DSB-DEPLOY-003 | staging before production | GAP → job ordering | deploy | WARN (default) |
| DSB-ID-001 | federated identity | GAP → OIDC role assumption | cross-cutting | WARN (default) |
| DSB-ID-002 | least privilege | GAP → scoped `permissions` | cross-cutting | BLOCK (default) |
| DSB-ID-004 | environment separation | GAP → per-environment roles | cross-cutting | BLOCK (default) |
| DSB-EVD-001 | evidence retention | GAP → 90-day artifacts | cross-cutting | REPORT (default) |
| DSB-EXC-003 | no inline suppression | GAP → suppression assertion | cross-cutting | BLOCK (default) |

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

**The pipeline audits itself.** Two assertions fail the build if a third-party action
is unpinned (DSB-SC-002) or if any security step has been neutralized with
`|| true` or `continue-on-error` (DSB-EXC-003).

## Before using this

- **Pin the scanner images by digest.** This example pins them by version tag for
  readability. Production use should pin by digest.
- **Verify the action SHAs.** Those shown correspond to the tagged versions in
  comments at time of writing. Re-verify before adopting.
- **Substitute your own capabilities.** The scanners here are illustrative. If your
  organization already has SAST or SCA, use that instead — DSB requires the
  capability, not the product.
