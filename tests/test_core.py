"""
Pytest-based tests for the PosTop core module.
"""

import pytest

from postop import ForcingRelation, PosTop, from_dict


@pytest.fixture
def forcing_relation() -> ForcingRelation[str, str]:
    fr = ForcingRelation[str, str]()
    fr.add("x1", ["a", "b"])
    fr.add("x2", ["b", "c"])
    fr.add("x3", ["a", "c"])
    return fr


@pytest.fixture
def simple_topology() -> PosTop[str, str]:
    data = {
        "x1": ["a", "b"],
        "x2": ["b", "c"],
        "x3": ["a"],
    }
    return PosTop(from_dict(data))


def test_forces_and_neighborhood(forcing_relation: ForcingRelation[str, str]) -> None:
    assert forcing_relation.forces("x1", "a")
    assert forcing_relation.forces("x1", "b")
    assert not forcing_relation.forces("x1", "c")
    assert forcing_relation.neighborhood("x1") == {"a", "b"}
    assert forcing_relation.neighborhood("x2") == {"b", "c"}


def test_extension_and_profiles_are_consistent(forcing_relation: ForcingRelation[str, str]) -> None:
    # Adding a point twice merges the profiles instead of replacing them.
    forcing_relation.add("x1", ["c"])
    assert forcing_relation.neighborhood("x1") == {"a", "b", "c"}
    assert forcing_relation.extension("a") == {"x1", "x3"}
    assert forcing_relation.extension("c") == {"x1", "x2", "x3"}


def test_len_contains_iter(forcing_relation: ForcingRelation[str, str]) -> None:
    assert len(forcing_relation) == 3
    assert "x1" in forcing_relation
    assert list(iter(forcing_relation)) == ["x1", "x2", "x3"]


def test_Ext(simple_topology: PosTop[str, str]) -> None:
    assert simple_topology.Ext({"a"}) == {"x1", "x3"}
    assert simple_topology.Ext({"a", "b"}) == {"x1", "x2", "x3"}


def test_Int(simple_topology: PosTop[str, str]) -> None:
    assert simple_topology.Int({"x1", "x3"}) == {"a"}


def test_Hit(simple_topology: PosTop[str, str]) -> None:
    assert simple_topology.Hit({"x1"}) == {"a", "b"}
    assert simple_topology.Hit({"x1", "x2"}) == {"a", "b", "c"}


def test_Sel(simple_topology: PosTop[str, str]) -> None:
    assert simple_topology.Sel({"a"}) == {"x3"}
    assert simple_topology.Sel({"a", "b"}) == {"x1", "x3"}


def test_J(simple_topology: PosTop[str, str]) -> None:
    assert simple_topology.J({"a"}) == {"a"}
    assert simple_topology.J({"a", "b"}) == {"a", "b"}


def test_covers(simple_topology: PosTop[str, str]) -> None:
    assert simple_topology.covers("a", {"a", "b"})
    assert not simple_topology.covers("b", {"a"})


def test_positive(simple_topology: PosTop[str, str]) -> None:
    assert simple_topology.positive("a", {"a"})
    assert not simple_topology.positive("b", {"b"})


def test_cover_explanations(simple_topology: PosTop[str, str]) -> None:
    witnesses = simple_topology.covers_witnesses("a", {"a", "b"})
    assert witnesses == {"x1": {"a", "b"}, "x3": {"a"}}

    counterexample = simple_topology.covers_counterexample("b", {"a"})
    assert counterexample == "x2"

    cover_details = simple_topology.explain_cover("b", {"a"})
    assert cover_details["holds"] is False
    assert cover_details["counterexample"] == "x2"


def test_find_witness(simple_topology: PosTop[str, str]) -> None:
    assert simple_topology.find_witness("a", {"a"}) == "x3"
    assert simple_topology.find_witness("b", {"b"}) is None


def test_formal_closed(simple_topology: PosTop[str, str]) -> None:
    assert simple_topology.is_formal_closed({"a"})
    assert not simple_topology.is_formal_closed({"b"})


def test_compatibility(simple_topology: PosTop[str, str]) -> None:
    u = simple_topology.check_compatibility("a", {"a", "b"}, {"a", "b"})
    assert u in {"a", "b"}
    assert simple_topology.positive(u, {"a", "b"})


def test_J_contractive_and_idempotent() -> None:
    data = {
        "x1": ["a", "b", "c"],
        "x2": ["a", "d"],
        "x3": ["b", "c"],
    }
    pt = PosTop(from_dict(data))
    test_sets = [{"a"}, {"b"}, {"a", "b"}, {"a", "b", "c"}, {"a", "b", "c", "d"}]

    for U in test_sets:
        J_U = pt.J(U)
        assert J_U <= U
        assert pt.J(J_U) == J_U
