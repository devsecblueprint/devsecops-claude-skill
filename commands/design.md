---
description: Generate implementation-ready CI/CD pipeline configuration with every security control placed, enforced, and annotated with its DSB rule.
argument-hint: "[what to build, target platform, and where it deploys]"
---

Read `${CLAUDE_PLUGIN_ROOT}/SKILL.md` and apply it in **Design / Generate mode** (§5.2).

What the user wants built:

$ARGUMENTS

Respect the completeness gate in §5.2 before generating anything. If the CI/CD
platform, languages, deployment targets, or artifact type are still unresolved, ask
for them and stop there. A plausible-looking pipeline built on guesses is worse than
a question, because it will be run.

Once the gate is met: build the Control Plan, answer the platform adapter contract
for the target platform, then render. Annotate every security step with the rule it
satisfies, and state which controls block and which only warn.

If the user is describing an existing pipeline rather than a new one, use
`/devsecops-engineer:assess` instead.
