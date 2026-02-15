"""
Minimal LLM guardrail helpers built on PosTop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set

from .core import PosTop


@dataclass
class ClaimNormalizer:
    """
    Map arbitrary textual claims to canonical observables.
    """

    synonyms: Dict[str, str] = field(default_factory=dict)

    def register(self, canonical: str, *aliases: str) -> None:
        self.synonyms[canonical] = canonical
        for name in aliases:
            self.synonyms[name] = canonical

    def normalize(self, claim: str) -> str:
        return self.synonyms.get(claim, claim)

    def normalize_many(self, claims: Iterable[str]) -> List[str]:
        return [self.normalize(c) for c in claims]


@dataclass
class GuardrailResult:
    claim: str
    status: str
    covered: bool
    grounded: bool
    witness: Optional[str]
    explanation: str


class PosTopGuardrail:
    """Utility class mirroring the behavior shown in examples."""

    def __init__(
        self, topology: PosTop[str, str], normalizer: Optional[ClaimNormalizer] = None
    ):
        self.pt = topology
        self.normalizer = normalizer or ClaimNormalizer()

    def _format_status(self, claim: str, context: Set[str]) -> GuardrailResult:
        profile = set(context)
        profile.add(claim)
        covered = self.pt.covers(claim, context)
        grounded = self.pt.positive(claim, profile)
        witness = self.pt.find_witness(claim, profile)

        if covered and grounded:
            status = "VALID"
            explanation = f"'{claim}' follows from context and has witness '{witness}'."
        elif covered and not grounded:
            status = "UNGROUNDED"
            explanation = (
                f"'{claim}' follows from context but lacks a confined witness."
            )
        elif not covered and grounded:
            status = "NON-SEQUITUR"
            explanation = f"'{claim}' has a witness but does not follow from the observed context."
        else:
            status = "INVALID"
            explanation = f"'{claim}' neither follows from context nor has a witness."

        return GuardrailResult(
            claim=claim,
            status=status,
            covered=covered,
            grounded=grounded,
            witness=witness,
            explanation=explanation,
        )

    def check_claim(self, claim: str, context: Set[str]) -> GuardrailResult:
        normalized_claim = self.normalizer.normalize(claim)
        normalized_context = {self.normalizer.normalize(item) for item in context}
        return self._format_status(normalized_claim, normalized_context)

    def filter_hypotheses(
        self, hypotheses: Sequence[str], observed: Set[str]
    ) -> Dict[str, object]:
        normalized_observed = {self.normalizer.normalize(o) for o in observed}
        details = [
            self._format_status(self.normalizer.normalize(h), normalized_observed)
            for h in hypotheses
        ]
        valid = [item.claim for item in details if item.status == "VALID"]
        return {
            "observed": normalized_observed,
            "all_hypotheses": list(hypotheses),
            "valid_hypotheses": valid,
            "details": details,
        }

    def check_consistency(self, claims: Sequence[str]) -> Dict[str, object]:
        normalized = set(self.normalizer.normalize_many(claims))
        for x in self.pt.forcing.points:
            if normalized <= self.pt.forcing.neighborhood(x):
                return {
                    "consistent": True,
                    "claims": list(normalized),
                    "witness": x,
                    "explanation": f"All claims witnessed by '{x}'.",
                }
        return {
            "consistent": False,
            "claims": list(normalized),
            "witness": None,
            "explanation": "No single witness satisfies every claim.",
        }
