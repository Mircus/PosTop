"""
PosTop Core: Forcing relations and positive topology.

The fundamental structure is a forcing relation x ⊩ a between:
- X: points (states, patients, cases, traces)
- S: observables (symptoms, tests, constraints)

From this, we derive:
- Ext/Int: the universal (cover) adjunction
- Hit/Sel: the existential (positivity) adjunction
- J = Hit ∘ Sel: the positivity interior
- Covers: a ◁ U iff Ext({a}) ⊆ Ext(U)
- Positivity: a ⋉ U iff a ∈ J(U)
"""

from __future__ import annotations
from typing import Set, Dict, List, Optional, Any, TypeVar, Generic
from dataclasses import dataclass, field

X = TypeVar("X")  # Points
S = TypeVar("S")  # Observables


@dataclass
class ForcingRelation(Generic[X, S]):
    """
    A forcing relation between points X and observables S.

    Stores the relation as a dict: point -> set of observables.
    """

    _forward: Dict[X, Set[S]] = field(default_factory=dict)
    _backward: Dict[S, Set[X]] = field(default_factory=dict)

    def add(self, point: X, observables: List[S] | Set[S]) -> None:
        """
        Add a point with its observable profile.

        Subsequent calls merge the new observables into the existing profile
        instead of replacing it, ensuring forward/backward indices stay aligned.
        """
        obs_set = set(observables)
        existing = self._forward.get(point, set())
        merged = existing | obs_set
        self._forward[point] = merged

        for a in merged:
            if a not in self._backward:
                self._backward[a] = set()
        for a in obs_set:
            self._backward[a].add(point)

    def forces(self, x: X, a: S) -> bool:
        """Check if point x forces observable a."""
        return a in self._forward.get(x, set())

    def neighborhood(self, x: X) -> Set[S]:
        """Get the neighborhood N(x) = {a : x ⊩ a}."""
        return self._forward.get(x, set()).copy()

    def extension(self, a: S) -> Set[X]:
        """Get Ext({a}) = {x : x ⊩ a}."""
        return self._backward.get(a, set()).copy()

    @property
    def points(self) -> Set[X]:
        """All points in the relation."""
        return set(self._forward.keys())

    @property
    def observables(self) -> Set[S]:
        """All observables in the relation."""
        return set(self._backward.keys())

    def __len__(self) -> int:
        """Number of points in the relation."""
        return len(self._forward)

    def __contains__(self, point: X) -> bool:
        """Check whether a point is present."""
        return point in self._forward

    def __iter__(self):
        """Iterate over the points."""
        return iter(self._forward)

    def __repr__(self) -> str:
        return f"ForcingRelation({len(self._forward)} points, {len(self._backward)} observables)"


class PosTop(Generic[X, S]):
    """
    A positive topology derived from a forcing relation.

    Provides:
    - Ext, Int: the universal (cover) adjunction
    - Hit, Sel: the existential (positivity) adjunction
    - J: the positivity interior
    - covers: the cover relation
    - positive: the positivity relation
    """

    def __init__(self, forcing: ForcingRelation[X, S]):
        self.forcing = forcing

    # =========== The First Adjunction: Ext ⊣ Int ===========

    def Ext(self, U: Set[S]) -> Set[X]:
        """
        Extension: Ext(U) = {x : ∃a ∈ U. x ⊩ a}

        Points that satisfy at least one observable in U.
        """
        result = set()
        backward = self.forcing._backward
        for a in U:
            points = backward.get(a)
            if points:
                result.update(points)
        return result

    def Int(self, A: Set[X]) -> Set[S]:
        """
        Interior-kernel: Int(A) = {a : ∀x. x ⊩ a ⟹ x ∈ A}

        Observables that only hold for points in A.
        """
        result = set()
        for a in self.forcing.observables:
            ext_a = self.forcing.extension(a)
            if ext_a <= A:  # subset
                result.add(a)
        return result

    # =========== The Second Adjunction: Hit ⊣ Sel ===========

    def Hit(self, C: Set[X]) -> Set[S]:
        """
        Hit: Hit(C) = {a : ∃x ∈ C. x ⊩ a}

        Observables witnessed by at least one point in C.
        """
        result = set()
        for x in C:
            result |= self.forcing.neighborhood(x)
        return result

    def Sel(self, U: Set[S]) -> Set[X]:
        """
        Selection: Sel(U) = {x : N(x) ⊆ U}

        Points whose entire neighborhood is contained in U.
        """
        result = set()
        for x in self.forcing.points:
            N_x = self.forcing.neighborhood(x)
            if N_x <= U:  # subset
                result.add(x)
        return result

    # =========== Composite Operators ===========

    def J(self, U: Set[S]) -> Set[S]:
        """
        Positivity interior: J(U) = Hit(Sel(U))

        Observables that have a witness confined to U.
        """
        return self.Hit(self.Sel(U))

    def closure_on_points(self, C: Set[X]) -> Set[X]:
        """
        Closure on points: cl(C) = Sel(Hit(C))

        Points whose every observable is witnessed in C.
        """
        return self.Sel(self.Hit(C))

    def j(self, U: Set[S]) -> Set[S]:
        """
        Nucleus on observables: j(U) = Int(Ext(U))

        Saturated formal opens.
        """
        return self.Int(self.Ext(U))

    # =========== Cover and Positivity Relations ===========

    def covers(self, a: S, U: Set[S]) -> bool:
        """
        Cover relation: a ◁ U iff Ext({a}) ⊆ Ext(U)

        Every point satisfying a satisfies something in U.
        """
        ext_a = self.forcing.extension(a)
        ext_U = self.Ext(U)
        return ext_a <= ext_U

    def positive(self, a: S, U: Set[S]) -> bool:
        """
        Positivity relation: a ⋉ U iff a ∈ J(U)

        There exists a witness for a confined to U.
        """
        return a in self.J(U)

    def covers_witnesses(self, a: S, U: Set[S]) -> Dict[X, Set[S]]:
        """
        For each point witnessing a, record which observables in U it hits.
        """
        witness_map: Dict[X, Set[S]] = {}
        for x in self.forcing.extension(a):
            hits = self.forcing.neighborhood(x) & U
            if hits:
                witness_map[x] = hits
        return witness_map

    def covers_counterexample(self, a: S, U: Set[S]) -> Optional[X]:
        """
        Return x witnessing the failure of a ◁ U, if one exists.
        """
        ext_U = self.Ext(U)
        for x in self.forcing.extension(a):
            if x not in ext_U:
                return x
        return None

    def explain_cover(self, a: S, U: Set[S]) -> Dict[str, Any]:
        """
        Explain why a ◁ U holds or fails.
        """
        counterexample = self.covers_counterexample(a, U)
        witnesses = self.covers_witnesses(a, U)
        holds = counterexample is None and self.covers(a, U)
        return {
            "holds": holds,
            "witnesses": witnesses,
            "counterexample": counterexample,
        }

    def find_witness(self, a: S, U: Set[S]) -> Optional[X]:
        """
        Find a witness for a ⋉ U, if one exists.

        Returns a point x with x ⊩ a and N(x) ⊆ U.
        """
        for x in self.forcing.extension(a):
            if self.forcing.neighborhood(x) <= U:
                return x
        return None

    # =========== Formal Opens and Closeds ===========

    def is_formal_open(self, U: Set[S]) -> bool:
        """Check if U is a formal open: j(U) = U."""
        return self.j(U) == U

    def is_formal_closed(self, U: Set[S]) -> bool:
        """Check if U is a formal closed: J(U) = U."""
        return self.J(U) == U

    # =========== Compatibility ===========

    def check_compatibility(self, a: S, U: Set[S], V: Set[S]) -> Optional[S]:
        """
        Check the compatibility axiom:
        If a ◁ U and a ⋉ V, find u ∈ U with u ⋉ V.

        Returns the witnessing u, or None if preconditions fail.
        """
        if not self.covers(a, U):
            return None
        if not self.positive(a, V):
            return None

        # Find u ∈ U with u ⋉ V
        for u in U:
            if self.positive(u, V):
                return u

        # This should not happen if the theory is correct
        raise AssertionError("Compatibility axiom violated!")

    # =========== Diagnosis / Inference ===========

    def consistent_hypotheses(self, observed: Set[S]) -> List[S]:
        """
        Find hypotheses consistent with observations.

        Returns observables a such that:
        - a ◁ observed (a implies something observed)
        - a ⋉ observed (a has a witness in observed profile)
        """
        result = []
        for a in self.forcing.observables:
            if self.covers(a, observed) and self.positive(a, observed):
                result.append(a)
        return result

    def explain(self, a: S, observed: Set[S]) -> Dict[str, Any]:
        """
        Explain why a is (or isn't) consistent with observations.
        """
        covers_ok = self.covers(a, observed)
        witness = self.find_witness(a, observed)
        cover_details = self.explain_cover(a, observed)

        return {
            "observable": a,
            "observed": observed,
            "covers": covers_ok,
            "has_witness": witness is not None,
            "witness": witness,
            "consistent": covers_ok and (witness is not None),
            "cover_details": cover_details,
        }


# =========== Convenience Functions ===========


def from_dict(data: Dict[Any, List[Any]]) -> ForcingRelation:
    """Create a forcing relation from a dict of point -> observables."""
    fr = ForcingRelation()
    for point, observables in data.items():
        fr.add(point, observables)
    return fr
