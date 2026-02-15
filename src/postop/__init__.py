"""
PosTop: Positive Topology for Grounded AI

A framework for building AI systems with:
- Grounded inference (every claim has a witness)
- Semantic entailment (covers track implications)  
- Resource awareness (cheapest verification first)
- Explainable reasoning (cover chains)
"""

from .core import (
    ForcingRelation,
    PosTop,
    from_dict,
)

from .costs import (
    CostDomain,
    BooleanDomain,
    LawvereDomain,
    CostForcing,
    CostPosTop,
)

from .operators import (
    OperatorSuite,
    OperatorTrace,
)

from .llm import (
    ClaimNormalizer,
    PosTopGuardrail,
)

__version__ = "0.1.0"
__all__ = [
    "ForcingRelation",
    "PosTop", 
    "from_dict",
    "CostDomain",
    "BooleanDomain",
    "LawvereDomain",
    "CostForcing",
    "CostPosTop",
    "OperatorSuite",
    "OperatorTrace",
    "ClaimNormalizer",
    "PosTopGuardrail",
]
