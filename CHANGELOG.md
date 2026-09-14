# Changelog

## 0.2.0 — Survey alignment refresh (unreleased)

Brings the repository into alignment with the September 2026 survey
*"Positive Topology and Feasible Refinement: Forcing Matrices,
Positivity, and Information"* (Mannucci & Sambin). See
`REPO_REFRESH_REPORT.md` for the full file-by-file account.

### Added
- Canonical operator names on `IncidenceSystem` (née `PosTop`):
  `ext`, `box`, `diamond`, `rest`, `saturation`, `reduction`. Old names
  (`Ext`, `Int`, `Hit`, `Sel`, `J`, `j`) kept as deprecated aliases.
- `FormalPositiveTopology` (`postop.formal`): the primitive/pointfree
  case, where cover and positivity are supplied as data and
  compatibility is validated as an axiom rather than derived as a
  theorem. `IncidenceSystem.to_formal_positive_topology()` bridges the
  two.
- `postop.certificates`: JSON-serializable `CoverCertificate`,
  `PositivityCertificate`, `CompatibilityCertificate`,
  `BudgetCertificate`, `CounterexampleCertificate`,
  `DiscriminatorSuggestion`. `explain_cover`/`explain_positive`/
  `compatibility_certificate` now return these instead of raw dicts.
- `CostAnnotatedIncidence` (`postop.costs`): the survey's minimal safe
  resource baseline — ground-truth forcing and verification cost as
  separate fields, `forces_within = forces AND cost <= budget`.
- `ThresholdSemantics` Protocol (`postop.costs`): an explicitly
  experimental/outlook-only skeleton for the survey's §9.3 generic
  enriched-value direction.
- `postop.evaluate.Evaluator`: a pure, deterministic
  cover+positivity(+budget) evaluation facade.
- `postop.adapters` package: the LLM-guardrail adapter moved out of core
  (`postop.llm` is now a deprecated shim), with explicit
  hypothesis/observation encoding parameters instead of implicitly
  treating claim strings as generators.
- Singleton reconstruction (`reconstruct_forcing_from_ext`,
  `reconstruct_forcing_from_diamond`), a formal-closed regression test
  distinguishing the fixed-point condition from mere contractivity, and
  budget non-monotonicity regression tests (`tests/test_costs.py`).
- `docs/ARCHITECTURE.md`.
- New `assets/postop-logo.svg` / `.png`.

### Changed
- README rewritten around the paper's actual structure and an explicit
  "implemented / experimental / programmatic" status table; dropped the
  categorical "knowledge graphs can't do X" framing in favor of the
  paper's "difference of emphasis" positioning.
- `pyproject.toml`: added `[project.urls]` pointing at the canonical
  repository (`https://github.com/Mircus/PosTop`); version bumped to
  0.2.0. No new git tag was created as part of this change — tagging a
  release is left to the maintainer.
- Notebooks renamed to paper vocabulary:
  `01_basics_ext_int_hit_sel_j.ipynb` → `01_forcing_and_adjunctions.ipynb`,
  `02_medical_diagnosis_and_explanations.ipynb` → `02_medical_cover_positivity.ipynb`,
  `03_costs_and_budgets.ipynb` → `03_budgeted_forcing.ipynb`,
  `04_llm_guardrail_pattern.ipynb` → `04_ai_certificates.ipynb`.
- CI (`tests.yml`) now also does a package build smoke test.

### Fixed
- All occurrences of the stale `mirco-mannucci/postop` remote and old
  `docs/positive_topology_survey_v2.pdf` reference updated to the
  canonical repository and the current survey PDF.
- `CITATION.cff` publication year and repository URL corrected; no
  arXiv ID or DOI is claimed until one actually exists.

### Deprecated
- `PosTop` class name → use `IncidenceSystem` (kept as an alias).
- `IncidenceSystem.Ext/Int/Hit/Sel/J/j` → use
  `ext/box/diamond/rest/reduction/saturation`.
- `OperatorSuite.Int/hit/sel/j` → use
  `OperatorSuite.box/diamond/rest/reduction`.
- `postop.llm` module → import from `postop.adapters` (or `postop`,
  which still re-exports the same names) instead.

## 0.1.0

Initial public snapshot (README/tests/CI/packaging pass; see
`docs/actionlist.md` for that pass's own worklist).
