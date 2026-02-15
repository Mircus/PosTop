# ActionList.md — Codex completion plan for PosTop (postop)

Goal: bring the repo to “arXiv + companion code” quality: reproducible examples, correct references, clean packaging/tests/CI,
and a minimal-but-coherent API that matches the paper.

## P0 — Repo hygiene + packaging correctness (must-do)

- [ ] **Delete/cleanup stray folders**
  - Remove `postop/{src,examples,docs,tests}/` (empty brace-dir).
  - Remove duplicate `files (19)/` (keep one canonical `docs/` copy of the paper sources).
  - Acceptance: `git status` clean; tree has no duplicates or brace-dirs.

- [ ] **Fix `project.urls` placeholders**
  - Replace `https://github.com/xxx/postop` with the real URL (or remove until known).
  - Acceptance: `pyproject.toml` has no `xxx` placeholders; README matches.

- [ ] **Make tests import the package correctly (no `sys.path` hacks)**
  - Replace unittest style + relative sys.path with pytest and normal imports.
  - Add `pyproject.toml` `dependencies` (empty is ok) but ensure `pip install -e .` works.
  - Update CI to run `pip install -e .[dev]` then `pytest`.
  - Acceptance: `pytest -q` passes from repo root in a clean venv.

- [ ] **Fix `ForcingRelation.add()` overwrite bug**
  - Current behavior overwrites `_forward[point]` but doesn’t remove old backward links.
  - Implement either:
    1) `add(point, observables)` = *merge* into existing profile, OR
    2) `set(point, observables)` (replace) + maintain backward index (remove old edges).
  - Acceptance: property-based test or explicit unit test demonstrates no stale backward edges.

- [ ] **Performance/clarity micro-fixes**
  - Implement `Ext(U)` as `⋃_{a∈U} extension(a)` using `_backward` (faster and clearer).
  - Add `__len__`, `__contains__` or iter helpers as needed.
  - Acceptance: same behavior, faster on large `|X|`.

## P1 — Paper ↔ repo integration for arXiv readiness

- [ ] **Add a “Software & Reproducibility” appendix to the LaTeX**
  - New appendix section: how the forcing matrix is encoded in code, what `covers`/`positive` correspond to,
    and how to run each example (CLI commands).
  - Include a *stable* link target (release tag / commit hash) once the repo is public.
  - Acceptance: PDF contains a clear appendix with commands and expected outputs.

- [ ] **Fix citations: currently references exist but are not cited**
  - Add `\cite{...}` calls in the relevant sections (Intro, positivity, reconstruction, costs, related work).
  - Ensure bibitems are correct:
    - Sambin, *Positive Topology* (OUP) (verify year/ISBN).
    - Ciraulo–Sambin (JSL 2012) “constructive Galois connection…”
    - Coquand–Sambin–Smith–Valentini (APAL 2003) “Inductively generated formal topologies”
    - Ciraulo–Vickers (2016) “Positivity relations on a locale”
  - Acceptance: PDF compiles with citations appearing in-text; no unused bibitems.

- [ ] **Add a top-level `CITATION.cff` + keep README BibTeX consistent**
  - Put the *paper* citation and the *software* citation (separately).
  - Acceptance: `CITATION.cff` present; README “Citation” matches.

- [ ] **Create a minimal “Reproduce” guide**
  - `docs/REPRODUCIBILITY.md` with:
    - install (editable)
    - run examples
    - run notebooks
    - run tests
  - Acceptance: a new user can reproduce with copy/paste.

## P2 — Examples → Notebooks (make the project “showable”)

Add `notebooks/` with 4 canonical notebooks (keep them small, fast, deterministic):

- [ ] `01_basics_ext_int_hit_sel_j.ipynb`
  - Create a tiny forcing relation; show `Ext/Int/Hit/Sel/J`, `covers`, `positive`, witnesses.
  - Acceptance: runs <10s, produces readable outputs.

- [ ] `02_medical_diagnosis_and_explanations.ipynb`
  - Port `examples/medical.py` and add “why not” cases, `explain()` output, and “formal closed” demo.

- [ ] `03_costs_and_budgets.ipynb`
  - Demonstrate `CostForcing` + `CostPosTop.at_budget`
  - Show “critical budget” curves for a few queries and `cheapest_discriminator()`.

- [ ] `04_llm_guardrail_pattern.ipynb`
  - Port `examples/llm_guardrail.py`; keep LLM as a stub.
  - Add a section showing how to map parsed claims to observables.

Acceptance: all notebooks run headless with `jupyter nbconvert --execute` (CI optional).

## P3 — API coherence + missing modules referenced by README

- [ ] **Fix README tree vs actual code**
  - Either remove `operators.py`/`llm.py` from the tree, OR implement them.
  - Recommendation: implement lightweight modules:
    - `operators.py`: re-export `Ext/Int/Hit/Sel/J` wrappers or helpers for tracing.
    - `llm.py`: *minimal* “claim → observable” interface + a guardrail class (no OpenAI dependency).
  - Acceptance: README tree is accurate; `import postop.llm` works if claimed.

- [ ] **Introduce a small “trace/explain” layer**
  - Add optional methods that return *why* `covers` holds (witness points showing inclusion) and why it fails (counterexample point).
  - Add optional method: `covers_counterexample(a, U) -> x` where `x ⊩ a` but `x ⊭ any u∈U`.
  - Acceptance: new explainability helpers used in notebooks.

## P4 — Logo + README + small docs polish

- [ ] **Add a simple logo**
  - Create `assets/logo.svg` and `assets/logo.png` (SVG is mandatory; PNG optional).
  - Use a “matrix / adjunction arrows” motif (Ext/Int and Hit/Sel).
  - Acceptance: README displays the logo on GitHub.

- [ ] **Rewrite README “Quick Start” to be copy/paste runnable**
  - Use `pip install -e .[dev]` and `python -m postop.examples...` (if adding module entrypoints) or show minimal snippet.
  - Remove/replace “OUP, 2025” with verified publication info.
  - Acceptance: README commands work.

## P5 — CI / release polish

- [ ] GitHub Actions: `tests`, `lint` (ruff/black), optional `notebooks` execution.
- [ ] Add `pre-commit` config.
- [ ] Add `tox` or `nox` for py39–py312.
- [ ] Tag `v0.1.1` once passing.

---

## Notes for Codex

- Keep everything deterministic and fast. No network calls in notebooks/tests.
- Prefer `pytest` over `unittest`.
- Avoid adding heavy dependencies unless they buy clarity (numpy optional; pandas optional).
- The “math correctness” criterion is: `covers`, `positive`, `J` satisfy contractive + idempotent, and examples match the paper’s definitions.
