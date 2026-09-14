"""
A generic evaluation facade combining cover + positivity (and, when a
budgeted evidence source is supplied, a budget certificate) into a single
structured, JSON-serializable result.

Evaluator is intentionally the only "porcelain" surface in this module:
it never mutates the IncidenceSystem/CostAnnotatedIncidence it wraps, and
it never makes an adoption/decision call on the caller's behalf -- it
supplies evidence (certificates), not decisions. Orchestration, arbitration,
adoption, and budget *enforcement* stay outside PosTop -- see
docs/ARCHITECTURE.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

from .certificates import BudgetCertificate, CoverCertificate, PositivityCertificate
from .core import IncidenceSystem
from .costs import CostAnnotatedIncidence


@dataclass(frozen=True)
class EvaluationResult:
    """The combined result of one evaluate() call."""

    claim: Any
    cover: CoverCertificate
    positivity: PositivityCertificate
    consistent: bool
    budget: Optional[BudgetCertificate] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "claim": self.claim,
            "consistent": self.consistent,
            "cover": self.cover.to_dict(),
            "positivity": self.positivity.to_dict(),
        }
        if self.budget is not None:
            payload["budget"] = self.budget.to_dict()
        return payload


class Evaluator:
    """
    Evaluate a claim against evidence (and, optionally, a separate
    constraint envelope and/or a budget) via a fixed IncidenceSystem, or
    a CostAnnotatedIncidence when budget-gated evaluation is needed.
    """

    def __init__(self, system: IncidenceSystem, cost_source: Optional[CostAnnotatedIncidence] = None):
        self.system = system
        self.cost_source = cost_source

    def evaluate(
        self,
        claim: Any,
        evidence: Set[Any],
        constraints: Optional[Set[Any]] = None,
        budget: Optional[Any] = None,
    ) -> EvaluationResult:
        """
        Returns:
            EvaluationResult(claim, cover, positivity, consistent, budget)

        `evidence` is the set a cover check is evaluated against;
        `constraints` (defaulting to `evidence` if omitted) is the
        envelope a positivity witness must be confined to. If `budget`
        is given, this Evaluator must have been constructed with a
        `cost_source`, and cover/positivity are computed on the system
        sliced at that budget rather than on `self.system`.
        """
        envelope = constraints if constraints is not None else evidence

        budget_cert: Optional[BudgetCertificate] = None
        if budget is not None:
            if self.cost_source is None:
                raise ValueError(
                    "evaluate() was called with a budget but this Evaluator "
                    "has no cost_source (CostAnnotatedIncidence) to slice."
                )
            system = self.cost_source.to_incidence_system_within(budget)
            budget_cert = self.cost_source.budget_certificate(
                claim, envelope, budget, kind="positive"
            )
        else:
            system = self.system

        cover_cert = system.explain_cover(claim, evidence)
        positivity_cert = system.explain_positive(claim, envelope)

        return EvaluationResult(
            claim=claim,
            cover=cover_cert,
            positivity=positivity_cert,
            consistent=cover_cert.holds and positivity_cert.holds,
            budget=budget_cert,
        )
