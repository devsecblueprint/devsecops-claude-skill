# Machine-readable rule catalog

**The normative rule catalog is [`SKILL.md`](../SKILL.md) §3.** All 42 rules are
defined there, and that file is what an agent loads. Nothing in this directory is
required to use the skill.

These YAML files are a *projection* of that catalog into the structure defined by
[`../schema/rule.schema.json`](../schema/rule.schema.json), for the Control Plan
evaluator. Authoring happens in `SKILL.md`; a rule is added here only once its
applicability can be expressed in the schema's predicate grammar without loss.

## Current coverage

| | |
|---|---|
| Rules in `SKILL.md` §3 | 42 |
| Extracted here | 6 |

`tools/validate_skill.py` reports this gap on every run. That is intentional — the
number should be visible, not silently accepted.

## Why not all 42

Extraction is deliberately incomplete rather than approximated. An applicability
predicate that is *close* to the prose is worse than no predicate: it produces
confident, wrong `NOT_APPLICABLE` results in output that lands in audit records.

Three groups are blocked, and they need design decisions, not transcription:

**Array membership and cardinality.** The atom grammar supports scalar equality,
`in`, and `exists`. It cannot yet say "includes production" or "more than one
environment" — needed by `DSB-IAC-004`, `DSB-DEPLOY-002`, `DSB-DEPLOY-003`,
and `DSB-ID-004`.

**Conditions outside the Workload Profile vocabulary.** Some rules apply when the
organization states a policy, or when a platform supports a feature — neither is a
closed-vocabulary profile field today. Affects `DSB-SCAN-008`, `DSB-IAC-003`,
`DSB-ART-003`, and the reachability conditions in `DSB-SCAN-006` and `DSB-SCAN-007`.

**Resolution-state predicates.** `DSB-EVD-003`, `DSB-EXC-001`, and `DSB-EXC-002`
apply based on how *other* controls resolve — whether anything came back `REUSE`,
`GAP`, or `BLOCK`. That is deliberately not expressible here. Applicability answers
"does this risk exist for this workload?"; resolution answers "who satisfies it?"
Mixing them destroys the `DELEGATED` outcome, and both
[`CONTRIBUTING.md`](../docs/CONTRIBUTING.md) and the validator forbid it. These rules
need a second evaluation pass, not a predicate.

## Adding a rule here

1. Author it in `SKILL.md` §3 first — that is the source of truth.
2. Confirm its applicability is expressible with no loss of meaning. If it is not,
   leave it out and extend the schema deliberately instead.
3. Write `rules/<phase>/<ID>.yaml` against the schema.
4. Run `python -m pytest` — `tests/test_rule_schema.py` validates every file here.

Tooling examples belong to capabilities, not rules: a rule names its `capability`,
and [`../references/capabilities.yaml`](../references/capabilities.yaml) carries the
illustrative products. This keeps vendor names in exactly one place.
