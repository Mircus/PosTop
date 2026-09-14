"""
Pytest-based tests for the PosTop core module (canonical operator names).
"""

import warnings

import pytest

from postop import ForcingRelation, IncidenceSystem, from_dict


@pytest.fixture
def forcing_relation() -> ForcingRelation[str, str]:
    fr = ForcingRelation[str, str]()
    fr.add("x1", ["a", "b"])
    fr.add("x2", ["b", "c"])
    fr.add("x3", ["a", "c"])
    return fr


@pytest.fixture
def simple_system() -> IncidenceSystem[str, str]:
    data = {
        "x1": ["a", "b"],
        "x2": ["b", "c"],
        "x3": ["a"],
    }
    return IncidenceSystem(from_dict(data))


def test_forces_and_neighborhood(forcing_relation: ForcingRelation[str, str]) -> None:
    assert forcing_relation.forces("x1", "a")
    assert forcing_relation.forces("x1", "b")
    assert not forcing_relation.forces("x1", "c")
    assert forcing_relation.neighborhood("x1") == {"a", "b"}
    assert forcing_relation.neighborhood("x2") == {"b", "c"}


def test_extension_and_profiles_are_consistent(
    forcing_relation: ForcingRelation[str, str],
) -> None:
    # Adding a point twice merges the profiles instead of replacing them.
    forcing_relation.add("x1", ["c"])
    assert forcing_relation.neighborhood("x1") == {"a", "b", "c"}
    assert forcing_relation.extension("a") == {"x1", "x3"}
    assert forcing_relation.extension("c") == {"x1", "x2", "x3"}


def test_len_contains_iter(forcing_relation: ForcingRelation[str, str]) -> None:
    assert len(forcing_relation) == 3
    assert "x1" in forcing_relation
    assert list(iter(forcing_relation)) == ["x1", "x2", "x3"]


def test_ext(simple_system: IncidenceSystem[str, str]) -> None:
    assert simple_system.ext({"a"}) == {"x1", "x3"}
    assert simple_system.ext({"a", "b"}) == {"x1", "x2", "x3"}


def test_box(simple_system: IncidenceSystem[str, str]) -> None:
    assert simple_system.box({"x1", "x3"}) == {"a"}


def test_diamond(simple_system: IncidenceSystem[str, str]) -> None:
    assert simple_system.diamond({"x1"}) == {"a", "b"}
    assert simple_system.diamond({"x1", "x2"}) == {"a", "b", "c"}


def test_rest(simple_system: IncidenceSystem[str, str]) -> None:
    assert simple_system.rest({"a"}) == {"x3"}
    assert simple_system.rest({"a", "b"}) == {"x1", "x3"}


def test_reduction(simple_system: IncidenceSystem[str, str]) -> None:
    assert simple_system.reduction({"a"}) == {"a"}
    assert simple_system.reduction({"a", "b"}) == {"a", "b"}


def test_saturation_extensivity_monotonicity_idempotence(
    simple_system: IncidenceSystem[str, str],
) -> None:
    test_sets = [{"a"}, {"b"}, {"a", "b"}, {"a", "b", "c"}]
    for U in test_sets:
        assert U <= simple_system.saturation(U)  # extensivity: U ⊆ saturation(U)
        assert simple_system.saturation(simple_system.saturation(U)) == simple_system.saturation(U)
    assert simple_system.saturation({"a"}) <= simple_system.saturation({"a", "b"})  # monotone


def test_covers(simple_system: IncidenceSystem[str, str]) -> None:
    assert simple_system.covers("a", {"a", "b"})
    assert not simple_system.covers("b", {"a"})


def test_covers_agrees_with_extensional_inclusion(
    simple_system: IncidenceSystem[str, str],
) -> None:
    # a ◁ U iff ext({a}) ⊆ ext(U) -- the defining extensional reading (Remark 3.7).
    for a, U in [("a", {"a", "b"}), ("b", {"a"}), ("c", {"b", "c"})]:
        assert simple_system.covers(a, U) == (
            simple_system.ext({a}) <= simple_system.ext(U)
        )


def test_positive(simple_system: IncidenceSystem[str, str]) -> None:
    assert simple_system.positive("a", {"a"})
    assert not simple_system.positive("b", {"b"})


def test_positive_agrees_with_witness_profile_form(
    simple_system: IncidenceSystem[str, str],
) -> None:
    # a ⋉ U iff exists x with x ⊩ a and N(x) ⊆ U (Remark 5.3).
    for a, U in [("a", {"a"}), ("b", {"b"}), ("a", {"a", "b"})]:
        witness = simple_system.find_witness(a, U)
        assert simple_system.positive(a, U) == (witness is not None)
        if witness is not None:
            assert simple_system.forcing.forces(witness, a)
            assert simple_system.forcing.neighborhood(witness) <= U


def test_cover_explanations(simple_system: IncidenceSystem[str, str]) -> None:
    witnesses = simple_system.covers_witnesses("a", {"a", "b"})
    assert witnesses == {"x1": {"a", "b"}, "x3": {"a"}}

    counterexample = simple_system.covers_counterexample("b", {"a"})
    assert counterexample == "x2"

    cert = simple_system.explain_cover("b", {"a"})
    assert cert.holds is False
    assert cert.counterexample == "x2"
    assert cert.subject == "b"


def test_find_witness(simple_system: IncidenceSystem[str, str]) -> None:
    assert simple_system.find_witness("a", {"a"}) == "x3"
    assert simple_system.find_witness("b", {"b"}) is None


def test_explain_positive_certificate(simple_system: IncidenceSystem[str, str]) -> None:
    cert = simple_system.explain_positive("a", {"a"})
    assert cert.holds is True
    assert cert.witness == "x3"
    assert cert.witness_profile == {"a"}

    cert_fail = simple_system.explain_positive("b", {"b"})
    assert cert_fail.holds is False
    assert cert_fail.witness is None


# ---- Formal-closed fixed-point regression (item 8) ----
# J(U) ⊆ U is automatic (contractivity, Prop. 5.6a). The actual content
# of "U is formal closed" is the nontrivial reverse inclusion U ⊆ J(U):
# every a ∈ U needs a witness x with x ⊩ a and N(x) ⊆ U. A test that only
# checks contractivity (J(U) ⊆ U) would pass under the *wrong*
# characterization from an earlier draft ("if a patient profile is
# inside U then its symptoms are in U" -- which is just contractivity,
# true for every U, and proves nothing about closedness).


def test_formal_closed_is_not_mere_contractivity(
    simple_system: IncidenceSystem[str, str],
) -> None:
    # Contractivity holds for every U, including non-closed ones -- so it
    # cannot be what "formal closed" means.
    for U in [{"a"}, {"b"}, {"a", "b"}, {"a", "b", "c"}, set()]:
        assert simple_system.reduction(U) <= U  # contractivity: always true

    # {"a"} IS formal closed: x3 forces a and N(x3) = {a} ⊆ {a}.
    assert simple_system.is_formal_closed({"a"})
    assert simple_system.reduction({"a"}) == {"a"}

    # {"b"} is NOT formal closed: no point forces b with a profile ⊆ {b}
    # (x1's profile is {a,b}, x2's is {b,c}) -- contractivity alone would
    # wrongly suggest reduction({"b"}) == {} ⊆ {"b"} "looks fine", but the
    # fixed-point condition reduction(U) == U correctly fails here.
    assert not simple_system.is_formal_closed({"b"})
    assert simple_system.reduction({"b"}) == set()  # b has no confined witness
    assert simple_system.reduction({"b"}) != {"b"}


def test_compatibility(simple_system: IncidenceSystem[str, str]) -> None:
    u = simple_system.check_compatibility("a", {"a", "b"}, {"a", "b"})
    assert u in {"a", "b"}
    assert simple_system.positive(u, {"a", "b"})


def test_compatibility_certificate(simple_system: IncidenceSystem[str, str]) -> None:
    cert = simple_system.compatibility_certificate("a", {"a", "b"}, {"a", "b"})
    assert cert.holds is True
    assert cert.surviving_refinement in {"a", "b"}
    assert cert.source_generator == "a"

    failing = simple_system.compatibility_certificate("b", {"a"}, {"a", "b"})
    assert failing.holds is False
    assert failing.reason_code == "precondition_cover_failed"

    # Certificate is JSON-serializable.
    payload = cert.to_dict()
    assert payload["holds"] is True
    assert isinstance(payload["cover_family"], list)


def test_reduction_contractive_and_idempotent() -> None:
    data = {
        "x1": ["a", "b", "c"],
        "x2": ["a", "d"],
        "x3": ["b", "c"],
    }
    system = IncidenceSystem(from_dict(data))
    test_sets = [{"a"}, {"b"}, {"a", "b"}, {"a", "b", "c"}, {"a", "b", "c", "d"}]

    for U in test_sets:
        reduced = system.reduction(U)
        assert reduced <= U
        assert system.reduction(reduced) == reduced

    # monotonicity
    assert system.reduction({"a"}) <= system.reduction({"a", "b"})


# ---- Singleton reconstruction (survey Theorem 8.1, item 9) ----


def test_singleton_reconstruction_from_ext(simple_system: IncidenceSystem[str, str]) -> None:
    rebuilt = simple_system.reconstruct_forcing_from_ext()
    original = simple_system.forcing
    all_points = original.points | rebuilt.points
    all_observables = original.observables | rebuilt.observables
    for x in all_points:
        for a in all_observables:
            assert original.forces(x, a) == rebuilt.forces(x, a)


def test_singleton_reconstruction_from_diamond(simple_system: IncidenceSystem[str, str]) -> None:
    rebuilt = simple_system.reconstruct_forcing_from_diamond()
    original = simple_system.forcing
    all_points = original.points | rebuilt.points
    all_observables = original.observables | rebuilt.observables
    for x in all_points:
        for a in all_observables:
            assert original.forces(x, a) == rebuilt.forces(x, a)


# ---- Deprecated aliases still work, with a DeprecationWarning ----


def test_deprecated_aliases_delegate_and_warn(simple_system: IncidenceSystem[str, str]) -> None:
    pairs = [
        ("Ext", "ext", ({"a"},)),
        ("Int", "box", ({"x1", "x3"},)),
        ("Hit", "diamond", ({"x1"},)),
        ("Sel", "rest", ({"a"},)),
        ("J", "reduction", ({"a"},)),
        ("j", "saturation", ({"a"},)),
    ]
    for old_name, new_name, args in pairs:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            old_result = getattr(simple_system, old_name)(*args)
        assert any(issubclass(w.category, DeprecationWarning) for w in caught)
        new_result = getattr(simple_system, new_name)(*args)
        assert old_result == new_result
