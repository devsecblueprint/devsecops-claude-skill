---
description: Assess an existing pipeline, workflow, or repository against DSB requirements and report findings ordered by what would actually be exploited.
argument-hint: "[path to a pipeline file or repository — defaults to this repository]"
---

Read `${CLAUDE_PLUGIN_ROOT}/SKILL.md` and apply it in **Review mode** (§5.3).

What to assess:

$ARGUMENTS

If that is empty, find the delivery pipelines in the current repository — CI/CD
configuration under `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`,
`azure-pipelines.yml`, or equivalent — and assess those.

Build the Workload Profile from what the pipeline itself reveals, then the Control
Plan, then the Observed Control Set, then diff them. Run the "always check these
explicitly" list in §5.3 — those findings are common, high-impact, and the ones most
often missed.

Order findings by severity, not by rule number. Lead with what an attacker would
reach first, not with the first control that happens to be absent. Every finding
carries the rule ID, what was observed, why it matters, and concrete remediation.
