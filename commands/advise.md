---
description: Advise on where security controls belong in a delivery pipeline, given a stack, constraints, and the tools an organization already owns.
argument-hint: "[your stack, constraints, and existing security tooling]"
---

Read `${CLAUDE_PLUGIN_ROOT}/SKILL.md` and apply it in **Advise mode** (§5.1).

The user's situation:

$ARGUMENTS

If that is empty, ask what they are building, on what CI/CD platform, and which
security products the organization already owns — then continue.

Work the four-step procedure in §2 to a Control Plan, then produce the §5.1 output
structure. Two things carry most of the value here, so do not let them slip:

- Resolve every capability the organization already owns to **REUSE**, naming the
  tool. Recommending a second scanner for a covered capability is a defect, not
  thoroughness.
- Emit the **Not applicable** and **undetermined** sections in full. What does not
  apply, and what you could not determine, are deliverables — not omissions.

Do not emit pipeline configuration in this mode. If they want that, use
`/devsecops-engineer:design`.
