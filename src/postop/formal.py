"""
FormalPositiveTopology: the primitive/pointfree case.

The survey (§1-8) distinguishes two ways to obtain cover and positivity:

- point-derived: given a forcing table x ⊩ a, cover and positivity are
  DERIVED via the ext/box and diamond/rest adjunctions, and the
  compatibility axiom is a PROVEN theorem (Prop. 5.10). This is
  postop.core.IncidenceSystem.

- formal/pointfree: cover (◁) and positivity (⋉) are taken as PRIMITIVE
  relations on a set of generators, with no underlying set of points at
  all, and compatibility with cover is imposed as an AXIOM rather than
  derived.

This module implements the second case. It does not (and cannot) derive
cover/positivity from anything -- the caller supplies both relations as
data (or callables), and FormalPositiveTopology's job is limited to
*validating* the compatibility axiom for given inputs and producing a
certificate, exactly as a formal topologist would check the axiom holds
for a proposed cover/positivity pair.

Do not treat this as a fuller or "more correct" replacement for
IncidenceSystem -- it is the other, complementary case the paper
describes, useful when you have direct axiomatic knowledge of cover and
positivity without an underlying incidence table.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Set, TypeVar

from .certificates import CompatibilityCertificate

S = TypeVar("S")

CoverRelation = Callable[[S, Set[S]], bool]
PositivityRelation = Callable[[S, Set[S]], bool]


@dataclass
class FormalPositiveTopology(Generic[S]):
    """
    A Positive Topology given directly by generators plus primitive cover
    and positivity relations (no points, no forcing table).

    Attributes:
        generators: the set of basic opens/generators S.
        cover: a callable implementing a ◁ U.
        positive: a callable implementing a ⋉ U.
    """

    generators: Set[S]
    cover: CoverRelation
    positive: PositivityRelation

    def validate_compatibility(
        self, a: S, U: Set[S], V: Set[S]
    ) -> CompatibilityCertificate[None, S]:
        """
        Check the compatibility axiom for the given a, U, V using the
        supplied (primitive) cover/positive relations:

            (a ◁ U) ∧ (a ⋉ V)  ⟹  ∃ u∈U. u ⋉ V

        Unlike IncidenceSystem.compatibility_certificate, this is NOT a
        theorem here -- it is exactly the axiom a formal topology is
        required to satisfy, and this method is how a caller (e.g. a
        validator) checks that a proposed (cover, positive) pair actually
        satisfies it for a given instance.
        """
        if not self.cover(a, U):
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

        return CompatibilityCertificate(
            holds=False,
            source_generator=a,
            cover_family=U,
            positive_region=V,
            counterexample="no u in U with u positive in V -- axiom fails for this instance",
            reason_code="compatibility_axiom_violated",
        )
