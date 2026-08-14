# Example — Design/Generate: Java service on Jenkins with an existing toolchain

The scenario from [issue #180](https://github.com/devsecblueprint/devsecblueprint/issues/180):

> We use Jenkins, Java, Maven, Artifactory, Checkmarx, Black Duck, Prisma Cloud,
> and OpenShift. How should our pipeline be designed?

See [`Jenkinsfile`](Jenkinsfile).

## What this example is for

The GitHub Actions example is greenfield — every capability is a gap, so every
capability gets a tool. This one is the opposite and more common case: **an
organization that already owns security products.**

The defining property of the output is what it does *not* contain.

## Workload profile

```yaml
source:            { host: github }
languages:         [java]
package_managers:  [maven]
artifacts:         { container: true, package: true }
iac:               { present: false }
runtime:           { kubernetes: true }               # OpenShift
deploy:            { targets: [openshift], environments: [staging, production],
                     promotion_model: promote }
cicd:              { platform: jenkins, runners: self-hosted }
registry:          { present: true, controlled_proxy: true }   # Artifactory
testing:           { unit: true, integration: true }

existing_controls:
  sast:                          [ { tool: Checkmarx,    scope: full } ]
  software-composition-analysis: [ { tool: Black Duck,   scope: full } ]
  container-image-scanning:      [ { tool: Prisma Cloud, scope: full } ]

policy:            { enforcement_posture: strict, dast_prod_authorized: false }
```

## Capability resolution

| Capability | Decision | Rule |
|---|---|---|
| `sast` | **REUSE — Checkmarx** | DSB-SCAN-001 |
| `software-composition-analysis` | **REUSE — Black Duck** | DSB-SCAN-002 |
| `container-image-scanning` | **REUSE — Prisma Cloud** | DSB-SCAN-004 |
| `artifact-integrity-verification` | **REUSE — Artifactory** | DSB-ART-001, DSB-ART-004 |
| controlled dependency source | **REUSE — Artifactory virtual repo** | DSB-SC-001 |
| `secret-scanning` | GAP or DELEGATED — see below | DSB-SCAN-003 |
| `sbom-generation` | GAP | DSB-BUILD-003 |
| `dast` | GAP | DSB-SCAN-006 |

**Zero new scanners are introduced for SAST, SCA, or container scanning.** Adding
Trivy alongside Prisma Cloud, or Snyk alongside Black Duck, would be a defect under
principles 5–7. Duplicate scanners produce divergent findings, split triage, and are
the usual reason teams start ignoring results entirely.

**Not applicable:**

- **DSB-IAC-001, DSB-IAC-003, DSB-IAC-004, DSB-TEST-002** — `iac.present` is false.
  No infrastructure-as-code in the delivery process, so no IaC scanning.
- **DSB-SCAN-008** — no licensing policy stated. Black Duck could satisfy this
  immediately if one exists; ask before assuming.

**Undetermined:** `artifact-signing` (DSB-ART-002) and `build-provenance`
(DSB-ART-003) — both require a stated organizational requirement.

## The delegation question

`secret-scanning` is the interesting one. Enterprises frequently own this at the
platform layer via a server-side hook or an organization-wide scanning service.

- If the app pipeline owns it → **GAP**, implement the stage as shown.
- If a platform team owns it → **DELEGATED**. Document the boundary and **delete
  that stage.** Duplicating a governed control is bloat, not defense in depth.

The pipeline includes the stage with a comment marking this decision, because the
requester did not say who owns it. That is the honest output: implement it, and flag
that it should be removed if it turns out to be owned elsewhere.

## Decisions worth reading

**SCA runs detector-based against the Maven tree, with signature scanning
disabled.** Signature-scanning a shaded jar produces noise and loses the transitive
dependency graph. This single flag is the difference between accurate SCA and a
report nobody trusts (DSB-SCAN-002).

**The image is built from the *published* jar**, downloaded back from Artifactory
rather than taken from `target/`. This guarantees the image contains the exact
artifact the registry holds, not a local rebuild (DSB-BUILD-001).

**`twistcli` runs before push.** A failing image never reaches the registry
(DSB-SCAN-004).

**One build, promoted twice.** Staging and production consume the same digest via
Artifactory repository promotion. Rebuilding per environment would make every scan
result describe a different artifact than the one running — the evidence becomes
fiction (DSB-DEPLOY-002).

**No `|| true` anywhere.** DSB-EXC-003 forbids neutralizing a security step inline.
It is worth grepping existing pipelines for this pattern — it is common and rarely
deliberate.

**Ephemeral Kubernetes agents rather than static Jenkins nodes** (DSB-BUILD-004).

## Recommendation beyond the pipeline

Jenkins holds credentials to source, Artifactory, and every cluster. It is usually
the softest target in this stack (principle 16).

Consider having Jenkins write the digest to a manifest repository and letting a
GitOps controller reconcile production, rather than Jenkins pushing with cluster
credentials. That removes production access from Jenkins entirely
(DSB-ID-002, DSB-ID-004).

## Before using this

Stage syntax depends on which plugins are installed and how they are configured.
Treat the security-step placement and enforcement as the reusable part, and adapt
the invocations to your environment. The DSB rules are constant; the expression is
not.
