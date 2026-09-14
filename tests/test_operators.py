from postop import IncidenceSystem, OperatorSuite, from_dict


def build_system() -> IncidenceSystem[str, str]:
    data = {
        "x1": ["a", "b"],
        "x2": ["b", "c"],
        "x3": ["a"],
    }
    return IncidenceSystem(from_dict(data))


def test_operator_suite_trace() -> None:
    ops = OperatorSuite(build_system())
    ext, info = ops.ext({"a"}, trace=True)
    assert ext == {"x1", "x3"}
    assert info is not None
    assert info.operator == "ext"
    assert info.inputs == {"U": {"a"}}

    diamond, diamond_info = ops.diamond({"x1", "x2"}, trace=True)
    assert diamond == {"a", "b", "c"}
    assert diamond_info and diamond_info.operator == "diamond"


def test_explain_chain_reports_missing_witnesses() -> None:
    ops = OperatorSuite(build_system())
    messages = list(ops.explain_chain("a", {"a", "b"}))
    assert messages[0].startswith("Cover holds")
    assert any("x1" in msg for msg in messages[1:])
    assert any("x3" in msg for msg in messages[1:])

    messages = list(ops.explain_chain("b", {"a"}))
    assert messages[0].startswith("Cover fails")
    assert "x2" in messages[0]
