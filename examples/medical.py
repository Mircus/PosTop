"""
Example: Medical Diagnosis with Positive Topology

This example shows how to use PosTop for medical diagnosis:
- Patients are points
- Symptoms/conditions are observables  
- Forcing = patient has symptom
- Covers = disease implies symptoms
- Positivity = symptom cluster is realizable
"""

from postop import PosTop, from_dict


def main():
    # =========== Define the forcing relation ===========
    # Each patient has a symptom profile
    
    patients = {
        "alice": ["fever", "cough", "fatigue"],
        "bob": ["fever", "headache", "fatigue", "myalgia"],
        "carol": ["cough", "runny_nose", "sneezing"],
        "dave": ["fever", "cough", "chest_pain", "infiltrates"],
        "eve": ["fever", "elevated_WBC", "fatigue"],
    }
    
    forcing = from_dict(patients)
    pt = PosTop(forcing)
    
    print("=" * 60)
    print("MEDICAL DIAGNOSIS WITH POSITIVE TOPOLOGY")
    print("=" * 60)
    
    print("\nPatients and their symptoms:")
    for name, symptoms in patients.items():
        print(f"  {name}: {symptoms}")
    
    # =========== Test Extension ===========
    print("\n--- Extension (Ext) ---")
    fever_patients = pt.Ext({"fever"})
    print(f"Patients with fever: {fever_patients}")
    
    cough_patients = pt.Ext({"cough"})
    print(f"Patients with cough: {cough_patients}")
    
    # =========== Test Covers ===========
    print("\n--- Cover Relation (◁) ---")
    
    # Does "fever" cover {"fever", "cough"}? 
    # i.e., does every fever patient have fever or cough?
    result = pt.covers("fever", {"fever", "cough"})
    print(f"fever ◁ {{fever, cough}}: {result}")  # True (trivially, fever ∈ set)
    
    # Check if having infiltrates implies having fever or cough
    result = pt.covers("infiltrates", {"fever", "cough"})
    print(f"infiltrates ◁ {{fever, cough}}: {result}")  # True (Dave has both)
    
    # =========== Test Positivity ===========
    print("\n--- Positivity Relation (⋉) ---")
    
    # Is there a patient with fever whose profile is ⊆ {fever, cough, fatigue}?
    profile = {"fever", "cough", "fatigue"}
    result = pt.positive("fever", profile)
    witness = pt.find_witness("fever", profile)
    print(f"fever ⋉ {profile}: {result}")
    print(f"  Witness: {witness}")  # Alice
    
    # Is there a patient with fever whose profile is ⊆ {fever, headache}?
    profile2 = {"fever", "headache"}
    result2 = pt.positive("fever", profile2)
    witness2 = pt.find_witness("fever", profile2)
    print(f"fever ⋉ {profile2}: {result2}")
    print(f"  Witness: {witness2}")  # None - Bob has more symptoms
    
    # Contradiction check: fever ⋉ {hypothermia}?
    result3 = pt.positive("fever", {"hypothermia"})
    print(f"fever ⋉ {{hypothermia}}: {result3}")  # False - no witness
    
    # =========== Formal Closeds ===========
    print("\n--- Formal Closeds (J-stable sets) ---")
    
    # Alice's profile is a formal closed (complete symptom cluster)
    alice_profile = {"fever", "cough", "fatigue"}
    j_alice = pt.J(alice_profile)
    print(f"J({alice_profile}) = {j_alice}")
    print(f"Is formal closed: {j_alice == alice_profile}")
    
    # =========== Compatibility Axiom ===========
    print("\n--- Compatibility Axiom ---")
    
    # If infiltrates ◁ {fever, cough, infiltrates} and infiltrates ⋉ V,
    # then some u ∈ {fever, cough, infiltrates} also has u ⋉ V
    U = {"fever", "cough", "infiltrates"}
    V = {"fever", "cough", "chest_pain", "infiltrates"}  # Dave's profile
    
    print(f"U = {U}")
    print(f"V = {V}")
    print(f"infiltrates ◁ U: {pt.covers('infiltrates', U)}")
    print(f"infiltrates ⋉ V: {pt.positive('infiltrates', V)}")
    
    u = pt.check_compatibility("infiltrates", U, V)
    print(f"Compatibility witness u ∈ U with u ⋉ V: {u}")
    
    # =========== Diagnosis ===========
    print("\n--- Diagnosis: Consistent Hypotheses ---")
    
    observed = {"fever", "cough"}
    print(f"Observed symptoms: {observed}")
    
    consistent = pt.consistent_hypotheses(observed)
    print(f"Consistent hypotheses: {consistent}")
    
    # Explain each
    for hyp in ["fever", "cough", "infiltrates", "headache"]:
        explanation = pt.explain(hyp, observed)
        print(f"\n  {hyp}:")
        print(f"    Covers observed: {explanation['covers']}")
        print(f"    Has witness: {explanation['has_witness']}")
        print(f"    Consistent: {explanation['consistent']}")
        if explanation['witness']:
            print(f"    Witness: {explanation['witness']}")


if __name__ == "__main__":
    main()
