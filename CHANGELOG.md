# Changelog

All notable changes to this project are documented here. This project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-08-16

Initial public release.

**Pre-1.0.** The rule catalog and the skill's output structure will evolve based on
real usage before 1.0. Rule *IDs* are the exception and are already stable: they
appear in review output that ends up in audit records, so a retired ID is deprecated,
never reused or renumbered.

### Added

- `SKILL.md` — the skill. Self-contained: 42 rules across 11 families, the
  Build → Test → Scan → Deploy methodology, the twenty baseline principles, and the
  Advise / Design / Review operating modes. Installing it needs this file and nothing
  else.
- Command entry points for Claude Code, under the `devsecops-engineer` plugin:
  - `/devsecops-engineer:advise` — where controls belong, given a stack and the tools
    already owned
  - `/devsecops-engineer:design` — implementation-ready pipeline configuration
  - `/devsecops-engineer:assess` — findings against an existing pipeline or repository
- Worked examples across four stacks — greenfield GitHub Actions, an enterprise
  Jenkins toolchain that introduces zero new scanners, a Terraform-only repository
  where twelve rules are Not Applicable, and a review of a pipeline with real defects.
- Framework mappings to NIST SSDF, SLSA, OWASP CI/CD, OWASP SAMM, and CNCF supply
  chain guidance, generated from the rule catalog into `docs/framework-mappings.md`.
- Machine-readable capability registry, curriculum snapshot, JSON Schemas for the rule
  and workload-profile structures, and a partial YAML projection of the catalog.
- `tools/validate_skill.py` and a pytest suite, both run in CI.

### Changed

- **License is now MIT** (was PolyForm Noncommercial 1.0.0). Commercial use no longer
  requires prior written authorization, and `docs/legal/COMMERCIAL-LICENSING.md` has
  been removed. DSB names, logos, and curriculum content remain outside the license —
  see `docs/legal/TRADEMARKS.md`.
- README rewritten as a product front door: what it is, why it exists, install, three
  prompts to try, and how the reasoning works.

[0.1.0]: https://github.com/devsecblueprint/devsecops-claude-skill/releases/tag/v0.1.0
