from postop import PosTop, PosTopGuardrail, ClaimNormalizer, from_dict


def build_guardrail() -> PosTopGuardrail:
    cases = {
        "case1": ["flu", "fever", "cough"],
        "case2": ["cold", "cough", "runny_nose"],
    }
    pt = PosTop(from_dict(cases))
    normalizer = ClaimNormalizer()
    normalizer.register("flu", "influenza")
    return PosTopGuardrail(pt, normalizer=normalizer)


def test_guardrail_check_claim() -> None:
    guardrail = build_guardrail()
    result = guardrail.check_claim("influenza", {"fever", "cough"})
    assert result.status == "VALID"
    assert result.witness in {"case1"}

    hallucination = guardrail.check_claim("flu", {"runny_nose"})
    assert hallucination.status in {"NON-SEQUITUR", "INVALID"}


def test_filter_and_consistency() -> None:
    guardrail = build_guardrail()
    payload = guardrail.filter_hypotheses(["flu", "cold"], {"cough", "runny_nose"})
    assert payload["valid_hypotheses"] == ["cold"]
    assert len(payload["details"]) == 2

    consistency = guardrail.check_consistency(["flu", "cold"])
    assert consistency["consistent"] is False
    assert "explanation" in consistency
