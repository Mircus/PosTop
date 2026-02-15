# Status — PosTop ActionList Progress

## Completed so far

- **Repo hygiene / packaging**
  - Removed stray brace-directory `postop/{src,examples,docs,tests}` and the duplicated `files (19)/` paper folder, leaving a single canonical `docs/`.
  - Upgraded `pyproject.toml` metadata (no `xxx` placeholders); optional dev extras now install cleanly via `pip install -e .[dev]`.
  - Converted the legacy unittest suite into pytest (`tests/test_core.py`) and ensured tests import the package normally.

- **Core fixes**
  - `ForcingRelation.add()` now merges observable profiles instead of overwriting them; backward edges stay consistent and new helper methods (`__len__`, `__contains__`, `__iter__`) make the structure iterable.
  - `PosTop.Ext(U)` now unions via the backward index for clarity/performance.

- **Explainability / helper modules**
  - Added `postop.operators.OperatorSuite` for tracing Ext/Int/Hit/Sel/J and minimal cover explanations, plus pytest coverage.
  - Added `postop.llm` with `ClaimNormalizer` and `PosTopGuardrail`, moving the guardrail logic out of the example.
  - Updated examples to rely on installed package imports (no `sys.path` hacks) and wired them to the new guardrail helper.

- **Docs + citation**
  - README now has a copy/paste install guide (venv + editable install), accurate tree, and citation section referencing `CITATION.cff`.
  - New `docs/REPRODUCIBILITY.md` gives a runbook for install, examples, notebooks (once added), and tests.
  - Added `CITATION.cff` covering both the software package and the paper draft.

- **Testing**
  - Verified with `python3 -m venv .venv && source .venv/bin/activate && pip install -e .[dev] && pytest -q` (temp venv removed afterwards); all tests pass (18 total).
  - Added four canonical notebooks under `notebooks/` and documented their `nbconvert --execute` usage.

- **CI / Tooling**
  - Added branding assets (`assets/logo.svg`, `logo.png`) and surfaced the SVG atop the README.
  - Created GitHub Actions for tests (`.github/workflows/tests.yml`) and linting (`.github/workflows/lint.yml`).
  - Added `tox.ini` for local py39–py312 test matrices and `.pre-commit-config.yaml` (ruff, black, mypy); README and reproducibility guide explain how to run them.

## Next up

- Wire notebook execution (`nbconvert --execute`) into CI (optional) and ensure ActionList P2 acceptance requires they run headlessly.
- Finish remaining P4/P5 items: README polish (Quick Start already updated), pre-commit badge optional, release tag v0.1.1 once tests/notebooks are green.
