# Example — Review: a non-compliant workflow

What Review mode produces when pointed at a pipeline with real defects.

## Input

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

      - uses: some-vendor/setup-toolchain@v2

      - run: npm install && npm run build

      - run: docker build -t myapp:latest .
      - run: docker push myapp:latest

      - run: trivy image myapp:latest || true

      - run: |
          aws ecs deploy --service myapp-prod --image myapp:latest
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET }}
```

## Observed Control Set

| Capability | Observed | Assessment |
|---|---|---|
| `container-image-scanning` | Trivy, post-push, non-blocking | WEAK + MISPLACED |
| `sast` | absent | MISSING |
| `software-composition-analysis` | absent | MISSING |
| `secret-scanning` | absent | MISSING |
| `automated-testing` | absent | MISSING |

## Findings

Ordered by what would actually be exploited, not by rule number.

### 1. CRITICAL — Untrusted code executes with production credentials

**DSB-SRC-003** (BLOCK) · **DSB-ID-002** (BLOCK) · **DSB-ID-004** (BLOCK)

`pull_request_target` runs in the context of the base repository **with access to
secrets**, and this workflow explicitly checks out the pull request head. Any person
who can open a pull request can execute arbitrary code with production AWS
credentials.

This requires no vulnerability. It is the configuration working as designed, and it
is the single most serious finding here.

**Remediation.** Use `pull_request` for untrusted contributions — it has no secret
access. If a workflow genuinely needs both untrusted code and secrets, split it: an
unprivileged job builds, a separate privileged job consumes the result without
executing untrusted code. Separately, production credentials must never be reachable
from a pull-request-triggered workflow at all (DSB-ID-004).

### 2. CRITICAL — Static long-lived cloud credentials

**DSB-ID-001** (WARN) · **DSB-ID-003** (BLOCK)

`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are long-lived secrets. Combined with
finding 1, they are exposed to anyone who can open a pull request. They do not
expire, and rotation is manual.

**Remediation.** Replace with OIDC federation and a role scoped to the specific
service and environment. Delete the static keys afterward — leaving them in place
preserves the exposure.

### 3. HIGH — The security control is decorative

**DSB-EXC-003** (BLOCK) · **DSB-SCAN-004** (BLOCK)

```
trivy image myapp:latest || true
```

`|| true` discards the exit code. The scan runs, prints findings, and never fails the
build. This is worse than having no scanner: it manufactures assurance. A reviewer
sees a scanning step and concludes images are gated. They are not.

**Remediation.** Remove `|| true`. Set an explicit severity threshold that fails the
build. If specific findings must be accepted, record a DSB-EXC-001 exception with a
named owner and an expiry date — not an inline suppression.

### 4. HIGH — Image scanned after it is already published

**DSB-SCAN-004** (BLOCK) — MISPLACED

The image is pushed, *then* scanned. Even with the exit code fixed, the vulnerable
image already exists in the registry and can be pulled by anything watching it.

**Remediation.** Scan the local image before `docker push`. Push only on success.

### 5. HIGH — Deployment by mutable tag

**DSB-ART-004** (BLOCK) · **DSB-DEPLOY-002** (BLOCK)

Everything references `myapp:latest`. Tags are mutable, so the artifact scanned and
the artifact deployed are not provably the same. Every scan result is a claim about
something that may no longer exist under that name.

**Remediation.** Capture the digest at push and deploy by digest.

### 6. HIGH — Third-party components on mutable references

**DSB-SC-002** (BLOCK)

`actions/checkout@main` and `some-vendor/setup-toolchain@v2` are both mutable. A
third party can change what executes inside this pipeline, with its credentials,
with no change on your side. `@main` is the worst case — it tracks a branch.

**Remediation.** Pin every third-party action to a full commit SHA.

### 7. MEDIUM — Dependencies resolved without a lockfile

**DSB-BUILD-002** (BLOCK)

`npm install` resolves fresh and may write a different tree than the lockfile
records. The same commit can produce different artifacts on different days.

**Remediation.** `npm ci`.

### 8. MEDIUM — No testing before delivery

**DSB-TEST-001** (BLOCK)

No test execution. If the project genuinely has no tests, that is an honest finding
rather than something to paper over — do not manufacture tests to populate the phase.

### 9. MEDIUM — Missing source-layer scanning

**DSB-SCAN-001** (BLOCK) · **DSB-SCAN-002** (BLOCK) · **DSB-SCAN-003** (BLOCK)

No SAST, no composition analysis, no secret scanning. Given a JavaScript codebase
with npm dependencies, all three are applicable.

**Before adding tools:** check whether the organization already owns these
capabilities. If an existing product covers SAST or SCA, use it. DSB requires the
capability, not a new purchase.

### 10. LOW — No evidence retention or findings routing

**DSB-EVD-001** (REPORT) · **DSB-EVD-003** (REPORT)

Scan output exists only in build logs. Nothing is retained against the artifact, and
no finding reaches an owning team. This is the most common reason a technically
correct pipeline produces no security improvement.

## Not applicable

- **DSB-IAC-\*** — no infrastructure-as-code observed in the delivery process.
- **DSB-SCAN-007** — no API specification observed; cannot determine whether an API
  surface exists.

## Undetermined

`artifact-signing` and `build-provenance` require a stated organizational
requirement. Not marked applicable, and not dismissed.

## Remediation order

Findings 1 and 2 first, and they are urgent — together they expose production to
anyone who can open a pull request. Fixing them is a configuration change, not a
project.

Then 3 through 6, which restore the integrity of the delivery path. Then the missing
controls, checking for existing organizational capabilities before adopting anything
new.
