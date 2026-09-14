"""
Example (adapter demo): grounding LLM-style hypotheses with PosTop.

This is an illustrative ADAPTER built on top of core PosTop, not part of
the core package -- see src/postop/adapters/guardrail.py and the survey's
Appendix A.4. It shows:
- Checking whether LLM claims are grounded (have witnesses)
- Checking whether claims are consistent (no contradictions)
- The explicit hypothesis/observation -> generator encoding step the
  earlier draft of this example skipped (an LLM string is NOT
  automatically a PosTop generator -- see encode_hypothesis below).
"""

from typing import List

from postop import IncidenceSystem, from_dict
from postop.adapters import PosTopGuardrail


def simulate_llm_response(query: str) -> List[str]:
    """Simulate an LLM generating hypotheses."""
    # In practice, this would call an actual LLM.
    if "fever" in query and "cough" in query:
        return ["flu", "covid", "pneumonia", "common_cold", "tuberculosis"]
    return ["unknown"]


def encode_hypothesis(hypothesis: str) -> str:
    """
    ι: H -> S -- map a raw LLM hypothesis string to a PosTop generator.

    In this demo the encoding is the identity (hypothesis strings already
    match the disease-name generators in `cases` below), which is a
    simplification specific to this toy scenario, not a general recipe.
    A real system's encoding typically involves entity linking, ontology
    lookup, or a classifier, and may map one hypothesis to several
    generators or reject it entirely.
    """
    return hypothesis


def encode_observation_state(observed_symptoms) -> set:
    """
    Map the current observation state (whatever form it arrives in) to a
    set of PosTop generators. Here it's already a set of symptom strings,
    so this is also the identity -- again, a simplification worth naming
    explicitly rather than leaving implicit.
    """
    return set(observed_symptoms)


def main():
    print("=" * 60)
    print("LLM GUARDRAIL ADAPTER DEMO")
    print("=" * 60)

    # =========== Build the knowledge base ===========
    # This would typically come from a medical ontology

    # Each "case" represents a prototypical disease profile
    cases = {
        "flu_case_1": ["flu", "fever", "cough", "fatigue", "myalgia"],
        "flu_case_2": ["flu", "fever", "headache", "fatigue"],
        "covid_case_1": ["covid", "fever", "cough", "fatigue", "loss_of_taste"],
        "covid_case_2": ["covid", "fever", "cough", "shortness_of_breath"],
        "cold_case_1": ["common_cold", "cough", "runny_nose", "sneezing"],
        "cold_case_2": ["common_cold", "cough", "sore_throat"],
        "pneumonia_case_1": [
            "pneumonia",
            "fever",
            "cough",
            "chest_pain",
            "infiltrates",
        ],
        "tb_case_1": ["tuberculosis", "fever", "cough", "night_sweats", "weight_loss"],
    }

    forcing = from_dict(cases)
    system = IncidenceSystem(forcing)
    guardrail = PosTopGuardrail(
        system,
        encode_hypothesis=encode_hypothesis,
        encode_observation=lambda symptom: symptom,  # per-item identity (see encode_observation_state below)
    )

    print("\nKnowledge base (disease profiles):")
    for case, profile in cases.items():
        print(f"  {case}: {profile}")

    # =========== Scenario 1: Valid diagnosis ===========
    print("\n" + "=" * 60)
    print("SCENARIO 1: Patient with fever, cough, fatigue")
    print("=" * 60)

    observed = encode_observation_state({"fever", "cough", "fatigue"})
    print(f"\nObserved symptoms: {observed}")

    # Simulate LLM response
    llm_hypotheses = simulate_llm_response("fever cough")
    print(f"LLM hypotheses (raw): {llm_hypotheses}")
    print(f"Encoded hypotheses: {[encode_hypothesis(h) for h in llm_hypotheses]}")

    # Filter through guardrail
    result = guardrail.filter_hypotheses(llm_hypotheses, observed)
    print(f"\nValid hypotheses: {result['valid_hypotheses']}")

    print("\nDetails:")
    for detail in result["details"]:
        print(f"  {detail.claim}: {detail.status}")
        print(f"    {detail.explanation}")

    # =========== Scenario 2: Hallucination detection ===========
    print("\n" + "=" * 60)
    print("SCENARIO 2: LLM claims 'tuberculosis' for mild symptoms")
    print("=" * 60)

    observed = encode_observation_state({"cough", "runny_nose"})
    print(f"\nObserved symptoms: {observed}")

    check = guardrail.check_claim("tuberculosis", observed)
    print("\nClaim: 'tuberculosis'")
    print(f"Status: {check.status}")
    print(f"Explanation: {check.explanation}")

    # =========== Scenario 3: Consistency check ===========
    print("\n" + "=" * 60)
    print("SCENARIO 3: Checking consistency of multiple claims")
    print("=" * 60)

    claims1 = ["fever", "cough", "fatigue"]
    result1 = guardrail.check_consistency(claims1)
    print(f"\nClaims: {claims1}")
    print(f"Consistent: {result1['consistent']}")
    print(f"Explanation: {result1['explanation']}")

    claims2 = ["flu", "covid"]
    result2 = guardrail.check_consistency(claims2)
    print(f"\nClaims: {claims2}")
    print(f"Consistent: {result2['consistent']}")
    print(f"Explanation: {result2['explanation']}")

    # =========== Scenario 4: Explain reasoning ===========
    print("\n" + "=" * 60)
    print("SCENARIO 4: Explaining why 'flu' is valid")
    print("=" * 60)

    observed = encode_observation_state({"fever", "cough", "fatigue", "myalgia"})
    print(f"\nObserved: {observed}")

    explanation = system.explain("flu", observed)
    print("\nExplanation for 'flu':")
    print(f"  Covers observed: {explanation['covers']}")
    print(f"  Has witness: {explanation['has_witness']}")
    print(f"  Witness: {explanation['witness']}")
    print(f"  Consistent: {explanation['consistent']}")


if __name__ == "__main__":
    main()
