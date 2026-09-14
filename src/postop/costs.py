"""
PosTop Costs: Resource-bounded forcing relations.

STATUS: the Boolean-forcing core (postop.core) is established (survey
§1-8). Everything in this module implements survey §9, which the paper
itself labels "a programmatic sketch" -- NOT a finished resource logic.
In particular:

- Truth is NOT identified with affordability. CostAnnotatedIncidence
  keeps ground-truth forcing (forces) and verification cost
  (verification_cost) as separate fields; forces_within is their
  conjunction, exactly the survey's minimal baseline (§9.1).
- Cover and positivity computed at a budget (`covers_at`/`positive_at`)
  are NOT guaranteed monotone in the budget, even though the underlying
  budgeted forcing relation is. See tests/test_costs.py for concrete
  counterexamples in both directions. Do not read a higher budget as
  "at least as much is true" for cover/positivity -- only for forcing
  itself.
- The generic ThresholdSemantics interface further down is an outlook
  sketch (survey §9.3), not a claimed-complete semantics.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
)

from .certificates import BudgetCertificate, DiscriminatorSuggestion
from .core import ForcingRelation, IncidenceSystem

X = TypeVar("X")
S = TypeVar("S")
B = TypeVar("B")  # budget type
V = TypeVar("V")  # enriched value type
H = TypeVar("H")  # threshold/output type


# =====================================================================
# Established baseline (survey §9.1): forces_within = forces AND cost<=budget
# =====================================================================


@dataclass
class CostAnnotatedIncidence(Generic[X, S, B]):
    """
    A forcing relation with a SEPARATE verification-cost annotation.

    This is the survey's minimal safe baseline: `forces(x, a)` is ground
    truth and does not depend on any budget; `verification_cost(x, a)`
    records what it costs to verify a true incidence (None = cost
    unknown/not applicable, distinct from "false"). `forces_within`
    combines the two:

        forces_within(x, a, budget) = forces(x, a) and cost(x, a) <= budget

    Unlike the legacy CostForcing (below), a missing cost here does NOT
    silently mean "false" -- it means "true but its verification cost was
    never recorded", which is a different, explicit state.
    """

    _ground_truth: ForcingRelation[X, S] = field(default_factory=ForcingRelation)
    _costs: Dict[Tuple[X, S], B] = field(default_factory=dict)
    leq: Callable[[B, B], bool] = field(default=lambda a, b: a <= b)

    def assert_true(self, x: X, a: S, cost: Optional[B] = None) -> None:
        """Record that x truly forces a, optionally with a verification cost."""
        self._ground_truth.add(x, [a])
        if cost is not None:
            self._costs[(x, a)] = cost

    def forces(self, x: X, a: S) -> bool:
        """Ground truth: does x really force a? Independent of any budget."""
        return self._ground_truth.forces(x, a)

    def verification_cost(self, x: X, a: S) -> Optional[B]:
        """Cost to verify (x, a), or None if unknown/not recorded."""
        return self._costs.get((x, a))

    def forces_within(self, x: X, a: S, budget: B) -> bool:
        """forces(x, a) AND a recorded cost that is <= budget."""
        if not self.forces(x, a):
            return False
        cost = self.verification_cost(x, a)
        if cost is None:
            return False
        return bool(self.leq(cost, budget))

    def to_incidence_system_within(self, budget: B) -> IncidenceSystem[X, S]:
        """Slice at a budget to get an ordinary (Boolean) IncidenceSystem."""
        fr: ForcingRelation[X, S] = ForcingRelation()
        for x in self._ground_truth.points:
            observables = [
                a
                for a in self._ground_truth.neighborhood(x)
                if self.forces_within(x, a, budget)
            ]
            if observables:
                fr.add(x, observables)
        return IncidenceSystem(fr)

    def budget_certificate(
        self, a: S, U: Set[S], budget: B, kind: str = "positive"
    ) -> BudgetCertificate[X, S]:
        """
        Evaluate cover or positivity of `a` in `U` at `budget`, returning
        full provenance: which (x, a) pairs were affordable, which
        weren't, and the resulting witness/counterexample.

        `kind` is "cover" or "positive".
        """
        system = self.to_incidence_system_within(budget)
        affordable = [
            (x, obs)
            for x in self._ground_truth.points
            for obs in self._ground_truth.neighborhood(x)
            if self.forces_within(x, obs, budget)
        ]
        unaffordable = [
            (x, obs)
            for x in self._ground_truth.points
            for obs in self._ground_truth.neighborhood(x)
            if self.forces(x, obs) and not self.forces_within(x, obs, budget)
        ]

        if kind == "cover":
            verdict = system.covers(a, U)
            counterexample = system.covers_counterexample(a, U)
            witness = None
        else:
            witness = system.find_witness(a, U)
            verdict = witness is not None
            counterexample = None

        return BudgetCertificate(
            budget=budget,
            verdict=verdict,
            affordable_observations=affordable,
            unaffordable_observations=unaffordable,
            witness=witness,
            counterexample=counterexample,
            assumptions=[
                "cover/positivity are NOT guaranteed monotone in budget "
                "(survey §9.2) -- re-evaluate at each budget of interest."
            ],
            reason_code=f"{kind}_at_budget",
        )


# =====================================================================
# Legacy scalar-cost API (kept for backward compatibility)
# =====================================================================


@dataclass
class CostDomain(ABC):
    """
    Abstract cost domain (V, ≤, ⊗, I, ⊸).

    - ≤: ordering (smaller = cheaper/stronger)
    - ⊗: monoidal product (combining costs)
    - I: unit (zero cost)
    - ⊸: residuation (cost difference)
    """

    @abstractmethod
    def leq(self, a: float, b: float) -> bool:
        """Check a ≤ b."""
        pass

    @abstractmethod
    def tensor(self, a: float, b: float) -> float:
        """Compute a ⊗ b."""
        pass

    @abstractmethod
    def unit(self) -> float:
        """Return the unit I."""
        pass

    @abstractmethod
    def residual(self, a: float, b: float) -> float:
        """Compute a ⊸ b."""
        pass

    @abstractmethod
    def join(self, values: List[float]) -> float:
        """Compute ⋁ values."""
        pass

    @abstractmethod
    def meet(self, values: List[float]) -> float:
        """Compute ⋀ values."""
        pass

    @abstractmethod
    def bottom(self) -> float:
        """Return the bottom element."""
        pass

    @abstractmethod
    def top(self) -> float:
        """Return the top element."""
        pass


@dataclass
class BooleanDomain(CostDomain):
    """Boolean cost domain: {0, 1} with ∧ as ⊗."""

    def leq(self, a: float, b: float) -> bool:
        return a <= b

    def tensor(self, a: float, b: float) -> float:
        return min(a, b)  # ∧

    def unit(self) -> float:
        return 1.0

    def residual(self, a: float, b: float) -> float:
        return 1.0 if a <= b else 0.0  # a → b

    def join(self, values: List[float]) -> float:
        return max(values) if values else 0.0

    def meet(self, values: List[float]) -> float:
        return min(values) if values else 1.0

    def bottom(self) -> float:
        return 0.0

    def top(self) -> float:
        return 1.0


@dataclass
class LawvereDomain(CostDomain):
    """
    Lawvere metric domain: [0, ∞] with + as ⊗.

    Note: smaller = better (closer), so we use standard ≤.
    This is the quantale for metric spaces / distances.
    """

    def leq(self, a: float, b: float) -> bool:
        return a <= b

    def tensor(self, a: float, b: float) -> float:
        return a + b

    def unit(self) -> float:
        return 0.0

    def residual(self, a: float, b: float) -> float:
        return max(0.0, b - a)  # truncated subtraction

    def join(self, values: List[float]) -> float:
        return max(values) if values else 0.0

    def meet(self, values: List[float]) -> float:
        return min(values) if values else math.inf

    def bottom(self) -> float:
        return 0.0

    def top(self) -> float:
        return math.inf


@dataclass
class CostForcing(Generic[X, S]):
    """
    A cost-valued forcing relation R: X × S → V.

    LEGACY / EXPERIMENTAL: a missing entry here means "infinite cost",
    which is used as a stand-in for "never true at any finite budget".
    That conflates "definitely false" with "true but unaffordable" --
    prefer CostAnnotatedIncidence (above) for new code, which keeps
    those two states distinct per the survey's minimal baseline (§9.1).
    """

    _costs: Dict[Tuple[X, S], float] = field(default_factory=dict)
    _points: Set[X] = field(default_factory=set)
    _observables: Set[S] = field(default_factory=set)
    domain: CostDomain = field(default_factory=LawvereDomain)
    default_cost: float = field(default=math.inf)

    def set_cost(self, x: X, a: S, cost: float) -> None:
        """Set R(x, a) = cost."""
        self._costs[(x, a)] = cost
        self._points.add(x)
        self._observables.add(a)

    def cost(self, x: X, a: S) -> float:
        """Get R(x, a)."""
        return self._costs.get((x, a), self.default_cost)

    def forces_at_budget(self, x: X, a: S, budget: float) -> bool:
        """Check x ⊩_b a, i.e., R(x, a) ≤ budget."""
        return self.domain.leq(self.cost(x, a), budget)

    def to_boolean_forcing(self, budget: float) -> ForcingRelation[X, S]:
        """
        Slice at budget b to get Boolean forcing.

        x ⊩_b a iff R(x, a) ≤ b
        """
        fr: ForcingRelation[X, S] = ForcingRelation()
        for x in self._points:
            observables = [
                a for a in self._observables if self.forces_at_budget(x, a, budget)
            ]
            if observables:
                fr.add(x, observables)
        return fr

    @property
    def points(self) -> Set[X]:
        return self._points.copy()

    @property
    def observables(self) -> Set[S]:
        return self._observables.copy()


class CostPosTop(Generic[X, S]):
    """
    Resource-bounded positive topology (legacy naming; new code should
    prefer CostAnnotatedIncidence.to_incidence_system_within).

    All operations are parameterized by a budget. Cover/positivity at a
    budget are computed exactly, but are NOT guaranteed monotone as the
    budget increases -- see module docstring and tests/test_costs.py.
    """

    def __init__(self, cost_forcing: CostForcing[X, S]):
        self.cf = cost_forcing

    def at_budget(self, budget: float) -> IncidenceSystem[X, S]:
        """Get the Boolean IncidenceSystem at a given budget."""
        fr = self.cf.to_boolean_forcing(budget)
        return IncidenceSystem(fr)

    def covers_at(self, a: S, U: Set[S], budget: float) -> bool:
        """Check a ◁_b U."""
        return self.at_budget(budget).covers(a, U)

    def positive_at(self, a: S, U: Set[S], budget: float) -> bool:
        """Check a ⋉_b U."""
        return self.at_budget(budget).positive(a, U)

    def critical_budget_cover(
        self, a: S, U: Set[S], budgets: List[float]
    ) -> Optional[float]:
        """
        Find the minimum budget (among those given) at which a ◁_b U
        holds. Because cover is not monotone in budget, this is a search
        over the supplied list, not a guaranteed threshold: a ◁_b U may
        hold at this budget and fail again at a larger one.
        """
        for b in sorted(budgets):
            if self.covers_at(a, U, b):
                return b
        return None

    def critical_budget_positive(
        self, a: S, U: Set[S], budgets: List[float]
    ) -> Optional[float]:
        """
        Find the minimum budget (among those given) at which a ⋉_b U
        holds. See critical_budget_cover's caveat about non-monotonicity.
        """
        for b in sorted(budgets):
            if self.positive_at(a, U, b):
                return b
        return None

    def cheapest_discriminator(
        self, hypotheses: List[S], observed: Set[S], budget: float
    ) -> Optional[Tuple[S, float]]:
        """
        Find the cheapest observation that discriminates between
        hypotheses at the given budget. A simple finite-search heuristic,
        not claimed optimal in any formal sense; see suggest_next_test
        for the certificate-producing wrapper.
        """
        system = self.at_budget(budget)

        candidates = []
        for a in self.cf.observables:
            if a in observed:
                continue  # Already observed

            # Check if a discriminates: some h covers a, some don't
            covers_a = [h for h in hypotheses if system.covers(h, {a} | observed)]
            if 0 < len(covers_a) < len(hypotheses):
                min_cost = min(self.cf.cost(x, a) for x in self.cf.points)
                if min_cost <= budget:
                    candidates.append((a, min_cost))

        if not candidates:
            return None

        return min(candidates, key=lambda item: item[1])

    def suggest_next_test(
        self, hypotheses: List[S], observed: Set[S], budget: float
    ) -> DiscriminatorSuggestion[S]:
        """
        Certificate-producing wrapper around cheapest_discriminator.

        This is a policy HOOK with a simple built-in heuristic, not a
        theorem -- it is never labeled "optimal" here.
        """
        result = self.cheapest_discriminator(hypotheses, observed, budget)
        if result is None:
            return DiscriminatorSuggestion(
                observable=None,
                estimated_cost=None,
                surviving_hypotheses_before=list(hypotheses),
                discriminates=False,
                reason_code="no_discriminator_within_budget",
            )
        observable, cost = result
        return DiscriminatorSuggestion(
            observable=observable,
            estimated_cost=cost,
            surviving_hypotheses_before=list(hypotheses),
            discriminates=True,
            reason_code="cheapest_discriminator_found",
        )


# =====================================================================
# Experimental: generic enriched-value threshold interface (survey §9.3)
# =====================================================================


class ThresholdSemantics(Protocol, Generic[V, B, H]):
    """
    EXPERIMENTAL -- outlook only, per survey §9.3. Not a complete or
    finalized semantics; the choice of V, the recovery of the underlying
    Boolean truth relation, and the interaction with logical structural
    rules are explicitly left open in the paper and deferred to a
    follow-up article. Do not build production logic against this
    Protocol expecting stability.

    A generic replacement for the Boolean forcing matrix, carrying both
    logical and resource information: R: X × S -> V, together with a
    threshold map recovering an ordinary Boolean (or other H-valued)
    forcing at a given budget.
    """

    def value(self, x: Any, a: Any) -> V:
        """The enriched value R(x, a) ∈ V."""
        ...

    def threshold(self, budget: B, value: V) -> H:
        """Project an enriched value down to an H-valued verdict at a budget."""
        ...


# =====================================================================
# Convenience example data
# =====================================================================


def medical_costs() -> Tuple[CostForcing[str, str], Dict[str, float]]:
    """
    Example: Medical test costs (legacy CostForcing demo data).
    """
    cf = CostForcing(domain=LawvereDomain(), default_cost=math.inf)

    costs = {
        "fever": 0,
        "cough": 0,
        "fatigue": 0,
        "headache": 0,
        "runny_nose": 0,
        "blood_pressure": 5,
        "pulse": 5,
        "temperature": 0,
        "blood_test": 50,
        "elevated_WBC": 50,
        "xray": 200,
        "infiltrates": 200,
        "ct_scan": 500,
        "pcr_test": 100,
        "covid_positive": 100,
        "flu_positive": 80,
    }

    return cf, costs
