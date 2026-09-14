"""
Tests for the primitive/pointfree interface (postop.formal), and for the
bridge from a point-derived IncidenceSystem into it.
"""

from postop import FormalPositiveTopology, IncidenceSystem, from_dict


def test_bridge_from_incidence_system_preserves_compatibility() -> None:
    data = {"x1": ["a", "b"], "x2": ["b", "c"], "x3": ["a"]}
    system = IncidenceSystem(from_dict(data))
    formal = system.to_formal_positive_topology()

    assert isinstance(formal, FormalPositiveTopology)
    assert formal.generators == {"a", "b", "c"}

    cert = formal.validate_compatibility("a", {"a", "b"}, {"a", "b"})
    assert cert.holds is True
    assert cert.surviving_refinement in {"a", "b"}


def test_primitive_relations_supplied_directly() -> None:
    # No points at all -- cover/positive are given as raw callables, as
    # in the formal/pointfree case the survey describes. Here both
    # relations are the trivial "membership" relation: a ◁ U / a ⋉ U iff
    # a ∈ U.
    def cover(a, U):
        return a in U

    def positive(a, U):
        return a in U

    formal = FormalPositiveTopology(generators={"a", "b", "top"}, cover=cover, positive=positive)

    holds = formal.validate_compatibility("top", {"a", "b"}, {"a"})
    # "top" ◁ {a,b} is False under membership-cover, so compatibility
    # should report the cover precondition failing, not crash.
    assert holds.holds is False
    assert holds.reason_code == "precondition_cover_failed"

    holds_ok = formal.validate_compatibility("a", {"a"}, {"a"})
    assert holds_ok.holds is True
    assert holds_ok.surviving_refinement == "a"


def test_axiom_violation_is_reported_not_raised() -> None:
    # A deliberately inconsistent (cover, positive) pair: satisfies the
    # preconditions but violates the axiom's conclusion. This is exactly
    # what FormalPositiveTopology is for catching -- unlike
    # IncidenceSystem, where the axiom is a theorem, here it's data the
    # caller must validate.
    def cover(a, U):
        return True  # trivially "a implies everything"

    def positive(a, U):
        return a == "z"  # only "z" is ever positive, in any region

    formal = FormalPositiveTopology(generators={"a", "z"}, cover=cover, positive=positive)
    cert = formal.validate_compatibility("z", {"a"}, {"a"})
    assert cert.holds is False
    assert cert.reason_code == "compatibility_axiom_violated"
