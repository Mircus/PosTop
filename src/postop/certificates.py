"""
Certificate types: structured, JSON-serializable evidence objects.

Every "does this hold?" question in PosTop can be answered with a bare
bool, but a bool alone discards the witness or counterexample that
justified it. The classes in this module are the structured alternative:
each carries a verdict *plus* the evidence, so a caller (a human, a log,
or eventually a HYRI Validator/Critic) can inspect *why*, not just *what*.

These are pure, immutable data. Building one never mutates the
IncidenceSystem/FormalPositiveTopology it was derived from, and nothing
here makes a decision on the caller's behalf -- PosTop supplies evidence,
not adoption/authority semantics (see docs/ARCHITECTURE.md).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar

X = TypeVar("X")
S = TypeVar("S")


def _jsonify(value: Any) -> Any:
    """Best-effort conversion of set/dict-valued fields into JSON-safe shapes."""
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=str)
    if isinstance(value, dict):
        return {str(k): _jsonify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonify(v) for v in value]
    return value


class _CertificateMixin:
    """Shared to_dict() behavior for every certificate type below.

    Not a dataclass itself, so it does not interfere with field ordering
    when mixed into a frozen dataclass subclass.
    """

    def to_dict(self) -> Dict[str, Any]:
        return {k: _jsonify(v) for k, v in asdict(self).items()}  # type: ignore[call-overload]


@dataclass(frozen=True)
class CoverCertificate(_CertificateMixin, Generic[X, S]):
    """Evidence for/against a cover claim ``a ◁ U``."""

    subject: S
    claim: str  # human-readable rendering, e.g. "a ◁ U"
    region: Any  # the set U (kept generic; Set[S] in practice)
    holds: bool
    witnesses: Dict[X, Any] = field(default_factory=dict)
    counterexample: Optional[X] = None
    reason_code: str = ""


@dataclass(frozen=True)
class PositivityCertificate(_CertificateMixin, Generic[X, S]):
    """Evidence for/against a positivity claim ``a ⋉ U``."""

    subject: S
    claim: str
    region: Any
    holds: bool
    witness: Optional[X] = None
    witness_profile: Any = None
    reason_code: str = ""


@dataclass(frozen=True)
class CounterexampleCertificate(_CertificateMixin, Generic[X, S]):
    """A standalone counterexample record (e.g. why a candidate failed)."""

    subject: S
    claim: str
    counterexample: Optional[X]
    explanation: str
    reason_code: str = ""


@dataclass(frozen=True)
class CompatibilityCertificate(_CertificateMixin, Generic[X, S]):
    """
    Evidence for/against the compatibility axiom (survey Prop. 5.10):

        (a ◁ U) ∧ (a ⋉ V)  ⟹  ∃ u∈U. u ⋉ V

    In the point-derived case (IncidenceSystem) this is a theorem and
    should always hold; in the primitive/pointfree case
    (FormalPositiveTopology) it is an assumption the caller supplies data
    for, and this certificate is how a validator checks it.
    """

    holds: bool
    source_generator: S
    cover_family: Any  # U
    positive_region: Any  # V
    surviving_refinement: Optional[S] = None  # the witnessing u ∈ U
    counterexample: Optional[str] = None
    reason_code: str = ""


@dataclass(frozen=True)
class BudgetCertificate(_CertificateMixin, Generic[X, S]):
    """
    Provenance for a budget-gated evaluation: which checks were affordable,
    which weren't, and what verdict resulted.

    Deliberately does NOT claim the verdict is monotone in the budget --
    the survey (§9) shows cover/positivity can flip in either direction
    as budget increases; see tests/test_costs.py for concrete
    counterexamples.
    """

    budget: Any
    verdict: Optional[bool]
    affordable_observations: Any = field(default_factory=list)
    unaffordable_observations: Any = field(default_factory=list)
    witness: Optional[X] = None
    counterexample: Optional[X] = None
    assumptions: List[str] = field(default_factory=list)
    reason_code: str = ""


@dataclass(frozen=True)
class DiscriminatorSuggestion(_CertificateMixin, Generic[S]):
    """
    A *heuristic* suggestion for the next-cheapest observation that would
    discriminate among surviving hypotheses.

    Not claimed optimal unless a specific optimality proof is attached --
    see postop.costs.suggest_next_test.
    """

    observable: Optional[S]
    estimated_cost: Optional[Any]
    surviving_hypotheses_before: Any
    discriminates: bool
    reason_code: str = ""
