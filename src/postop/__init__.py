"""
PosTop: a reference implementation of the forcing-matrix view of
Positive Topology.

From one incidence relation x ⊩ a, two canonical Galois adjunctions
(ext ⊣ box, diamond ⊣ rest) induce cover, positivity, saturation, and
reduction -- plus witness/counterexample certificates for each. See
README.md for the "what is implemented / experimental / programmatic"
breakdown, and docs/ARCHITECTURE.md for the three-layer design.
"""

from .core import (
    ForcingRelation,
    IncidenceSystem,
    PosTop,
    from_dict,
)

from .formal import (
    FormalPositiveTopology,
)

from .certificates import (
    BudgetCertificate,
    CompatibilityCertificate,
    CounterexampleCertificate,
    CoverCertificate,
    DiscriminatorSuggestion,
    PositivityCertificate,
)

from .costs import (
    BooleanDomain,
    CostAnnotatedIncidence,
    CostDomain,
    CostForcing,
    CostPosTop,
    LawvereDomain,
    ThresholdSemantics,
)

from .operators import (
    OperatorSuite,
    OperatorTrace,
)

from .evaluate import (
    EvaluationResult,
    Evaluator,
)

# Re-exported from postop.adapters.guardrail for backward compatibility
# (importing directly here, not via the deprecated postop.llm shim, so a
# plain `import postop` does not itself raise a DeprecationWarning).
from .adapters.guardrail import (
    ClaimNormalizer,
    GuardrailResult,
    PosTopGuardrail,
)

__version__ = "0.2.0"
__all__ = [
    # core
    "ForcingRelation",
    "IncidenceSystem",
    "PosTop",
    "from_dict",
    # formal / pointfree
    "FormalPositiveTopology",
    # certificates
    "BudgetCertificate",
    "CompatibilityCertificate",
    "CounterexampleCertificate",
    "CoverCertificate",
    "DiscriminatorSuggestion",
    "PositivityCertificate",
    # costs / resource-bounded (experimental)
    "BooleanDomain",
    "CostAnnotatedIncidence",
    "CostDomain",
    "CostForcing",
    "CostPosTop",
    "LawvereDomain",
    "ThresholdSemantics",
    # operators / tracing
    "OperatorSuite",
    "OperatorTrace",
    # evaluation facade
    "EvaluationResult",
    "Evaluator",
    # adapters (illustrative, provider-neutral)
    "ClaimNormalizer",
    "GuardrailResult",
    "PosTopGuardrail",
]
