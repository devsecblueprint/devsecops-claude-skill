# Maintainers

The DSB DevSecOps Engineering Skill is owned and maintained by
**The DevSec Blueprint LLC**.

## Ownership

| | |
|---|---|
| **Owner** | The DevSec Blueprint LLC |
| **Organization** | [github.com/devsecblueprint](https://github.com/devsecblueprint) |
| **Community** | [Discord](https://discord.gg/enMmUNq8jc) |
| **License** | PolyForm Noncommercial 1.0.0 |
| **Commercial licensing** | [docs/legal/COMMERCIAL-LICENSING.md](docs/legal/COMMERCIAL-LICENSING.md) |

This skill is an implementation of DSB knowledge and standards. It is not the source
of those standards — the DSB curriculum is. Where this skill and the curriculum
disagree, the curriculum wins and the skill is a defect.

## Maintainer responsibilities

**Guard the vendor-neutrality boundary.** The most likely way this repository degrades
is a well-intentioned pull request that makes a specific product a requirement. Every
rule change gets checked against this.

**Keep the skill loadable as one file.** `SKILL.md` must remain self-contained. A
contribution that splits knowledge into files a user has to also download breaks the
distribution model.

**Keep methodology and curriculum aligned.** When DSB curriculum changes, review the
rule catalog for rules that now contradict it, and refresh
`references/dsb-curriculum.yaml`.

**Protect rule ID permanence.** Retired IDs are never reused. Review output containing
rule IDs ends up in customer audit records.

**Verify behavior, not just diffs.** A `SKILL.md` change that reads well but does not
change agent behavior has not landed. Test against a live agent before merging.

## Release and review

- Rule additions and changes require maintainer review.
- Methodology changes originate in the DSB curriculum, not here.
- Breaking changes to rule IDs are not permitted.
- CI must pass on every pull request.

## Reporting a security issue

Do not open a public issue for a security problem in this repository or in guidance it
produces. Contact the maintainers through the
[DSB Discord](https://discord.gg/enMmUNq8jc) or the commercial licensing contact.

## Related

- Origin issue: [devsecblueprint#180](https://github.com/devsecblueprint/devsecblueprint/issues/180)
- Platform repository: [devsecblueprint/devsecblueprint](https://github.com/devsecblueprint/devsecblueprint)
