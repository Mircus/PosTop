# PosTop Repo Refresh Report

Executed against the "PosTop Repo Refresh — Claude Code Worklist"
(P0–P6), aligning the repository with the September 2026 survey
*"Positive Topology and Feasible Refinement: Forcing Matrices,
Positivity, and Information"* (Mannucci & Sambin,
`docs/Positive_Topology_and_Feasible_Refinemen.pdf`).

## Files changed

**New:**
- `src/postop/certificates.py` — `CoverCertificate`, `PositivityCertificate`,
  `CounterexampleCertificate`, `CompatibilityCertificate`,
  `BudgetCertificate`, `DiscriminatorSuggestion`
- `src/postop/formal.py` — `FormalPositiveTopology` (primitive/pointfree case)
- `src/postop/evaluate.py` — `Evaluator` / `EvaluationResult` facade
- `src/postop/adapters/__init__.py`, `src/postop/adapters/guardrail.py` —
  the LLM-guardrail adapter, moved out of core
- `tests/test_costs.py`, `tests/test_formal.py`, `tests/test_properties.py`
- `docs/ARCHITECTURE.md`, `CHANGELOG.md`, `REPO_REFRESH_REPORT.md` (this file)
- `assets/postop-logo.svg`, `assets/postop-logo.png`

**Modified:**
- `README.md` — full rewrite (paper-aligned structure, implemented/
  experimental/programmatic table, corrected KG comparison)
- `src/postop/core.py` — canonical operator names, `IncidenceSystem`,
  certificate-returning `explain_*`, singleton reconstruction, deprecated
  aliases
- `src/postop/operators.py` — updated to canonical names + deprecated aliases
- `src/postop/costs.py` — added `CostAnnotatedIncidence`,
  `ThresholdSemantics`, `suggest_next_test`; legacy `CostForcing`/
  `CostPosTop` kept, documented as legacy/experimental
- `src/postop/llm.py` — now a deprecated shim re-exporting from `adapters`
- `src/postop/__init__.py` — exports everything; imports the guardrail
  from `adapters` directly (not via the deprecated `llm` shim) so a plain
  `import postop` never itself warns
- `examples/medical.py`, `examples/llm_guardrail.py` — canonical names;
  the guardrail example now has explicit `encode_hypothesis`/
  `encode_observation_state` functions
- `tests/test_core.py`, `tests/test_operators.py` — canonical names,
  plus new regression tests (formal-closed fixed point, singleton
  reconstruction, deprecated-alias delegation)
- `pyproject.toml` — `[project.urls]` added (canonical repo URL),
  version `0.1.0` → `0.2.0`
- `CITATION.cff` — repository URL, corrected year (2026), explicit note
  that no arXiv ID/DOI is claimed until one exists
- `docs/REPRODUCIBILITY.md` — canonical URL, new notebook names, a
  Windows `PYTHONIOENCODING` note (examples print Unicode symbols)
- `.github/workflows/tests.yml` — added a package-build smoke-test job
- `.gitignore` — added `build/`, `dist/`, `*.egg-info/`
- `notebooks/*.ipynb` — renamed to paper vocabulary and rewritten to
  canonical names (see below); all four **executed headlessly** via
  `nbconvert` as part of this refresh, not just written

**Removed:**
- `src/postop.egg-info/` — a stray committed build artifact (should never
  have been tracked); now covered by `.gitignore`
- `docs/positive_topology_survey_v2.pdf` / `.tex` — the old, superseded
  paper draft, once the new draft (`docs/Positive_Topology_and_Feasible_Refinemen.pdf`)
  was confirmed to be the canonical one (removed in a follow-up cleanup
  pass after the initial refresh; see CHANGELOG.md)
- `docs/actionlist.md` — the previous (Codex) repo-refresh worklist;
  fully completed and superseded by this file and `CHANGELOG.md`
- `assets/logo.png` / `.svg` — the original logo, superseded once the
  maintainer uploaded `assets/posttoplogo.jpg` and pointed the README at it
- `assets/postop-logo.png` / `.svg` — the logo generated during this
  refresh's first pass; also superseded by `assets/posttoplogo.jpg` and
  removed once it was clear it was unreferenced dead weight rather than
  a useful spare

**Notebook renames** (content also updated to canonical operator names):
- `01_basics_ext_int_hit_sel_j.ipynb` → `01_forcing_and_adjunctions.ipynb`
- `02_medical_diagnosis_and_explanations.ipynb` → `02_medical_cover_positivity.ipynb`
- `03_costs_and_budgets.ipynb` → `03_budgeted_forcing.ipynb` (now includes
  an explicit non-monotonicity demonstration)
- `04_llm_guardrail_pattern.ipynb` → `04_ai_certificates.ipynb`

**Deliberately left untouched** (see "Not implemented / out of scope"):
`status.md`, `docs/MECHANIZATION_STATUS.md`, `scripts/no_sorry.py` (see
below) — an unrelated, in-progress Lean/RB-TT effort that predates and
is unrelated to this worklist; not PosTop-repo clutter, just a separate
concern living in the same repo.

## API changes

| Old | New (canonical) | Old still works? |
|---|---|---|
| `PosTop` | `IncidenceSystem` | Yes — `PosTop = IncidenceSystem` alias |
| `.Ext(U)` | `.ext(U)` | Yes — deprecated alias, warns |
| `.Int(E)` | `.box(E)` | Yes — deprecated alias, warns |
| `.Hit(C)` | `.diamond(C)` | Yes — deprecated alias, warns |
| `.Sel(U)` | `.rest(U)` | Yes — deprecated alias, warns |
| `.J(U)` | `.reduction(U)` | Yes — deprecated alias, warns |
| `.j(U)` | `.saturation(U)` | Yes — deprecated alias, warns |
| `OperatorSuite.Int/hit/sel/j` | `.box/.diamond/.rest/.reduction` | Yes — deprecated aliases, warn |
| `explain_cover()` → dict | → `CoverCertificate` (has `.to_dict()`) | **Breaking** for dict-index callers (`["holds"]`); attribute access (`.holds`) is the new form. Both call sites in this repo (`operators.explain_chain`, tests) were updated. |
| `check_compatibility()` → `Optional[S]` or raises | Unchanged signature/behavior (now implemented via the new `compatibility_certificate()`) | Yes — no change to this method's contract |
| `postop.llm` | `postop.adapters.guardrail` (or `postop`, still re-exported) | Yes — `postop.llm` is a shim that warns on import |

New, additive-only: `FormalPositiveTopology`, all of
`postop.certificates`, `CostAnnotatedIncidence`, `ThresholdSemantics`,
`Evaluator`/`EvaluationResult`, `IncidenceSystem.to_formal_positive_topology()`,
`reconstruct_forcing_from_ext()`/`reconstruct_forcing_from_diamond()`,
`compatibility_certificate()`, `explain_positive()`.

**One genuine behavior change worth flagging explicitly:**
`explain_cover()` returning a certificate object instead of a plain dict
is a breaking change for any external caller doing
`explain_cover(...)["holds"]`. Nothing else in this refresh changes
existing return values or semantics — every other change is additive or
alias-preserving.

## Deprecated aliases

All deprecated aliases emit `DeprecationWarning` and delegate to the
canonical implementation (see table above). None will be removed in this
release; a future major version can drop them once downstream callers
have migrated. `postop/__init__.py` itself never triggers a warning on
plain `import postop` — only calling a deprecated method, or explicitly
`import postop.llm`, does.

## Test count before / after

- **Before:** 17 tests across 3 files (`test_core.py`, `test_operators.py`,
  `test_llm.py`). `postop.costs` (`CostForcing`/`CostPosTop`) had **zero**
  test coverage.
- **After:** 44 tests across 6 files (added `test_costs.py`,
  `test_formal.py`, `test_properties.py`; expanded `test_core.py` and
  `test_operators.py`). All pass, no network access, no external
  services. Verified in a clean venv (`pip install -e .[dev]`, Python
  3.11) and via a built-wheel smoke install.
- New coverage specifically closes gaps the worklist called out: the
  correct formal-closed fixed-point condition (vs. mere contractivity),
  singleton reconstruction (Theorem 8.1) from both `ext` and `diamond`,
  cover/positivity budget non-monotonicity in both directions (with a
  third case showing positivity *gaining* a witness at higher budget),
  and both adjunction laws + saturation/reduction closure-operator laws
  checked on ~30 random finite incidence tables each (plain `random`,
  no new dependency).

## Remaining research-only TODOs

These are intentionally **not implemented** — they are the subject of
the paper's own planned follow-up article, and the worklist explicitly
says not to promote them to established API:

- General `V`-valued threshold semantics with coherent threshold maps
  (only a bare `Protocol` skeleton exists: `ThresholdSemantics`)
- Resource-indexed positive sites
- TROPOS
- RB-CwF / graded logical semantics
- A recursively-defined budget-indexed logical satisfaction judgement
  (`s ⊩_b φ`, survey §10.1) — no syntax or semantics for this exists in
  the codebase, nor should it yet

## Items intentionally not implemented, and why

- **Repo-wide typing-syntax modernization (PEP 585/604) was NOT done.**
  `ruff check .` reports ~199 `UP006`/`UP045`/`UP035` findings ("use
  `list`/`set`/`X | None` instead of `List`/`Set`/`Optional[X]`"). I
  verified this is **pre-existing**: the original, unmodified
  `src/postop/core.py` alone already had 52 such findings before this
  refresh touched it. Fixing this repo-wide is a large, purely
  mechanical, non-functional diff that isn't in the worklist and isn't
  required for any acceptance criterion beyond "CI is green" — and
  making `lint.yml` green would require either this sweep or relaxing
  ruff's ruleset, both of which are judgment calls for the maintainer,
  not something to do silently. `tests.yml` (pytest + the new build
  smoke test) is green; `lint.yml` was red before this refresh and
  remains red, for the same pre-existing reason, unchanged by this work.
- **`docs/positive_topology_survey_v2.pdf`/`.tex`** (the old, superseded
  paper draft, containing the old `mirco-mannucci/postop` URL and a
  `v0.1.0` tag reference) was initially left in place rather than edited
  — it's someone's academic manuscript source, and rewriting paper prose
  is outside a software-repo-refresh mandate. In a follow-up cleanup
  pass, the maintainer asked for stale files to be removed outright once
  the September 2026 PDF was confirmed canonical, so both files were
  deleted rather than edited (git history still has them if needed).
- **Hypothesis (property-based testing library) was NOT added.** Used
  plain, seeded `random` sampling instead (`tests/test_properties.py`),
  per the worklist's own "keep dependencies lightweight" instruction.
  Straightforward to swap in later if wanted.
- **Notebook CI execution was NOT added to `.github/workflows/`.** All
  four notebooks were executed headlessly and verified to pass during
  this refresh (see below), but the worklist explicitly says to keep
  notebook execution out of mandatory CI unless stable — I judged a
  fresh rewrite doesn't yet have enough runs under its belt to promise
  CI stability (kernel/timeout flakiness on CI runners is common for a
  first pass).
- **Did not touch `status.md`, `docs/MECHANIZATION_STATUS.md`,
  `scripts/no_sorry.py`.** These describe an unrelated, in-progress Lean
  mechanization effort (RB-TT/RB-MLTT — a `src/RBTT/` Lean tree that
  does not exist in this checkout) that predates and is unrelated to
  this worklist. They were already present as uncommitted/untracked
  changes when this refresh began; touching them wasn't requested and
  risks interfering with separate, currently-in-progress work.
- **No `LICENSE` file exists in this repository**, despite
  `pyproject.toml`/`CITATION.cff` declaring MIT. I did not fabricate one
  — adding a real license file is the maintainer's call, not something
  to infer silently. README now says "if present" rather than asserting
  it unconditionally.
- **No git tag was created**, per the worklist's explicit instruction
  ("do not choose/tag a version without checking existing tags first").
  The repository currently has zero tags; `0.2.0` in `pyproject.toml`/
  `CITATION.cff` is the recommended next version, left for the
  maintainer to actually tag/release.
- **No arXiv ID or DOI was added anywhere** (`CITATION.cff`, README) —
  none exists yet for the September 2026 draft; inventing one was
  explicitly forbidden by the worklist.

## Verification performed

- `pytest -q`: 44/44 passed, clean venv, Python 3.11.
- `python -m build` + install the built wheel into a separate clean venv
  + `import postop` — succeeds (matches the new CI build job).
- `python examples/medical.py` and `python examples/llm_guardrail.py`
  run to completion with correct output (Windows console needs
  `PYTHONIOENCODING=utf-8` for the Unicode symbols — now documented in
  `docs/REPRODUCIBILITY.md`).
- All four notebooks executed headlessly via
  `jupyter nbconvert --execute` with a 60s timeout, zero errors. The
  budgeted-forcing notebook's non-monotonicity cell was manually
  inspected to confirm it actually demonstrates a True→False flip (an
  earlier draft of that notebook had a cost value that accidentally made
  both budgets agree — caught and fixed during this verification pass,
  not left in).
- `ruff check .` run and its (pre-existing, unrelated) failures
  characterized — see above.

## HYRI integration recommendation

Per the worklist: **do not** import PosTop into HYRI Core, and **do
not** couple PosTop to HYRI. The certificate types added in this refresh
(`postop.certificates`) are the intended extraction surface — pure,
deterministic, JSON-serializable, with no PosTop-internal types leaking
through `to_dict()`.

Recommended HYRI candidates, matching the worklist's own list, and now
concretely backed by code in this repo:

| Certificate | Produced by | Suggested HYRI consumer |
|---|---|---|
| `CoverCertificate` | `IncidenceSystem.explain_cover` | Validator/Critic — entailment-style validation over an explicit representation |
| `PositivityCertificate` | `IncidenceSystem.explain_positive` | Validator/AdoptionPolicy — proves a candidate survives a given evidence/constraint envelope |
| `CompatibilityCertificate` | `IncidenceSystem.compatibility_certificate` / `FormalPositiveTopology.validate_compatibility` | Validator — whether evidence survived a proposal's refinement/remediation |
| `BudgetCertificate` | `CostAnnotatedIncidence.budget_certificate` | Routing/observability — which checks were affordable, which weren't |
| `DiscriminatorSuggestion` | `CostPosTop.suggest_next_test` | Routing/tool-choice — a heuristic, explicitly not claimed optimal |

Before any real extraction, treat the interfaces above as tested-but-
young (this is their first release under the canonical names) rather
than a stable, frozen protocol — the worklist's own instruction to
"extract a stable certificate protocol into HYRI only after the
refreshed interfaces are tested" should mean *more* mileage on this
repo's own test suite and real usage first, not a fixed waiting period.

HYRI Core keeps authority over orchestration, critic/arbiter roles,
validation, adoption, persistence/events, human escalation, permissions,
and budget *enforcement* (as opposed to budget *evidence*, which is what
`BudgetCertificate` supplies) — nothing in this refresh changes that
boundary or attempts to.
