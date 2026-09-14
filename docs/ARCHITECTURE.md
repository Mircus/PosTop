# Architecture

PosTop is organized in three layers, matching the status distinctions in
the September 2026 survey (*"Positive Topology and Feasible Refinement"*,
Mannucci & Sambin). Each layer is a separate module; nothing in a lower
layer imports from a higher one.

```
Layer 3 — Experimental resource semantics
  postop.costs
  (CostAnnotatedIncidence, CostForcing/CostPosTop, ThresholdSemantics)
        │
Layer 2 — Derived Positive Topology operators / certificates
  postop.core (IncidenceSystem), postop.formal (FormalPositiveTopology),
  postop.certificates, postop.operators, postop.evaluate
        │
Layer 1 — Finite incidence kernel
  postop.core (ForcingRelation)
```

## Layer 1 — finite incidence kernel

`ForcingRelation` is the whole kernel: a finite, in-memory `X × S`
incidence matrix (point → set of observables, plus a maintained reverse
index). It has no notion of cover, positivity, cost, or certificates. It
does not know it will be used to derive a topology at all.

## Layer 2 — derived Positive Topology operators / certificates

Two classes consume a `ForcingRelation` (or generators directly) and
produce cover/positivity structure:

- **`IncidenceSystem`** (`postop.core`) — the *point-derived* case
  (survey §1–8). Implements both adjunctions (`ext ⊣ box`,
  `diamond ⊣ rest`), their composites (`saturation`, `reduction`), the
  induced `covers`/`positive` relations, singleton reconstruction
  (Theorem 8.1), and formal-open/formal-closed checks. Compatibility
  (Prop. 5.10) is a *proven theorem* here — `compatibility_certificate`
  should never report `holds=False` with `reason_code
  ="compatibility_axiom_violated"` for a correctly-implemented instance;
  if it does, that is a bug report, not an expected outcome.

- **`FormalPositiveTopology`** (`postop.formal`) — the *primitive/
  pointfree* case. No points, no forcing table: cover and positivity are
  supplied directly as callables/data, and compatibility is an *axiom*
  the caller is responsible for satisfying. `validate_compatibility` is
  how a caller checks a proposed (cover, positive) pair against a
  specific instance — unlike `IncidenceSystem`, a `False` verdict here is
  a normal, expected outcome (the instance's data doesn't satisfy the
  axiom), not evidence of a library bug.

`postop.certificates` defines the shared, JSON-serializable evidence
types (`CoverCertificate`, `PositivityCertificate`,
`CompatibilityCertificate`, `BudgetCertificate`,
`CounterexampleCertificate`, `DiscriminatorSuggestion`) both classes
return from their `explain_*` / `*_certificate` methods, instead of a
bare bool. `postop.evaluate.Evaluator` is a small facade combining a
cover check and a positivity check into one `EvaluationResult`.

`postop.operators.OperatorSuite` is a thin tracing/convenience wrapper
around `IncidenceSystem` for notebook/demo use — it adds nothing
semantically.

## Layer 3 — experimental resource semantics

`postop.costs` implements the survey's §9 "programmatic sketch":

- `CostAnnotatedIncidence` is the recommended entry point: ground truth
  (`forces`) and verification cost (`verification_cost`) are kept as
  separate fields, so "true but unverified" and "false" are distinct
  states — the survey's minimal safe baseline (§9.1).
- `CostForcing` / `CostPosTop` are the legacy scalar-cost API, kept for
  backward compatibility. They conflate "no cost recorded" with
  "infinite cost" (i.e. "never true"), which the survey explicitly
  argues against — prefer `CostAnnotatedIncidence` for new code.
- `ThresholdSemantics` is a bare `Protocol` skeleton for the survey's
  §9.3 outlook (a generic `V`-valued incidence relation with a
  budget-indexed threshold map to an ordinary or other `H`-valued
  verdict). It has no default implementation and makes no completeness
  claim; it exists so a future resource logic has a stable place to land
  without requiring every call site to be rewritten.

**Non-monotonicity is the load-bearing fact of this layer.** Budgeted
*forcing* (`forces_within`) is monotone in the budget by construction.
The *induced* cover and positivity computed at a budget are **not**
guaranteed monotone — a larger budget can introduce a new point that
breaks a previously-true universal cover claim, or reveal a new
observable on an existing witness that breaks its confinement to a
positivity envelope, or make an expensive-to-verify witness newly
affordable. `tests/test_costs.py` has one concrete counterexample for
each direction. Nothing in this layer, in its docstrings, or in the
README should ever be read as claiming otherwise.

TROPOS, resource-indexed positive sites, coherent threshold maps, and
RB-CwF / graded logical semantics are **not implemented anywhere in this
repository** — they are the subject of the paper's planned follow-up
article and are only referenced here as motivation for
`ThresholdSemantics`'s shape.

## What PosTop deliberately does not own

- **Decisions.** Nothing in PosTop adopts state, arbitrates a proposal,
  or enforces a budget — it computes and returns certificates (evidence).
  A caller (a human, a script, or eventually an orchestration layer like
  HYRI's Kernel) decides what to do with that evidence.
- **Mutation.** No method here mutates the `ForcingRelation`/
  `IncidenceSystem`/`CostAnnotatedIncidence` it's called on; every
  `explain_*`/`*_certificate` call is a pure read.
- **A specific domain.** PosTop has no HYRI-specific code, and none is
  planned — see the "HYRI integration" note in the repository's refresh
  report (`REPO_REFRESH_REPORT.md`) for the recommended integration
  shape (certificates only, no internal coupling).
