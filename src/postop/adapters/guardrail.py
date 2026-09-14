"""
An illustrative, provider-neutral adapter for checking LLM-style claims
against a PosTop IncidenceSystem.

This is an ADAPTER, not core PosTop: it has no dependency on any LLM
provider (no API calls, no network), and core PosTop
(postop.core / postop.formal / postop.certificates) has no dependency on
this module either -- the arrow points one way.

Typing gap this module makes explicit (survey Appendix A.4): an LLM
hypothesis string is NOT automatically a PosTop generator. A concrete
system must supply an explicit encoding of hypotheses (and of the
current observation state) into the formal structure before any cover
or positivity expression is well typed. `PosTopGuardrail` below defaults
both encodings to `ClaimNormalizer.normalize` -- a real but deliberately
simple string -> string mapping -- rather than a bare identity, and both
encodings are constructor parameters so a caller can supply a real
hypothesis/observation encoder (`ι: H -> S`, in the paper's notation).
Treat the default as a demo convenience, not a recommendation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set

from ..core import IncidenceSystem


@dataclass
class ClaimNormalizer:
    """
    Map arbitrary textual claims to canonical observables.

    This is a real (if simple) hypothesis -> generator encoding: an
    alias table. It is NOT a claim that arbitrary natural-language
    hypotheses reduce to alias lookups in general -- only that this is
    the minimal encoding needed to make the demo well typed.
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
    """
    Checks whether a claim (i) follows from an observed context (cover)
    and (ii) has a confined witness (positivity), and reports one of
    VALID / UNGROUNDED / NON-SEQUITUR / INVALID.

    `encode_hypothesis` / `encode_observation` are the explicit
    hypothesis/observation -> generator encodings discussed in the
    module docstring; both default to `normalizer.normalize`.
    """

    def __init__(
        self,
        topology: IncidenceSystem[str, str],
        normalizer: Optional[ClaimNormalizer] = None,
        encode_hypothesis: Optional[Callable[[str], str]] = None,
        encode_observation: Optional[Callable[[str], str]] = None,
    ):
        self.pt = topology
        self.normalizer = normalizer or ClaimNormalizer()
        self.encode_hypothesis = encode_hypothesis or self.normalizer.normalize
        self.encode_observation = encode_observation or self.normalizer.normalize

    def _format_status(self, encoded_claim: str, encoded_context: Set[str]) -> GuardrailResult:
        profile = set(encoded_context)
        profile.add(encoded_claim)
        covered = self.pt.covers(encoded_claim, encoded_context)
        grounded = self.pt.positive(encoded_claim, profile)
        witness = self.pt.find_witness(encoded_claim, profile)

        if covered and grounded:
            status = "VALID"
            explanation = f"'{encoded_claim}' follows from context and has witness '{witness}'."
        elif covered and not grounded:
            status = "UNGROUNDED"
            explanation = (
                f"'{encoded_claim}' follows from context but lacks a confined witness."
            )
        elif not covered and grounded:
            status = "NON-SEQUITUR"
            explanation = f"'{encoded_claim}' has a witness but does not follow from the observed context."
        else:
            status = "INVALID"
            explanation = f"'{encoded_claim}' neither follows from context nor has a witness."

        return GuardrailResult(
            claim=encoded_claim,
            status=status,
            covered=covered,
            grounded=grounded,
            witness=witness,
            explanation=explanation,
        )

    def check_claim(self, claim: str, context: Set[str]) -> GuardrailResult:
        encoded_claim = self.encode_hypothesis(claim)
        encoded_context = {self.encode_observation(item) for item in context}
        return self._format_status(encoded_claim, encoded_context)

    def filter_hypotheses(
        self, hypotheses: Sequence[str], observed: Set[str]
    ) -> Dict[str, object]:
        encoded_observed = {self.encode_observation(o) for o in observed}
        details = [
            self._format_status(self.encode_hypothesis(h), encoded_observed)
            for h in hypotheses
        ]
        valid = [item.claim for item in details if item.status == "VALID"]
        return {
            "observed": encoded_observed,
            "all_hypotheses": list(hypotheses),
            "valid_hypotheses": valid,
            "details": details,
        }

    def check_consistency(self, claims: Sequence[str]) -> Dict[str, object]:
        encoded = {self.encode_hypothesis(c) for c in claims}
        for x in self.pt.forcing.points:
            if encoded <= self.pt.forcing.neighborhood(x):
                return {
                    "consistent": True,
                    "claims": list(encoded),
                    "witness": x,
                    "explanation": f"All claims witnessed by '{x}'.",
                }
        return {
            "consistent": False,
            "claims": list(encoded),
            "witness": None,
            "explanation": "No single witness satisfies every claim.",
        }
