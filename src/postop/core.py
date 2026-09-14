"""
PosTop Core: Forcing relations and the point-derived Positive Topology.

The fundamental structure is a forcing relation x ⊩ a between:
- X: points (states, patients, cases, traces)
- S: observables (symptoms, tests, constraints)

From this, IncidenceSystem derives (canonical names from the paper
"Positive Topology and Feasible Refinement", Mannucci & Sambin 2026):

- ext ⊣ box:      the universal (cover) adjunction
- diamond ⊣ rest: the existential (positivity) adjunction
- saturation = box ∘ ext:      formal opens
- reduction  = diamond ∘ rest: the positivity interior 𝒥
- covers:   a ◁ U  iff  ext({a}) ⊆ ext(U)
- positive: a ⋉ U  iff  a ∈ reduction(U)

This is the *point-derived* case (survey §1-8): cover and positivity are
derived from a concrete forcing table, and the compatibility axiom is a
theorem, not an assumption. See postop.formal.FormalPositiveTopology for
the primitive/pointfree case, where positivity is taken as data.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, Set, TypeVar

from .certificates import (
    CompatibilityCertificate,
    CoverCertificate,
    PositivityCertificate,
)

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
        """Get ext({a}) = {x : x ⊩ a}."""
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


def _deprecated(old_name: str, new_name: str) -> None:
    warnings.warn(
        f"'{old_name}' is a deprecated alias; use '{new_name}' instead "
        f"(canonical names per the paper's operator table -- see docs/ARCHITECTURE.md).",
        DeprecationWarning,
        stacklevel=3,
    )


class IncidenceSystem(Generic[X, S]):
    """
    A point-derived Positive Topology built on top of a ForcingRelation.

    Provides the two canonical adjunctions (ext/box and diamond/rest),
    their composites (saturation/reduction), the induced cover and
    positivity relations, and certificate-producing explanations.
    """

    def __init__(self, forcing: ForcingRelation[X, S]):
        self.forcing = forcing

    # =========== The First Adjunction: ext ⊣ box ===========

    def ext(self, U: Set[S]) -> Set[X]:
        """
        Extension: ext(U) = {x : ∃a ∈ U. x ⊩ a}

        Points that satisfy at least one observable in U.
        """
        result: Set[X] = set()
        backward = self.forcing._backward
        for a in U:
            points = backward.get(a)
            if points:
                result.update(points)
        return result

    def box(self, E: Set[X]) -> Set[S]:
        """
        The universal residual: box(E) = {a : ∀x. x ⊩ a ⟹ x ∈ E}

        Observables that only hold for points in E.
        """
        result: Set[S] = set()
        for a in self.forcing.observables:
            ext_a = self.forcing.extension(a)
            if ext_a <= E:  # subset
                result.add(a)
        return result

    # =========== The Second Adjunction: diamond ⊣ rest ===========

    def diamond(self, D: Set[X]) -> Set[S]:
        """
        diamond(D) = {a : ∃x ∈ D. x ⊩ a}

        Observables witnessed by at least one point in D.
        """
        result: Set[S] = set()
        for x in D:
            result |= self.forcing.neighborhood(x)
        return result

    def rest(self, U: Set[S]) -> Set[X]:
        """
        rest(U) = {x : N(x) ⊆ U}

        Points whose entire neighborhood is contained in U.
        """
        result: Set[X] = set()
        for x in self.forcing.points:
            N_x = self.forcing.neighborhood(x)
            if N_x <= U:  # subset
                result.add(x)
        return result

    # =========== Composite Operators ===========

    def reduction(self, U: Set[S]) -> Set[S]:
        """
        Positivity interior: reduction(U) = diamond(rest(U))  (paper 𝒥)

        Observables that have a witness confined to U.
        """
        return self.diamond(self.rest(U))

    def closure_on_points(self, C: Set[X]) -> Set[X]:
        """
        Closure on points: cl(C) = rest(diamond(C))

        Points whose every observable is witnessed in C.
        """
        return self.rest(self.diamond(C))

    def saturation(self, U: Set[S]) -> Set[S]:
        """
        Nucleus on observables: saturation(U) = box(ext(U))  (paper 𝒜)

        Saturated formal opens.
        """
        return self.box(self.ext(U))

    # =========== Cover and Positivity Relations ===========

    def covers(self, a: S, U: Set[S]) -> bool:
        """
        Cover relation: a ◁ U iff ext({a}) ⊆ ext(U)

        Every point satisfying a satisfies something in U.
        """
        ext_a = self.forcing.extension(a)
        ext_U = self.ext(U)
        return ext_a <= ext_U

    def positive(self, a: S, U: Set[S]) -> bool:
        """
        Positivity relation: a ⋉ U iff a ∈ reduction(U)

        There exists a witness for a confined to U.
        """
        return a in self.reduction(U)

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
        ext_U = self.ext(U)
        for x in self.forcing.extension(a):
            if x not in ext_U:
                return x
        return None

    def explain_cover(self, a: S, U: Set[S]) -> CoverCertificate[X, S]:
        """
        Explain why a ◁ U holds or fails, as a structured certificate.
        """
        counterexample = self.covers_counterexample(a, U)
        witnesses = self.covers_witnesses(a, U)
        holds = counterexample is None and self.covers(a, U)
        return CoverCertificate(
            subject=a,
            claim=f"{a!r} ◁ U",
            region=U,
            holds=holds,
            witnesses=witnesses,
            counterexample=counterexample,
            reason_code="cover_holds" if holds else "cover_counterexample",
        )

    def find_witness(self, a: S, U: Set[S]) -> Optional[X]:
        """
        Find a witness for a ⋉ U, if one exists.

        Returns a point x with x ⊩ a and N(x) ⊆ U.
        """
        for x in self.forcing.extension(a):
            if self.forcing.neighborhood(x) <= U:
                return x
        return None

    def explain_positive(self, a: S, U: Set[S]) -> PositivityCertificate[X, S]:
        """
        Explain why a ⋉ U holds or fails, as a structured certificate.
        """
        witness = self.find_witness(a, U)
        holds = witness is not None
        return PositivityCertificate(
            subject=a,
            claim=f"{a!r} ⋉ U",
            region=U,
            holds=holds,
            witness=witness,
            witness_profile=self.forcing.neighborhood(witness) if witness is not None else None,
            reason_code="positivity_witnessed" if holds else "no_witness",
        )

    # =========== Formal Opens and Closeds ===========

    def is_formal_open(self, U: Set[S]) -> bool:
        """Check if U is a formal open: saturation(U) = U."""
        return self.saturation(U) == U

    def is_formal_closed(self, U: Set[S]) -> bool:
        """
        Check if U is a formal closed: reduction(U) = U.

        reduction(U) ⊆ U is automatic (contractivity, Prop. 5.6a) -- the
        nontrivial direction, and the actual content of this check, is
        U ⊆ reduction(U): every a ∈ U must have a witness x with x ⊩ a
        and N(x) ⊆ U. Do not conflate this with mere contractivity.
        """
        return self.reduction(U) == U

    # =========== Compatibility ===========

    def check_compatibility(self, a: S, U: Set[S], V: Set[S]) -> Optional[S]:
        """
        Check the compatibility axiom:
        If a ◁ U and a ⋉ V, find u ∈ U with u ⋉ V.

        Returns the witnessing u, or None if the preconditions fail.
        For the structured version (with counterexample/provenance), use
        compatibility_certificate().
        """
        cert = self.compatibility_certificate(a, U, V)
        return cert.surviving_refinement

    def compatibility_certificate(
        self, a: S, U: Set[S], V: Set[S]
    ) -> CompatibilityCertificate[X, S]:
        """
        Structured version of the compatibility check (survey Prop. 5.10):
        (a ◁ U) ∧ (a ⋉ V) ⟹ ∃u∈U. u ⋉ V
        """
        if not self.covers(a, U):
            return CompatibilityCertificate(
                holds=False,
                source_generator=a,
                cover_family=U,
                positive_region=V,
                counterexample="precondition failed: not (a ◁ U)",
                reason_code="precondition_cover_failed",
            )
        if not self.positive(a, V):
            return CompatibilityCertificate(
                holds=False,
                source_generator=a,
                cover_family=U,
                positive_region=V,
                counterexample="precondition failed: not (a ⋉ V)",
                reason_code="precondition_positive_failed",
            )

        for u in U:
            if self.positive(u, V):
                return CompatibilityCertificate(
                    holds=True,
                    source_generator=a,
                    cover_family=U,
                    positive_region=V,
                    surviving_refinement=u,
                    reason_code="compatibility_holds",
                )

        # For a point-derived IncidenceSystem this is a proven theorem and
        # should be unreachable; surfaced as a certificate rather than a
        # raised exception so callers can log/report it uniformly.
        return CompatibilityCertificate(
            holds=False,
            source_generator=a,
            cover_family=U,
            positive_region=V,
            counterexample="no u in U with u positive in V (theorem violated -- check inputs)",
            reason_code="compatibility_axiom_violated",
        )

    # =========== Singleton Reconstruction (survey Theorem 8.1) ===========

    def reconstruct_forcing_from_ext(self) -> ForcingRelation[X, S]:
        """
        Rebuild the forcing relation from ext alone, using:
            x ⊩ a  iff  x ∈ ext({a})

        Should reproduce the original ForcingRelation's `forces` behavior
        exactly (see tests/test_core.py for the round-trip check).
        """
        rebuilt: ForcingRelation[X, S] = ForcingRelation()
        for a in self.forcing.observables:
            for x in self.ext({a}):
                rebuilt.add(x, [a])
        return rebuilt

    def reconstruct_forcing_from_diamond(self) -> ForcingRelation[X, S]:
        """
        Rebuild the forcing relation from diamond alone, using:
            x ⊩ a  iff  a ∈ diamond({x})
        """
        rebuilt: ForcingRelation[X, S] = ForcingRelation()
        for x in self.forcing.points:
            observables = self.diamond({x})
            if observables:
                rebuilt.add(x, observables)
        return rebuilt

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

    # =========== Bridge to the primitive/pointfree interface ===========

    def to_formal_positive_topology(self):
        """
        Wrap this derived system behind the FormalPositiveTopology
        interface (postop.formal), where cover/positivity are treated as
        primitive rather than derived. Useful to exercise the same
        validators against both the point-derived and pointfree cases.
        """
        from .formal import FormalPositiveTopology

        return FormalPositiveTopology(
            generators=set(self.forcing.observables),
            cover=self.covers,
            positive=self.positive,
        )

    # =========== Deprecated aliases (pre-canonical-rename names) ===========
    # Kept so existing code keeps working; each emits a DeprecationWarning
    # and delegates to the canonical method. See docs/ARCHITECTURE.md.

    def Ext(self, U: Set[S]) -> Set[X]:
        _deprecated("Ext", "ext")
        return self.ext(U)

    def Int(self, E: Set[X]) -> Set[S]:
        _deprecated("Int", "box")
        return self.box(E)

    def Hit(self, C: Set[X]) -> Set[S]:
        _deprecated("Hit", "diamond")
        return self.diamond(C)

    def Sel(self, U: Set[S]) -> Set[X]:
        _deprecated("Sel", "rest")
        return self.rest(U)

    def J(self, U: Set[S]) -> Set[S]:
        _deprecated("J", "reduction")
        return self.reduction(U)

    def j(self, U: Set[S]) -> Set[S]:
        _deprecated("j", "saturation")
        return self.saturation(U)

    def __repr__(self) -> str:
        return f"IncidenceSystem({self.forcing!r})"


# Backward-compatible alias: the historical class name for IncidenceSystem.
# `from postop import PosTop` keeps working; new code should prefer
# IncidenceSystem, which names what the class actually is (one derived
# topology among possibly several -- "PosTop" is the package/paper name).
PosTop = IncidenceSystem


# =========== Convenience Functions ===========


def from_dict(data: Dict[Any, List[Any]]) -> ForcingRelation:
    """Create a forcing relation from a dict of point -> observables."""
    fr = ForcingRelation()
    for point, observables in data.items():
        fr.add(point, observables)
    return fr
