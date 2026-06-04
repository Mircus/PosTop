# PosTop: Positive Topology for Grounded AI

<p align="center">
  <img src="assets/logo.svg" alt="PosTop logo" width="700">
</p>

<p align="center">
  <a href="https://github.com/mirco-mannucci/postop/actions/workflows/tests.yml">
    <img alt="Tests" src="https://github.com/mirco-mannucci/postop/actions/workflows/tests.yml/badge.svg">
  </a>
  <a href="https://github.com/mirco-mannucci/postop/actions/workflows/lint.yml">
    <img alt="Lint" src="https://github.com/mirco-mannucci/postop/actions/workflows/lint.yml/badge.svg">
  </a>
</p>

**Covers tell you what implies what. Positivity tells you what exists. Together: grounded inference.**

PosTop is a framework for building AI systems that are:
- **Grounded**: Every claim has a witness
- **Consistent**: No contradictions
- **Explainable**: Reasoning via cover chains
- **Resource-aware**: Cheapest verification first

## The Core Idea

From a forcing relation `x ⊩ a` ("state x satisfies observable a"), we derive:

| Structure | Meaning | Use |
|-----------|---------|-----|
| `a ◁ U` (cover) | a implies something in U | Semantic entailment |
| `a ⋉ U` (positivity) | ∃ witness for a confined to U | Consistency check |
| `r` (resource) | Cost to verify | Budget optimization |

The **compatibility axiom** ensures soundness:
```
(a ◁ U) ∧ (a ⋉ V) ⟹ ∃u ∈ U. u ⋉ V
```
Refinement preserves witnesses.

## Installation

Use an isolated environment so editable installs and dev dependencies stay contained:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Quick Start

After installing, you can either run the canned demos or script inline experiments. See `docs/REPRODUCIBILITY.md` for a full setup/run checklist.

Run the medical example directly:

```bash
python examples/medical.py
```

Or open a Python REPL/nb and use the API:

```python
from postop import ForcingRelation, PosTop

forcing = ForcingRelation()
forcing.add("patient_1", ["fever", "cough", "fatigue"])
forcing.add("patient_2", ["fever", "headache", "fatigue"])
forcing.add("patient_3", ["cough", "runny_nose"])

pt = PosTop(forcing)
print(pt.covers("fever", {"fever", "cough"}))
print(pt.positive("fever", {"fever", "cough", "fatigue"}))
```

### Developer Tooling

- Run formatters/linters locally via `pre-commit install` then `pre-commit run --all-files`.
- Use `tox` to exercise the pytest matrix (`py39`–`py312`) locally before pushing.

## Architecture

```
┌─────────────────────────────────────────┐
│            User Query                   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│     LLM (Pattern Matching)              │
│     Generates candidate hypotheses      │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│     PosTop Backbone                     │
│                                         │
│  • Cover check (valid inference?)       │
│  • Positivity check (has witness?)      │
│  • Resource optimization                │
│  • Explanation generation               │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│     Verified Output                     │
│     + Explanation + Confidence          │
└─────────────────────────────────────────┘
```

## Examples

- [Medical Diagnosis](examples/medical.py) - Symptom-based diagnosis with test costs
- [LLM Guardrail](examples/llm_guardrail.py) - Grounding LLM outputs
- [Notebooks](notebooks/) - `01_basics_ext_int_hit_sel_j.ipynb` (operator tour), `02_medical_diagnosis_and_explanations.ipynb` (witness reasoning), `03_costs_and_budgets.ipynb` (budget slices), `04_llm_guardrail_pattern.ipynb` (claim normalization); run with `jupyter nbconvert --execute ...`

## Theory

The mathematical foundations are in [docs/survey.pdf](docs/positive_topology_survey_v2.pdf).

Key references:
- Sambin, G. *Positive Topology* (OUP, forthcoming)
- Ciraulo & Sambin, "A constructive Galois connection" (JSL, 2012)

## Project Structure

```
postop/
├── src/
│   └── postop/
│       ├── __init__.py
│       ├── core.py          # ForcingRelation, PosTop
│       ├── operators.py     # Ext/Int/Hit/Sel/J helpers + tracing
│       ├── costs.py         # Cost domains, budgets
│       └── llm.py           # Guardrail + claim normalization helpers
├── examples/
│   ├── medical.py
│   └── llm_guardrail.py
├── tests/
│   └── test_core.py
├── docs/
│   ├── positive_topology_survey_v2.pdf
│   └── REPRODUCIBILITY.md
│   └── actionlist.md
├── assets/
│   ├── logo.svg
│   └── logo.png
├── CITATION.cff
└── README.md
```

## Why Not Just Knowledge Graphs?

| Feature | Knowledge Graph | PosTop |
|---------|-----------------|--------|
| Entities | ✓ | ✓ |
| Relations | ✓ | ✓ |
| Facts | ✓ | ✓ |
| **Entailment** | ✗ | ✓ |
| **Witnesses** | ✗ | ✓ |
| **Costs** | ✗ | ✓ |
| **Refinement soundness** | ✗ | ✓ |

> **Knowledge Graphs** tell you what exists.  
> **PosTop** tells you what's consistent, what implies what, and how to verify efficiently.

## License

MIT

## Citation

See `CITATION.cff` for machine-readable metadata. A minimal BibTeX entry is:

```bibtex
@misc{postop2025,
  title={PosTop: Positive Topology for Grounded AI},
  author={Mannucci, Mirco A. and Sambin, Giovanni},
  year={2025}
}
```
