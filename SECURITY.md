# Security Policy

## Reporting a vulnerability

**Do not open a public issue.**

Report privately through either:

- [GitHub private vulnerability reporting](https://github.com/devsecblueprint/devsecops-claude-skill/security/advisories/new)
- The [DSB Discord](https://discord.gg/enMmUNq8jc) — contact a maintainer directly, not a public channel

Expect an acknowledgement within 5 business days.

## What counts as a vulnerability here

This repository ships guidance, not a running service. The interesting failure modes
are different from a typical application, and two of them matter more than anything
else:

**Unsafe generated configuration.** A pipeline snippet in `SKILL.md` or `examples/`
that would introduce a real weakness if a user adopted it — a leaked secret pattern,
an over-permissioned deployment identity, an unpinned action, a scanner whose exit
code is discarded so findings cannot block. These are security defects in the product
even though nothing here executes.

**Guidance that neutralizes a control.** A rule, example, or explanation that causes
an agent to recommend disabling, bypassing, or silently downgrading a security control
without an explicit, recorded exception.

Also in scope: prompt-injection paths that make the skill emit attacker-chosen
pipeline configuration, and anything in `tools/` that executes untrusted input or
writes outside the repository.

## Out of scope

- Vulnerabilities in third-party products named as illustrative examples. Tool names
  in this repository are never requirements — report those upstream.
- Disagreement with a rule's enforcement default. That is an engineering discussion:
  open a normal issue.
- Findings in the DSB platform repository. Report those to
  [devsecblueprint/devsecblueprint](https://github.com/devsecblueprint/devsecblueprint).

## Disclosure

We will confirm the issue, agree a fix timeline with you, and credit you in the
release notes unless you would rather stay anonymous. Please give us a reasonable
window to ship a fix before publishing.
