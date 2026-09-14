# Reproducibility Guide

Use this guide to install PosTop, run the shipped examples, execute
notebooks, and validate the test suite. Every block below is copy/paste
ready for a clean machine, and matches `README.md`.

Canonical repository: <https://github.com/Mircus/PosTop>

## 1. Create an Environment and Install

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -e .[dev]
```

The editable install exposes `postop` as a package while making the
source tree editable. Re-run `pip install -e .[dev]` whenever
dependencies change.

## 2. Run the Examples

Medical diagnosis walkthrough:

```bash
python examples/medical.py
```

LLM guardrail adapter walkthrough:

```bash
python examples/llm_guardrail.py
```

Both scripts print their results to stdout, including Unicode symbols
(`◁`, `⋉`, `𝒥`). On Windows, if you see a `UnicodeEncodeError` in a
plain `cmd.exe`/legacy console, set `PYTHONIOENCODING=utf-8` first (or
run from PowerShell/Windows Terminal, which default to UTF-8):

```powershell
$env:PYTHONIOENCODING = "utf-8"
python examples\medical.py
```

No additional arguments are required for either script.

## 3. Execute the Notebooks

The canonical notebooks live in `notebooks/`:

- `01_forcing_and_adjunctions.ipynb` — minimal forcing relation,
  ext/box/diamond/rest/reduction traces, cover explanations
- `02_medical_cover_positivity.ipynb` — reproduces the medical scenario
  with detailed witnesses/counterexamples
- `03_budgeted_forcing.ipynb` — slices a cost-annotated forcing relation
  at increasing budgets, including a non-monotonicity example
- `04_ai_certificates.ipynb` — the guardrail adapter pattern, emphasizing
  the explicit hypothesis/observation encoding and certificate output

Execute any notebook headlessly via:

```bash
jupyter nbconvert --to notebook --execute notebooks/01_forcing_and_adjunctions.ipynb
```

Swap the filename accordingly; the command fails if any cell errors,
making it CI-friendly (notebooks are not currently run in CI itself --
see `.github/workflows/tests.yml`).

## 4. Run the Tests

```bash
pytest -q
```

The tests import `postop` as an installed package, so run them from the
repository root inside the same virtual environment created above. No
network access or external services are required anywhere in the suite.

## 5. Optional: Developer Tooling

- `pre-commit install` then `pre-commit run --all-files` to mirror the
  lint workflow (ruff + black + mypy).
- `tox -q` to exercise the Python 3.9–3.12 test matrix locally (matches
  CI).
