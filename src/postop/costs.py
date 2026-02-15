"""
PosTop Costs: Resource-bounded forcing relations.

A cost-valued forcing relation assigns a cost R(x, a) to each pair,
representing the verification cost for point x to satisfy observable a.

At budget b, we have: x ⊩_b a iff R(x, a) ≤ b
"""

from __future__ import annotations
from typing import Set, Dict, List, Optional, TypeVar, Generic, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import math

from .core import ForcingRelation, PosTop

X = TypeVar('X')
S = TypeVar('S')


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
    
    R(x, a) = cost to verify that x satisfies a.
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
        fr = ForcingRelation()
        for x in self._points:
            observables = [a for a in self._observables 
                          if self.forces_at_budget(x, a, budget)]
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
    Resource-bounded positive topology.
    
    All operations are parameterized by a budget.
    """
    
    def __init__(self, cost_forcing: CostForcing[X, S]):
        self.cf = cost_forcing
    
    def at_budget(self, budget: float) -> PosTop[X, S]:
        """Get the Boolean PosTop at a given budget."""
        fr = self.cf.to_boolean_forcing(budget)
        return PosTop(fr)
    
    def covers_at(self, a: S, U: Set[S], budget: float) -> bool:
        """Check a ◁_b U."""
        return self.at_budget(budget).covers(a, U)
    
    def positive_at(self, a: S, U: Set[S], budget: float) -> bool:
        """Check a ⋉_b U."""
        return self.at_budget(budget).positive(a, U)
    
    def critical_budget_cover(self, a: S, U: Set[S], 
                               budgets: List[float]) -> Optional[float]:
        """
        Find the minimum budget at which a ◁_b U holds.
        
        Searches through the given budget list.
        """
        for b in sorted(budgets):
            if self.covers_at(a, U, b):
                return b
        return None
    
    def critical_budget_positive(self, a: S, U: Set[S],
                                  budgets: List[float]) -> Optional[float]:
        """
        Find the minimum budget at which a ⋉_b U holds.
        """
        for b in sorted(budgets):
            if self.positive_at(a, U, b):
                return b
        return None
    
    def cheapest_discriminator(self, hypotheses: List[S], 
                                observed: Set[S],
                                budget: float) -> Optional[Tuple[S, float]]:
        """
        Find the cheapest observation that discriminates between hypotheses.
        
        Returns (observable, cost) or None if no discriminator exists.
        """
        pt = self.at_budget(budget)
        
        # Get all observables that could help
        candidates = []
        for a in self.cf.observables:
            if a in observed:
                continue  # Already observed
            
            # Check if a discriminates: some h covers a, some don't
            covers_a = [h for h in hypotheses if pt.covers(h, {a} | observed)]
            if 0 < len(covers_a) < len(hypotheses):
                # Find minimum cost to verify a across all points
                min_cost = min(self.cf.cost(x, a) for x in self.cf.points)
                if min_cost <= budget:
                    candidates.append((a, min_cost))
        
        if not candidates:
            return None
        
        # Return cheapest
        return min(candidates, key=lambda x: x[1])


# =========== Convenience ===========

def medical_costs() -> Tuple[CostForcing[str, str], Dict[str, float]]:
    """
    Example: Medical test costs.
    
    Returns a cost forcing with typical medical test costs.
    """
    cf = CostForcing(domain=LawvereDomain(), default_cost=math.inf)
    
    # Costs for verifying symptoms/tests
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
