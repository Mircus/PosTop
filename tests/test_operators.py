from postop import OperatorSuite, PosTop, from_dict


def build_topology() -> PosTop[str, str]:
    data = {
        "x1": ["a", "b"],
        "x2": ["b", "c"],
        "x3": ["a"],
    }
    return PosTop(from_dict(data))


def test_operator_suite_trace() -> None:
    ops = OperatorSuite(build_topology())
    ext, info = ops.ext({"a"}, trace=True)
    assert ext == {"x1", "x3"}
    assert info is not None
    assert info.operator == "Ext"
    assert info.inputs == {"U": {"a"}}

    hit, hit_info = ops.hit({"x1", "x2"}, trace=True)
    assert hit == {"a", "b", "c"}
    assert hit_info and hit_info.operator == "Hit"


def test_explain_chain_reports_missing_witnesses() -> None:
    ops = OperatorSuite(build_topology())
    messages = list(ops.explain_chain("a", {"a", "b"}))
    assert messages[0].startswith("Cover holds")
    assert any("x1" in msg for msg in messages[1:])
    assert any("x3" in msg for msg in messages[1:])

    messages = list(ops.explain_chain("b", {"a"}))
    assert messages[0].startswith("Cover fails")
    assert "x2" in messages[0]
