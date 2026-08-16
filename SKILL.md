---
name: dsb-devsecops
description: >
  DSB DevSecOps engineering skill from The DevSec Blueprint. Advise on, design,
  generate, and review CI/CD delivery pipelines using the Build → Test → Scan →
  Deploy methodology. Use when designing or architecting a pipeline, choosing or
  placing security scanning (SAST, SCA, secret scanning, IaC scanning, container
  scanning, DAST, API security testing), reviewing an existing pipeline, workflow,
  or repository for security gaps, auditing CI/CD against SSDF or SLSA, deciding
  which security tools a project actually needs, mapping an organization's existing
  security products onto a delivery lifecycle, or generating GitHub Actions,
  Jenkins, GitLab CI, or Azure DevOps pipeline configuration.
---

# DSB DevSecOps Engineering

Maintained by [The DevSec Blueprint](https://github.com/devsecblueprint).
MIT licensed. DSB names, logos, and curriculum content are not covered by that
license.

> **DSB defines the required capabilities and engineering outcomes.
> The organization determines how those capabilities are implemented.**

This skill implements DSB knowledge. It is not the source of that knowledge, and it
never overrides engineering judgment.

---

## 1. The methodology

```
BUILD → TEST → SCAN → DEPLOY
```

**Logical engineering phases.** They do not mandate a job structure, vendor, or
platform. A single GitHub Actions job may satisfy all four; twelve Jenkins stages may
satisfy the same four.

> **Build what you need. Test what you built. Scan what can introduce meaningful
> risk. Deploy only what passed.**

**Build** — create or prepare the deliverable repeatably and traceably: compilation,
dependency resolution, packaging, container image creation, infrastructure
preparation, deployment artifact generation.

**Test** — validate expected behavior with testing appropriate to the workload: unit,
integration, framework, infrastructure, configuration, contract. Prefer existing
project-native testing. **Never invent meaningless tests to populate this phase.**

**Scan** — non-negotiable. Every pipeline includes security scanning appropriate to
the workload. Individual scanners are required only where the associated technology,
artifact, or risk actually exists.

**Deploy** — deliver or promote only artifacts that passed the applicable Build, Test,
and Scan requirements.

**Post-deployment validation** — some controls need a running workload. DAST, API
security testing, and runtime validation execute *after* deployment to an appropriate
testable environment. This is placement inside the Scan requirement, **not a fifth
phase**.

### The twenty baseline principles

1. Every delivery pipeline follows Build → Test → Scan → Deploy.
2. Security scanning is mandatory.
3. Individual security capabilities are selected based on applicability.
4. Controls are workload-driven, not checklist-driven.
5. Use the minimum sufficient security toolchain.
6. Prefer existing organizational capabilities before introducing new tools.
7. No unnecessary security tooling or duplicate scanners.
8. Testing and security scanning are separate engineering concerns.
9. Security controls execute at the earliest technically valid stage.
10. Runtime-dependent controls such as DAST execute post-deployment where applicable.
11. `Not Applicable` is a valid and explicit engineering outcome.
12. Build outputs remain traceable and trustworthy through deployment.
13. Previously validated artifacts are promoted rather than unnecessarily rebuilt.
14. Deployment identity and authorization follow least privilege.
15. Short-lived or federated workload identity is preferred where supported.
16. CI/CD pipelines are themselves attack surface and must be secured.
17. Security controls have explicit enforcement behavior.
18. DSB rules define capabilities and outcomes, not mandatory vendors.
19. Organizational architecture and ownership boundaries influence implementation.
20. This skill correlates directly with what The DevSec Blueprint teaches.

### Relationship to external standards

```
Industry standards and best practices   (SSDF, SLSA, OWASP CI/CD, SAMM, CNCF)
              ↓
DSB DevSecOps engineering methodology
              ↓
DSB rules
              ↓
Organizational context
              ↓
Platform and tool implementation
```

Frameworks inform the methodology. They do not replace engineering judgment or
dictate a pipeline architecture. Compliance regimes may be mapped, but compliance is
never the primary driver.

---

## 2. How to reason

All three modes run the same four-step procedure and produce the same intermediate
artifact, a **Control Plan**. This is why Advise, Design, and Review cannot disagree
about what applies to a given workload.

```
Input (natural language | pipeline file | repository | any mix)
        ↓
1. WORKLOAD PROFILE       structured facts; every field known / unknown
        ↓
2. APPLICABILITY          evaluate each rule against the profile
        ↓                 → APPLICABLE | NOT APPLICABLE (+reason) | UNKNOWN (+question)
3. CAPABILITY RESOLUTION  reuse existing | delegated | gap | duplicate
        ↓
4. ENFORCEMENT + PLACEMENT   BLOCK/WARN/REPORT, earliest technically valid phase
        ↓
   ══ CONTROL PLAN ══
        ↓
 Advise (explain)   Design (render)   Review (diff against observed)
```

### Step 1 — Build the Workload Profile

Extract only facts the user actually stated. **Never infer.** If they mention Java and
Maven, `languages: [java]` and `package_managers: [maven]` are stated. Whether they
build a container is *not* stated unless they said so.

Everything unstated is `unknown`. This is what lets you work without repository access.

The vocabulary is closed. These are the only fields you may reason about:

```yaml
source:            { host, protected_branches, review_required, fork_prs_allowed }
languages:         [java, python, javascript, go, ...]
package_managers:  [maven, npm, pip, ...]
artifacts:         { container, package, binary, iac_plan, helm_chart }
iac:               { present, tools }
runtime:           { kubernetes, serverless, vm, paas }
deploy:            { targets, environments, promotion_model }   # rebuild | promote
cicd:              { platform, runners, shared_library }        # hosted | self-hosted
identity:          { mechanism }         # oidc | static-creds | vault | cloud-role
registry:          { present, controlled_proxy }
testing:           { unit, integration, contract, infrastructure }
existing_controls: { <capability>: [ { tool, owner, scope } ] }
ownership:         { <capability>: app-pipeline | platform-team | external-governed | none }
policy:            { enforcement_posture, exception_process, compliance_regimes,
                     dast_prod_authorized, signing_required, provenance_required }
```

Every field is tri-state: `true` / `false` / `unknown`.

`existing_controls` and `ownership` describe **who satisfies a control**. They are
resolution concerns and must never affect applicability.

### Step 2 — Evaluate applicability

| Result | Meaning | What you do |
|---|---|---|
| **TRUE** | Rule applies | Include it in the plan |
| **FALSE** | Not applicable | Record it **with the reason** |
| **UNKNOWN** | Insufficient facts | Record the exact field you need |

Operator semantics:

- `all_of` — every atom TRUE. **A FALSE atom beats an UNKNOWN one**: the rule cannot
  apply, so return FALSE rather than asking.
- `any_of` — at least one atom TRUE. **A TRUE atom beats an UNKNOWN one**: return TRUE
  rather than asking.
- `none_of` — satisfied when no atom is TRUE.

Atom forms: `field: value`, `field: {in: [...]}`, `field: {exists: true}`.

**The unresolved fields are your questions.** Do not invent an interview. Ask for
exactly what the evaluation could not decide, and nothing more.

Distinguish carefully:
- **NOT APPLICABLE** — a stated fact rules it out. "No IaC in the delivery process."
- **UNDETERMINED** — you lack the fact. Never present this as N/A, and never mark it
  applicable "to be safe."

### Step 3 — Resolve capabilities

Resolve each applicable rule's `capability` **exactly once**. Because resolution keys
on capability rather than rule, one existing tool satisfies every rule naming it.

1. Tool in `existing_controls[capability]` at full scope → **REUSE**. Name it. State
   plainly the DSB requirement is satisfied.
2. `ownership[capability]` is `external-governed` → **DELEGATED**. Document the
   boundary. **Do not duplicate the control.**
3. Neither → **GAP**. Recommend the *capability*. Tooling examples are illustrations,
   never requirements.
4. Two or more full-scope tools → **DUPLICATE**. Recommend consolidation.

A tool declared in this pipeline outranks a delegation claim. Partial scope is a GAP —
say what is uncovered.

### Step 4 — Enforcement and placement

Applicability and enforcement are **separate concerns**.

| Level | Meaning |
|---|---|
| **BLOCK** | Cannot continue until satisfied or an approved exception exists |
| **WARN** | Surfaced without preventing delivery |
| **REPORT** | Produces evidence or informational output only |
| **N/A** | Intentionally does not apply |

| Posture | BLOCK → | WARN → | REPORT → |
|---|---|---|---|
| strict | BLOCK | BLOCK | REPORT |
| balanced | BLOCK | WARN | REPORT |
| advisory | WARN | WARN | REPORT |

**Always state provenance** — `default` or `org-policy`. A reader must be able to tell
whether BLOCK came from DSB or from their own policy. Never present an organizational
choice as a DSB requirement.

**Placement** is earliest-technically-valid.

> **Hard guard rail:** never propose active DAST or intrusive testing against
> production unless `policy.dast_prod_authorized` is explicitly true. `unknown` is
> treated as **false**. Absence of information is not authorization.

---

## 3. The DSB rule catalog

Rule IDs are permanent and appear in audit trails. Cite them in every recommendation.
Tooling examples are **illustrative** — presenting one as a DSB requirement is a defect.

Format: **ID — Title** · phase · capability · default enforcement · applicability.

### DSB-BUILD — build and artifact creation

**DSB-BUILD-001 — Builds execute from version-controlled source**
· build · `build-traceability` · BLOCK · applies when `source.host exists`
**Requirement.** Every deployable artifact must be produced by an automated build
executing from a specific, identifiable commit, and must be traceable back to it.
**Why.** An artifact that cannot be traced to a commit cannot be reviewed, reproduced,
or attested. Traceability is the precondition for every downstream supply-chain
control; without it, scan results cannot be tied to what shipped.
*SSDF PS.1.1, PS.3.1 · SLSA build-L1 · CNCF build-integrity · Curriculum: module-2-1 (What is the Secure SDLC?), module-2-4 (DevSecOps Fundamentals)*

**DSB-BUILD-002 — Dependency resolution is controlled and repeatable**
· build · `dependency-resolution-control` · BLOCK · applies when `package_managers exists`
**Requirement.** Dependencies must resolve through a controlled source with pinned or
locked versions, such that the same commit produces the same dependency set.
**Why.** Unpinned resolution means the artifact you scanned and the artifact you ship
can contain different code. It also makes every SCA result a point-in-time claim about
something that no longer exists.
*SSDF PW.4.1 · SLSA build-L2 · CNCF dependency-management · Curriculum: module-2-4 (DevSecOps Fundamentals)*

**DSB-BUILD-003 — A software bill of materials is produced for each deployable artifact**
· build · `sbom-generation` · WARN · applies when `artifacts.package` or `artifacts.container`
**Requirement.** Generate an SBOM at build time, attached to the artifact or its build
record.
**Why.** The SBOM is what makes a CVE published after release answerable without
rebuilding. It is the difference between "are we exposed?" taking minutes or weeks.
*SSDF PS.3.2 · SLSA build-L2 · CNCF sbom · Curriculum: module-2-4 (DevSecOps Fundamentals)*

**DSB-BUILD-004 — Build environments are ephemeral**
· build · `build-environment-isolation` · WARN · applies when `cicd.runners exists`
**Requirement.** Builds run in clean, disposable environments rather than long-lived
mutable agents carrying state between builds.
**Why.** Persistent agents accumulate credentials, caches, and artifacts from other
builds. One compromised build then contaminates every subsequent one, and nobody can
reconstruct what the environment contained.
*SSDF PO.5.1 · SLSA build-L3 · OWASP CICD-SEC-5 · Curriculum: module-2-4 (DevSecOps Fundamentals)*

### DSB-TEST — testing

**DSB-TEST-001 — Automated tests execute before security scanning**
· test · `automated-testing` · BLOCK · applies when any of `testing.unit`,
`testing.integration`, `testing.contract`, `testing.infrastructure`
**Requirement.** Where a project has automated tests, they execute and pass before
Scan. Tests must not be created solely to satisfy this phase.
**Why.** Testing and scanning are separate concerns. Running tests first fails fast on
functional defects and avoids spending scanner licence capacity and wall-clock time on
artifacts that were never going to ship.
*SSDF PW.7.2, PW.8.2 · OWASP SAMM verification-testing · Curriculum: module-2-1 (What is the Secure SDLC?)*

**DSB-TEST-002 — Infrastructure changes are validated before application**
· test · `automated-testing` · BLOCK · applies when `iac.present`
**Requirement.** Infrastructure-as-code must be validated — plan, syntax, and policy
checks — before being applied to any environment.
**Why.** Infrastructure defects fail differently from application defects: they often
fail *open*, silently widening access rather than crashing. A plan review is the last
point where that is cheap to catch.
*SSDF PW.8.2 · Curriculum: module-3-7 (IaC Security)*

### DSB-SCAN — security scanning

**DSB-SCAN-001 — Static application security testing**
· scan · `sast` · BLOCK · applies when `languages exists`
**Requirement.** First-party source must be analysed for security defects before the
artifact is promoted to a deployable state.
**Why.** SAST finds defect classes dependency and runtime analysis cannot see, at the
earliest stage where the code exists and remediation is cheapest.
*SSDF PW.7.1, PW.8.1 · OWASP SAMM verification-security-testing · OWASP CICD-SEC-1 · Curriculum: module-2-2 (What is Application Security?), module-2-3 (Secure Coding Overview)*

**DSB-SCAN-002 — Software composition analysis**
· scan · `software-composition-analysis` · BLOCK · applies when `package_managers exists` or `artifacts.package`
**Requirement.** Third-party dependencies resolved during the build must be analysed
for known vulnerabilities before promotion.
**Why.** Most code in a typical artifact is third-party. Analysing only first-party
source leaves most of the attack surface unexamined.
**Placement note.** Run SCA against the resolved dependency tree from the build, not
against a packaged or shaded artifact — packaging destroys the transitive graph that
makes SCA accurate.
*SSDF PW.4.1, RV.1.1 · OWASP CICD-SEC-3 · CNCF dependency-management · Curriculum: module-2-2 (What is Application Security?), module-2-4 (DevSecOps Fundamentals)*

**DSB-SCAN-003 — Secret scanning of source and history**
· scan · `secret-scanning` · BLOCK · applies when `source.host in (github, gitlab, bitbucket, azure-repos, other)`
**Requirement.** Repositories feeding the pipeline must be scanned for committed
credentials, tokens, and secrets, covering history rather than only the working tree.
**Why.** A committed secret is disclosed to everyone with repository access and
survives deletion in history. The exposure window opens at push time, not review time,
so detection must be automated.
*SSDF PO.5.2, PS.1.1 · OWASP CICD-SEC-6 · Curriculum: module-2-3 (Secure Coding Overview), module-3-4 (Secrets Management In The Cloud)*

**DSB-SCAN-004 — Container image vulnerability scanning**
· scan · `container-image-scanning` · BLOCK · applies when `artifacts.container`, and not `runtime.serverless`
**Requirement.** Container images built or consumed must be scanned for known
vulnerabilities in OS packages and application dependencies before promotion to a
deployable registry.
**Why.** Base images accumulate CVEs independently of application code. Scanning only
source dependencies leaves most of a container's attack surface unexamined.
**Placement note.** Scan before push. Scanning a registry after the fact means the
vulnerable image already exists and can be pulled.
*SSDF PW.4.1, RV.1.1 · SLSA build-L2 · OWASP CICD-SEC-4 · CNCF artifact-verification · Curriculum: module-2-6 (Container Security Overview), module-3-1 (What is Cloud Security Development?)*

**DSB-SCAN-005 — Pipeline configuration security analysis**
· scan · `pipeline-configuration-scanning` · WARN · applies when `cicd.platform exists`
**Requirement.** CI/CD configuration must itself be analysed for insecure practices:
unpinned third-party steps, excessive permissions, untrusted trigger contexts, secret
exposure in logs.
**Why.** The pipeline holds credentials to source, registries, and production. It is
frequently the softest target in the stack and the least reviewed file in the repo.
*OWASP CICD-SEC-1, CICD-SEC-5 · SSDF PO.5.1 · Curriculum: module-2-4 (DevSecOps Fundamentals)*

**DSB-SCAN-006 — Dynamic application security testing**
· post-deploy · `dast` · WARN · applies when `deploy.environments exists` and
`runtime` indicates a reachable service
**Requirement.** Where the workload exposes a running interface, dynamic testing must
execute against a deployed instance in a non-production environment.
**Why.** DAST observes behavior that static analysis cannot: authentication flows,
misconfiguration, and defects that only exist once components are assembled and running.
**Guard rail.** Never against production unless `policy.dast_prod_authorized` is
explicitly true. `unknown` means no.
*SSDF RV.1.1 · OWASP SAMM verification-security-testing · Curriculum: module-2-2 (What is Application Security?)*

**DSB-SCAN-007 — API security testing**
· post-deploy · `api-security-testing` · WARN · applies when the workload exposes an API
**Requirement.** Exposed API surfaces must be tested against their specification for
authorization, input handling, and exposure defects.
**Why.** API defects — broken object-level authorization above all — are invisible to
SAST and to generic DAST crawling, because they require understanding intended
authorization semantics.
*OWASP SAMM verification-security-testing · Curriculum: module-3-3 (API Patterns and SDKs)*

**DSB-SCAN-008 — Dependency license and compliance analysis**
· scan · `license-compliance-analysis` · REPORT · applies when `package_managers exists`
and the organization states a licensing policy
**Requirement.** Where organizational policy governs licensing, dependency licenses
must be analysed against it.
**Why.** Licensing is a legal obligation attached to the same dependency graph SCA
already walks. Applicable only where a policy exists to enforce — otherwise this rule
is N/A, not a default control.
*SSDF PW.4.4 · Curriculum: module-2-4 (DevSecOps Fundamentals)*

### DSB-IAC — infrastructure-as-code security

**DSB-IAC-001 — Infrastructure-as-code static analysis**
· scan · `iac-scanning` · BLOCK · applies when `iac.present`
**Requirement.** IaC definitions must be analysed for insecure configuration before
the plan is applied.
**Why.** Misconfigured infrastructure is the most common cloud breach cause, and
unlike application defects it is fully determinable from source before anything runs.
*SSDF PW.8.1 · OWASP CICD-SEC-9 · Curriculum: module-3-7 (IaC Security)*

**DSB-IAC-002 — Kubernetes and workload configuration analysis**
· scan · `kubernetes-configuration-scanning` · BLOCK · applies when `runtime.kubernetes`
or `artifacts.helm_chart`
**Requirement.** Kubernetes manifests, Helm charts, and equivalent workload
configuration must be analysed for insecure settings before deployment.
**Why.** Privileged containers, host mounts, and absent network policy are deployment
configuration defects, not image defects — image scanning will never surface them.
*OWASP CICD-SEC-9 · CNCF workload-security · Curriculum: module-2-6 (Container Security Overview)*

**DSB-IAC-003 — Policy-as-code enforcement**
· scan · `policy-as-code-enforcement` · WARN · applies when `iac.present` and the
organization states configuration policy
**Requirement.** Where organizational configuration policy exists, it must be enforced
programmatically rather than by review convention.
**Why.** Policy enforced by human review is applied inconsistently and degrades under
delivery pressure. Encoded policy applies identically to everyone at 3am.
*SSDF PO.1.1 · Curriculum: module-3-7 (IaC Security)*

**DSB-IAC-004 — Infrastructure changes are reviewed before application to production**
· deploy · `deployment-gating` · BLOCK · applies when `iac.present` and
`deploy.environments` includes production
**Requirement.** The planned change set must be produced and reviewed before applying
infrastructure changes to production.
**Why.** Infrastructure changes are frequently irreversible and can sever access to
the systems needed to fix them. The plan is the last cheap checkpoint.
*SSDF PW.8.2 · Curriculum: module-3-7 (IaC Security)*

### DSB-SRC — source control security

**DSB-SRC-001 — Deployable branches are protected**
· cross-cutting · `source-control-hardening` · BLOCK · applies when `source.host exists`
**Requirement.** Branches that trigger deployment must prevent direct pushes, force
pushes, and unreviewed changes.
**Why.** Every downstream control is worthless if code can reach the deployable branch
without passing through the pipeline that enforces them.
*SSDF PO.5.2 · OWASP CICD-SEC-1 · Curriculum: module-2-1 (What is the Secure SDLC?)*

**DSB-SRC-002 — Changes are reviewed before merge**
· cross-cutting · `source-control-hardening` · BLOCK · applies when `source.host exists`
**Requirement.** Changes to deployable branches require review by someone other than
the author.
**Why.** Review is the only control that catches intent. Automation catches known
patterns; it does not catch a deliberate or subtle logic change.
*SSDF PW.7.1 · SLSA source-L2 · Curriculum: module-2-3 (Secure Coding Overview)*

**DSB-SRC-003 — Untrusted contributions cannot access privileged pipeline context**
· cross-cutting · `source-control-hardening` · BLOCK · applies when
`source.fork_prs_allowed`
**Requirement.** Pipelines triggered by untrusted contributions must not have access
to deployment credentials, production secrets, or privileged runners.
**Why.** A pipeline definition supplied by an untrusted branch, executing with
production credentials, is the classic CI compromise. It requires no vulnerability —
only the default configuration.
*OWASP CICD-SEC-4 · SSDF PO.5.1 · Curriculum: module-2-4 (DevSecOps Fundamentals)*

### DSB-SC — software supply chain

**DSB-SC-001 — Dependencies resolve through a controlled source**
· build · `dependency-resolution-control` · WARN · applies when `package_managers exists`
**Requirement.** Builds resolve dependencies through an organizationally controlled
registry or proxy rather than reaching public registries directly.
**Why.** A controlled proxy gives you an inventory of what actually entered your
builds, survives upstream deletion, and is the only place a malicious package can be
blocked before it is compiled into an artifact.
*SSDF PW.4.1 · SLSA build-L2 · CNCF dependency-management · Curriculum: module-2-4 (DevSecOps Fundamentals)*

**DSB-SC-002 — Third-party pipeline components are pinned to immutable references**
· cross-cutting · `pipeline-configuration-scanning` · BLOCK · applies when `cicd.platform exists`
**Requirement.** Third-party actions, plugins, orbs, and templates must be referenced
by immutable identifier rather than a mutable tag or branch.
**Why.** A mutable reference means a third party can change what executes inside your
pipeline, with your credentials, without any change on your side.
*SLSA build-L3 · OWASP CICD-SEC-3 · CNCF build-integrity · Curriculum: module-2-4 (DevSecOps Fundamentals)*

**DSB-SC-003 — Newly introduced dependencies are evaluated before adoption**
· scan · `software-composition-analysis` · WARN · applies when `package_managers exists`
**Requirement.** Dependency additions must be surfaced for evaluation rather than
merged as ordinary changes.
**Why.** Adding a dependency imports its transitive tree, its maintainers, and its
update channel permanently. That decision deserves more scrutiny than a code change of
the same diff size.
*SSDF PW.4.1 · CNCF dependency-management · Curriculum: module-2-4 (DevSecOps Fundamentals)*

### DSB-ART — artifacts, provenance, signing, registries

**DSB-ART-001 — Artifacts are published to a controlled registry**
· deploy · `artifact-integrity-verification` · BLOCK · applies when `artifacts.package`
or `artifacts.container`
**Requirement.** Deployable artifacts must be published to a controlled registry that
records their identity and origin.
**Why.** Without a registry of record there is no stable identity to promote, verify,
or roll back to, and no way to prove what was deployed.
*SSDF PS.3.1 · SLSA build-L1 · Curriculum: module-2-4 (DevSecOps Fundamentals)*

**DSB-ART-002 — Artifacts are signed where required**
· build · `artifact-signing` · WARN · applies when `policy.signing_required`
**Requirement.** Where the organization requires signing, artifacts must be
cryptographically signed as part of the build.
**Why.** Signing binds an artifact to the system that produced it, so consumers can
detect substitution between build and deployment.
*SSDF PS.2.1 · SLSA build-L2 · CNCF artifact-signing · Curriculum: module-2-4 (DevSecOps Fundamentals)*

**DSB-ART-003 — Build provenance is recorded**
· build · `build-provenance` · WARN · applies when `policy.provenance_required` or
`cicd.platform` supports attestation
**Requirement.** Record attestable provenance describing how, where, and from what
source an artifact was built.
**Why.** Provenance is what lets a consumer verify an artifact came from the expected
pipeline and source, rather than trusting that it did.
*SLSA build-L2, build-L3 · SSDF PS.3.2 · CNCF provenance · Curriculum: module-2-4 (DevSecOps Fundamentals)*

**DSB-ART-004 — Deployed artifacts are verified by immutable identity**
· deploy · `artifact-integrity-verification` · BLOCK · applies when `artifacts.container`
or `artifacts.package`
**Requirement.** Deployment must reference artifacts by immutable identity — digest or
checksum — not by a mutable tag.
**Why.** Tags are mutable. Deploying by tag means the artifact you scanned and the
artifact you ran can differ, which silently invalidates every scan result you hold.
*SLSA build-L2 · SSDF PS.3.1 · CNCF artifact-verification · Curriculum: module-2-6 (Container Security Overview)*

### DSB-DEPLOY — deployment and promotion

**DSB-DEPLOY-001 — Only artifacts that passed required controls are deployed**
· deploy · `deployment-gating` · BLOCK · applies when `deploy.targets exists`
**Requirement.** Deployment must be conditional on the applicable Build, Test, and
Scan requirements having passed, or on a recorded exception.
**Why.** This is the whole point of the phase ordering. Controls that do not gate
delivery are reporting, not enforcement — which is a legitimate choice, but must be a
deliberate one.
*SSDF PW.8.2, RV.1.1 · Curriculum: module-2-1 (What is the Secure SDLC?)*

**DSB-DEPLOY-002 — Validated artifacts are promoted, not rebuilt**
· deploy · `deployment-gating` · BLOCK · applies when
`deploy.environments` has more than one environment
**Requirement.** Progression between environments promotes the already-validated
artifact rather than rebuilding from source per environment.
**Why.** Rebuilding severs the chain of custody: every scan result describes a
different artifact than the one running in production. The evidence becomes fiction.
*SLSA build-L2 · SSDF PS.3.1 · Curriculum: module-2-4 (DevSecOps Fundamentals)*

**DSB-DEPLOY-003 — Production deployment follows validation in a lower environment**
· deploy · `deployment-gating` · WARN · applies when `deploy.environments`
includes both production and a non-production environment
**Requirement.** Artifacts reach production only after being deployed and validated in
at least one lower environment.
**Why.** Some defect classes appear only once deployed. A lower environment is where
that discovery is affordable, and it is the only place runtime-dependent controls can
run safely.
*SSDF RV.1.1 · Curriculum: module-2-1 (What is the Secure SDLC?)*

**DSB-DEPLOY-004 — Deployment is automated and reproducible**
· deploy · `deployment-gating` · WARN · applies when `deploy.targets exists`
**Requirement.** Deployment executes through automation from recorded configuration
rather than manual operator steps.
**Why.** Manual deployment is unreviewable, unrepeatable, and unattributable. It also
means the credentials involved are held by people rather than scoped to a system.
*SSDF PO.3.1 · Curriculum: module-2-4 (DevSecOps Fundamentals)*

### DSB-ID — workload identity, authentication, authorization

**DSB-ID-001 — Pipelines authenticate with short-lived federated identity**
· cross-cutting · `workload-identity-management` · WARN · applies when `identity.mechanism exists`
**Requirement.** Where the platform and target support it, pipelines authenticate
using short-lived federated workload identity rather than long-lived static credentials.
**Why.** A static credential in CI is a permanent, copyable, widely-readable key to
production. Federated identity makes stolen credentials expire on their own.
*SSDF PO.5.1 · OWASP CICD-SEC-2 · Curriculum: module-3-2 (IAM Fundamentals)*

**DSB-ID-002 — Deployment identity follows least privilege**
· cross-cutting · `workload-identity-management` · BLOCK · applies when `deploy.targets exists`
**Requirement.** Deployment credentials are scoped to the specific environment and
resources they deploy, not shared across projects or environments.
**Why.** A single over-scoped deployment identity converts a compromise of the least
important pipeline into a compromise of everything it can reach.
*SSDF PO.5.1 · OWASP CICD-SEC-2 · Curriculum: module-3-2 (IAM Fundamentals)*

**DSB-ID-003 — Secrets are not stored in pipeline definitions or source**
· cross-cutting · `secrets-management` · BLOCK · applies when `cicd.platform exists`
**Requirement.** Credentials are supplied through a secret store or platform secret
mechanism, never committed to source or embedded in pipeline definitions.
**Why.** Anything in the repository is readable by everyone with repository access,
retained in history, and copied into every clone and fork.
*SSDF PO.5.2 · OWASP CICD-SEC-6 · Curriculum: module-3-4 (Secrets Management In The Cloud)*

**DSB-ID-004 — Environment credentials are separated**
· cross-cutting · `workload-identity-management` · BLOCK · applies when
`deploy.environments` has more than one environment
**Requirement.** Each environment uses distinct credentials, and non-production
pipelines cannot obtain production credentials.
**Why.** Shared credentials mean a compromise of the least-protected environment is a
compromise of production. Non-production is always the least protected.
*SSDF PO.5.1 · OWASP CICD-SEC-2 · Curriculum: module-3-2 (IAM Fundamentals)*

### DSB-EVD — evidence, logging, observability

**DSB-EVD-001 — Security control results are retained as evidence**
· cross-cutting · `pipeline-evidence-retention` · REPORT · applies when `cicd.platform exists`
**Requirement.** Scan results and control outcomes are retained and associated with
the artifact and commit they describe.
**Why.** A control that leaves no record cannot demonstrate it ran, cannot support an
audit, and cannot be compared over time to show whether anything improved.
*SSDF PO.4.1, RV.1.1 · Curriculum: module-3-5 (Cloud Logging and Monitoring)*

**DSB-EVD-002 — Pipeline execution is auditable**
· cross-cutting · `pipeline-evidence-retention` · REPORT · applies when `cicd.platform exists`
**Requirement.** Pipeline runs record what was built, from what source, by whom or what
trigger, and what was deployed where.
**Why.** During an incident the first questions are what shipped, when, and from what
commit. Without an audit trail those questions take days.
*SSDF PO.4.1 · OWASP CICD-SEC-10 · Curriculum: module-3-5 (Cloud Logging and Monitoring)*

**DSB-EVD-003 — Findings reach an owning team**
· cross-cutting · `security-findings-management` · REPORT · applies when
any scanning capability resolves to REUSE or GAP
**Requirement.** Security findings are routed to the team that owns remediation, not
left only in pipeline output.
**Why.** Findings visible only in a build log are not findings. This is the most common
reason a technically correct pipeline produces no security improvement.
*SSDF RV.2.1 · Curriculum: module-2-1 (What is the Secure SDLC?)*

### DSB-EXC — exceptions and risk acceptance

**DSB-EXC-001 — Exceptions are explicit, owned, and time-bound**
· cross-cutting · `exception-management` · BLOCK · applies when
`policy.exception_process` or any control resolves to BLOCK
**Requirement.** Bypassing a BLOCK-level control requires a recorded exception with a
named owner, a stated rationale, and an expiry date.
**Why.** Exceptions are legitimate engineering decisions. Undocumented, permanent
bypasses are not — and without expiry every exception becomes permanent by default.
*SSDF RV.2.2 · OWASP SAMM governance-policy · Curriculum: module-2-1 (What is the Secure SDLC?)*

**DSB-EXC-002 — Suppressions reference an exception**
· cross-cutting · `exception-management` · WARN · applies when any scanning
capability resolves to REUSE
**Requirement.** In-code or in-tool suppressions of security findings must reference
the exception authorizing them.
**Why.** An unexplained suppression is indistinguishable from an accidental one, and
nobody will ever remove it because nobody knows why it exists.
*SSDF RV.2.2 · Curriculum: module-2-3 (Secure Coding Overview)*

**DSB-EXC-003 — Controls are not disabled inline to pass a build**
· cross-cutting · `pipeline-configuration-scanning` · BLOCK · applies when `cicd.platform exists`
**Requirement.** Pipeline definitions must not neutralize security controls through
inline suppression of failures — `|| true`, `continue-on-error`, `catchError`, and
equivalents applied to security steps.
**Why.** This produces a pipeline that appears to enforce controls and does not. It is
strictly worse than having no control, because it manufactures false assurance.
**Review note.** Grep for these patterns explicitly. They are common and rarely
deliberate.
*OWASP CICD-SEC-1 · SSDF PW.8.2 · Curriculum: module-2-4 (DevSecOps Fundamentals)*

---

## 4. Security capability catalog

DSB requires **capabilities, never vendors**.

| Group | Capabilities |
|---|---|
| Application and repository | `sast`, `software-composition-analysis`, `secret-scanning`, `license-compliance-analysis`, `source-control-hardening` |
| Infrastructure and platform | `iac-scanning`, `kubernetes-configuration-scanning`, `policy-as-code-enforcement`, `pipeline-configuration-scanning`, `build-environment-isolation`, `secrets-management`, `workload-identity-management` |
| Artifact and supply chain | `container-image-scanning`, `sbom-generation`, `artifact-integrity-verification`, `artifact-signing`, `build-provenance`, `build-traceability`, `dependency-resolution-control`, `deployment-gating` |
| Dynamic and post-deployment | `dast`, `api-security-testing` |
| Governance and evidence | `pipeline-evidence-retention`, `security-findings-management`, `exception-management` |
| Engineering | `automated-testing` (not a security control) |

**Capabilities are distinguished by what actually satisfies them, not by what sounds
adjacent.** `secret-scanning` detects committed secrets; `secrets-management` supplies
credentials from a store. `dependency-resolution-control` makes resolution repeatable;
`software-composition-analysis` examines what was resolved. Because resolution keys on
capability, collapsing two of these into one makes a tool that provides only the first
report the second as satisfied.

**Advanced, organization-dependent** — fuzz testing, IAST, specialized compliance
scanners, proprietary internal tools, penetration testing workflows. Not baseline.
Include only where workload, policy, or organizational requirements make them apply.

Custom and proprietary tools need no rule changes — the organization declares them in
`existing_controls` against the capability they satisfy, and resolution treats them
identically to any commercial product.

---

## 5. Operating modes

Repository access is never required. Partial context produces a partial plan plus
specific questions — never a guess.

### 5.1 Advise

**Use when** the user describes requirements, tooling, architecture, or constraints
and wants guidance.

Output structure:

1. **Understanding** — the profile as you read it, including what you have no facts
   about. Lets the user correct you before the analysis lands.
2. **Build → Test → Scan → Deploy mapping** — where each capability belongs and why
   that is the earliest technically valid stage.
3. **Capability resolution** — capability, decision, tool, rule ID, enforcement.
   Keep this table narrow enough to render in an 80-column terminal: fold the tool
   into the decision cell (`REUSE — Checkmarx`) and abbreviate provenance
   (`BLOCK (default)`).
4. **Gaps** — what is missing, at capability level, with enforcement recommendations.
5. **Not applicable** — each with its reason, and separately, what is *undetermined*.
   **Never omit this section.**
6. **What I need to know** — the unresolved fields, phrased as questions.

Do not emit pipeline code in Advise mode unless asked. If asked, switch to Design.

### 5.2 Design / Generate

**Use when** the user wants implementation-ready pipeline configuration.

**Completeness gate.** Do not generate until you know `cicd.platform`, `languages`,
`deploy.targets`, and at least one `artifacts` field. If any are unresolved, ask. A
plausible-looking pipeline built on guesses is worse than a question, because it will
be run.

Procedure:

1. Build the Control Plan exactly as in Advise.
2. Answer the **platform adapter contract** for the target platform:
   1. How is a logical phase expressed? (job, stage, step)
   2. How is BLOCK expressed? (non-zero exit, gate, required check)
   3. How is WARN expressed?
   4. How is REPORT expressed? (artifact upload, published report)
   5. What workload identity mechanisms exist? (OIDC federation, credential binding)
   6. How are artifacts passed between phases?
   7. How is promote-versus-rebuild expressed?
   8. What is the secrets access pattern?
   9. What native pipeline-configuration security controls exist?
3. Render each Control Plan entry into that platform's constructs.
4. Annotate every security step with its DSB rule ID as a comment.
5. State explicitly which controls BLOCK and which WARN, and why.

**Platform notes.**

*GitHub Actions* — phases as jobs with `needs`; BLOCK as a failing step; WARN as
`continue-on-error: true`; REPORT as uploaded artifacts or SARIF; identity via OIDC to
a cloud role (`permissions: id-token: write`), never long-lived cloud keys; pin every
third-party action to a commit SHA (DSB-SC-002); never grant secrets to
`pull_request_target` on untrusted forks (DSB-SRC-003).

*Jenkins* — phases as stages, ideally in a shared library so security policy changes
do not require editing every repository; BLOCK by failing the stage; WARN via
`catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE')`; REPORT via
`archiveArtifacts` or a publisher; prefer ephemeral agents over static nodes
(DSB-BUILD-004); credentials from the credential store or a secret manager, scoped per
project (DSB-ID-002). **Never** `|| true` on a security step (DSB-EXC-003).

*Other platforms* (GitLab CI, Azure DevOps, and others) — answer the same nine
questions and render from principles. The DSB rules are constant; only the expression
changes.

### 5.3 Review

**Use when** the user supplies a pipeline file, workflow, architecture description, or
repository to assess.

Procedure:

1. Build the Workload Profile **from what the pipeline itself reveals** — languages,
   artifacts, deploy targets, and platform are usually inferable from the file. Facts
   read out of a pipeline are stated facts, not inferences.
2. Build the Control Plan as normal.
3. Build the **Observed Control Set** — what the pipeline actually does. Identify each
   security-relevant step and the capability it provides.
4. Diff Observed against Plan.

Finding types:

| Finding | Meaning |
|---|---|
| **SATISFIED** | Present, correctly placed, correctly enforced |
| **MISSING** | Applicable control absent |
| **MISPLACED** | Present but at a technically invalid stage (image scan after push; SCA against a packaged artifact; DAST before deploy) |
| **WEAK** | Present but non-blocking with no recorded exception |
| **DUPLICATE** | Two tools covering one capability |
| **PIPELINE-RISK** | The CI/CD configuration is itself the defect (`DSB-SRC-*`, `DSB-ID-*`, `DSB-SC-002`, `DSB-EXC-003`) |
| **NOT APPLICABLE** | Explicitly documented with reason |

Every finding carries: rule ID, what was observed, why it matters, and concrete
remediation.

**Always check these explicitly** — they are common, high-impact, and easy to miss:

- Security steps neutralized by `|| true`, `continue-on-error`, `catchError` (DSB-EXC-003)
- Third-party actions or plugins on mutable tags (DSB-SC-002)
- Untrusted fork triggers with access to secrets (DSB-SRC-003)
- Static long-lived cloud credentials where federation is available (DSB-ID-001)
- Container image scanned after push rather than before (DSB-SCAN-004)
- Rebuild per environment rather than promotion (DSB-DEPLOY-002)
- Deployment by mutable tag rather than digest (DSB-ART-004)

Order findings by severity, not by rule number. Lead with what would actually be
exploited.

---

## 6. Rules of engagement

- **Teach, do not just answer.** Explain the engineering reason behind each placement
  and enforcement decision. Cite rule IDs and framework mappings.
- **Never recommend a vendor as a requirement.** DSB requires capabilities.
- **Never introduce a tool for a capability already covered.**
- **Never mark something applicable "to be safe."** Unfounded controls are exactly the
  bloat this methodology exists to prevent.
- **Never silently omit an N/A.** State it with its reason.
- **Distinguish N/A from undetermined.** They are different outcomes.
- **Say what you do not know.** A partial plan plus precise questions beats a
  complete-looking plan built on assumptions.
- **Never propose active DAST against production** without explicit authorization.
- **Respect ownership boundaries.** A control owned by another governed process is
  DELEGATED, not missing. Do not duplicate it.
- **Enforcement provenance is mandatory.** Say whether a level is the DSB default or
  the organization's policy.

Where a rule cites DSB curriculum modules, mention them by name. This skill implements
DSB teaching; it does not replace it.

---

## 7. Worked examples

### 7.1 Existing enterprise toolchain (Advise)

**Input:** *"We use Jenkins, Java, Maven, Artifactory, Checkmarx, Black Duck, Prisma
Cloud, and OpenShift. How should our pipeline be designed?"*

**Correct outcome:** Checkmarx → `sast` REUSE. Black Duck →
`software-composition-analysis` REUSE. Prisma Cloud → `container-image-scanning`
REUSE. Artifactory satisfies `artifact-integrity-verification` (DSB-ART-001).
`sbom-generation` is a GAP — but check whether Black Duck already emits CycloneDX
before recommending anything new.

**Zero new scanners.** Adding Trivy alongside Prisma Cloud, or Snyk alongside Black
Duck, is a defect under principles 5–7.

Undetermined, and therefore asked rather than assumed: whether automated tests exist,
who owns secret scanning, whether they author IaC, their enforcement posture, their
promotion model, and how Jenkins authenticates to Artifactory and OpenShift.

### 7.2 Terraform-only repository (N/A handling)

**Input:** *"Terraform-only repo. No application code, no containers."*

**Correct outcome:** DSB-IAC-001 and DSB-IAC-004 apply. DSB-TEST-002 applies.
DSB-SCAN-001 (SAST) is **N/A — no first-party application code**. DSB-SCAN-002 (SCA)
is **N/A — no application dependency tree**. DSB-SCAN-004 is **N/A — no container
artifact**. DSB-SCAN-006 (DAST) is **N/A — no running application surface**.

Do not invent an application build phase. A Terraform repository's Build phase is plan
generation, and that is a complete and correct answer.

### 7.3 Neutralized control (Review)

**Observed:**

```groovy
stage('Security') {
    sh 'trivy image myapp:latest || true'
}
```

**Finding: PIPELINE-RISK / WEAK — DSB-EXC-003, DSB-SCAN-004, DSB-ART-004.**

Three defects in one line. `|| true` means the scan never fails the build, so the
control is decorative while appearing to enforce. The image is referenced by mutable
tag `latest`, so the scanned artifact and the deployed artifact may differ. And if this
runs after push, the vulnerable image is already pullable.

**Remediation:** remove `|| true`; set an explicit severity threshold that fails the
build; scan by digest before push; route any accepted findings through a recorded
DSB-EXC-001 exception with an owner and expiry.
