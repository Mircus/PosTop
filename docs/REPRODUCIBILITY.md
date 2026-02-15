# Reproducibility Guide

Use this guide to install PosTop, run the shipped examples, execute notebooks (once published), and validate the test suite. Every block below is copy/paste ready for a clean machine.

## 1. Create an Environment and Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

The editable install exposes `postop` as a package while making the source tree editable. Re-run `pip install -e .[dev]` whenever dependencies change.

## 2. Run the Examples

Medical diagnosis walkthrough:

```bash
python examples/medical.py
```

LLM guardrail walkthrough:

```bash
python examples/llm_guardrail.py
```

Both scripts print their results to stdout. No additional arguments are required.

## 3. Execute the Notebooks

The canonical notebooks now live in `notebooks/`:

- `01_basics_ext_int_hit_sel_j.ipynb` — minimal forcing relation, Ext/Int/Hit/Sel/J traces, cover explanations
- `02_medical_diagnosis_and_explanations.ipynb` — reproduces the medical scenario with detailed witnesses/counterexamples
- `03_costs_and_budgets.ipynb` — slices a cost-valued forcing relation at increasing budgets
- `04_llm_guardrail_pattern.ipynb` — claim normalization + guardrail workflow mirroring the example module

Execute any notebook headlessly via:

```bash
jupyter nbconvert --to notebook --execute notebooks/01_basics_ext_int_hit_sel_j.ipynb
```

Swap the filename accordingly; the command fails if any cell errors, making it CI-friendly.

## 4. Run the Tests

```bash
pytest -q
```

The tests import `postop` as an installed package, so run them from the repository root inside the same virtual environment created above.

## 5. Optional: Developer Tooling

- `pre-commit install` then `pre-commit run --all-files` to mirror the lint workflow (ruff + black + mypy).
- `tox -q` to exercise the Python 3.9–3.12 test matrix locally (matches CI).
