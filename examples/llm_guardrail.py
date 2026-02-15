"""
Example: LLM Guardrail with Positive Topology

This example shows how to use PosTop as a guardrail for LLM outputs:
- Check if LLM claims are grounded (have witnesses)
- Check if claims are consistent (no contradictions)
- Suggest cheapest verification when uncertain
"""

from typing import List

from postop import PosTop, PosTopGuardrail, from_dict


def simulate_llm_response(query: str) -> List[str]:
    """Simulate an LLM generating hypotheses."""
    # In practice, this would call an actual LLM
    if "fever" in query and "cough" in query:
        return ["flu", "covid", "pneumonia", "common_cold", "tuberculosis"]
    return ["unknown"]


def main():
    print("=" * 60)
    print("LLM GUARDRAIL WITH POSITIVE TOPOLOGY")
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
        "pneumonia_case_1": ["pneumonia", "fever", "cough", "chest_pain", "infiltrates"],
        "tb_case_1": ["tuberculosis", "fever", "cough", "night_sweats", "weight_loss"],
    }
    
    forcing = from_dict(cases)
    pt = PosTop(forcing)
    guardrail = PosTopGuardrail(pt)
    
    print("\nKnowledge base (disease profiles):")
    for case, profile in cases.items():
        print(f"  {case}: {profile}")
    
    # =========== Scenario 1: Valid diagnosis ===========
    print("\n" + "=" * 60)
    print("SCENARIO 1: Patient with fever, cough, fatigue")
    print("=" * 60)
    
    observed = {"fever", "cough", "fatigue"}
    print(f"\nObserved symptoms: {observed}")
    
    # Simulate LLM response
    llm_hypotheses = simulate_llm_response("fever cough")
    print(f"LLM hypotheses: {llm_hypotheses}")
    
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
    
    observed = {"cough", "runny_nose"}
    print(f"\nObserved symptoms: {observed}")
    
    # Check tuberculosis claim
    check = guardrail.check_claim("tuberculosis", observed)
    print(f"\nClaim: 'tuberculosis'")
    print(f"Status: {check.status}")
    print(f"Explanation: {check.explanation}")
    
    # =========== Scenario 3: Consistency check ===========
    print("\n" + "=" * 60)
    print("SCENARIO 3: Checking consistency of multiple claims")
    print("=" * 60)
    
    # Consistent claims
    claims1 = ["fever", "cough", "fatigue"]
    result1 = guardrail.check_consistency(claims1)
    print(f"\nClaims: {claims1}")
    print(f"Consistent: {result1['consistent']}")
    print(f"Explanation: {result1['explanation']}")
    
    # Inconsistent claims (no single case has both flu and covid)
    claims2 = ["flu", "covid"]
    result2 = guardrail.check_consistency(claims2)
    print(f"\nClaims: {claims2}")
    print(f"Consistent: {result2['consistent']}")
    print(f"Explanation: {result2['explanation']}")
    
    # =========== Scenario 4: Explain reasoning ===========
    print("\n" + "=" * 60)
    print("SCENARIO 4: Explaining why 'flu' is valid")
    print("=" * 60)
    
    observed = {"fever", "cough", "fatigue", "myalgia"}
    print(f"\nObserved: {observed}")
    
    explanation = pt.explain("flu", observed)
    print(f"\nExplanation for 'flu':")
    print(f"  Covers observed: {explanation['covers']}")
    print(f"  Has witness: {explanation['has_witness']}")
    print(f"  Witness: {explanation['witness']}")
    print(f"  Consistent: {explanation['consistent']}")


if __name__ == "__main__":
    main()
