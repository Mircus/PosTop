"""
Tests for the resource-bounded layer (postop.costs).

The key regression coverage here is item 14 from the repo refresh: budget-
gated *forcing* is monotone, but the *induced* cover and positivity are
NOT guaranteed monotone in the budget (survey §9.2). Each fixture below
is deliberately minimal and uses its own generator/point names so the
three phenomena (cover flips true->false, positivity gains a witness,
positivity loses its only witness) don't interact.
"""

from postop import CostAnnotatedIncidence, CostForcing, CostPosTop, LawvereDomain


def build_fixture() -> CostAnnotatedIncidence[str, str, float]:
    cai: CostAnnotatedIncidence[str, str, float] = CostAnnotatedIncidence()

    # Fixture A: cover({"b"}) is true at low budget, false at high budget --
    # a second point that also forces "a" (but not "b") only becomes
    # affordable at the higher budget, breaking the universal claim.
    cai.assert_true("p1", "a", cost=5)
    cai.assert_true("p1", "b", cost=5)
    cai.assert_true("p2", "a", cost=50)

    # Fixture B: positive("c", {"c"}) is false at low budget (no witness
    # affordable yet), true at high budget (the witness becomes affordable).
    cai.assert_true("q1", "c", cost=50)

    # Fixture C: positive("e", {"e"}) is true at low budget (r1 confined to
    # {e}), false at high budget (a second, expensive-to-verify observable
    # of r1's becomes affordable, breaking confinement -- and there is no
    # other point to serve as an alternate witness).
    cai.assert_true("r1", "e", cost=5)
    cai.assert_true("r1", "f", cost=60)

    return cai


def test_forcing_is_monotone_in_budget() -> None:
    cai = build_fixture()
    # Anything forced within a smaller budget stays forced within a larger one.
    checks = [
        ("p1", "a"),
        ("p1", "b"),
        ("p2", "a"),
        ("q1", "c"),
        ("r1", "e"),
        ("r1", "f"),
    ]
    budgets = [1, 5, 10, 50, 60, 100]
    for x, a in checks:
        affordable_at = [b for b in budgets if cai.forces_within(x, a, b)]
        if not affordable_at:
            continue
        threshold = min(affordable_at)
        for b in budgets:
            expected = b >= threshold
            assert cai.forces_within(x, a, b) == expected


def test_cover_non_monotonicity_true_then_false() -> None:
    cai = build_fixture()

    system_10 = cai.to_incidence_system_within(10)
    system_50 = cai.to_incidence_system_within(50)

    assert system_10.covers("a", {"b"}) is True
    assert system_50.covers("a", {"b"}) is False  # p2 appears, breaks the universal claim


def test_positivity_non_monotonicity_gains_witness() -> None:
    cai = build_fixture()

    system_10 = cai.to_incidence_system_within(10)
    system_50 = cai.to_incidence_system_within(50)

    assert system_10.positive("c", {"c"}) is False  # q1 not yet affordable
    assert system_50.positive("c", {"c"}) is True  # q1 becomes affordable and qualifies


def test_positivity_non_monotonicity_loses_witness() -> None:
    cai = build_fixture()

    system_10 = cai.to_incidence_system_within(10)
    system_60 = cai.to_incidence_system_within(60)

    assert system_10.positive("e", {"e"}) is True  # r1 confined to {e} so far
    assert system_60.positive("e", {"e"}) is False  # r1's "f" becomes visible, breaks confinement


def test_budget_certificate_carries_provenance() -> None:
    cai = build_fixture()
    cert = cai.budget_certificate("a", {"b"}, 50, kind="cover")

    assert cert.verdict is False
    assert cert.budget == 50
    assert ("p2", "a") in cert.affordable_observations
    assert cert.assumptions  # non-empty: explicitly disclaims monotonicity

    payload = cert.to_dict()
    assert payload["verdict"] is False
    assert isinstance(payload["affordable_observations"], list)


def test_ground_truth_and_cost_are_decoupled() -> None:
    # forces() is ground truth, independent of any budget; an unset cost
    # means "true but unverified", not "false" -- unlike the legacy
    # CostForcing default-cost-as-infinity behavior tested below.
    cai: CostAnnotatedIncidence[str, str, float] = CostAnnotatedIncidence()
    cai.assert_true("x", "a")  # no cost recorded
    assert cai.forces("x", "a") is True
    assert cai.verification_cost("x", "a") is None
    assert cai.forces_within("x", "a", budget=1_000_000) is False  # cost unknown, never affordable


# ---- Legacy CostForcing / CostPosTop smoke tests (previously untested) ----


def test_legacy_cost_forcing_slices_by_budget() -> None:
    cf: CostForcing[str, str] = CostForcing(domain=LawvereDomain())
    cf.set_cost("alice", "fever", 0)
    cf.set_cost("alice", "cough", 0)
    cf.set_cost("alice", "elevated_wbc", 50)

    low = cf.to_boolean_forcing(budget=10)
    high = cf.to_boolean_forcing(budget=50)

    assert low.neighborhood("alice") == {"fever", "cough"}
    assert high.neighborhood("alice") == {"fever", "cough", "elevated_wbc"}


def test_legacy_cost_postop_covers_and_positive_at_budget() -> None:
    cf: CostForcing[str, str] = CostForcing(domain=LawvereDomain())
    cf.set_cost("alice", "fever", 0)
    cf.set_cost("alice", "cough", 0)
    cf.set_cost("bob", "fever", 0)
    cf.set_cost("bob", "elevated_wbc", 50)

    cp = CostPosTop(cf)

    # bob forces fever but never cough, so "fever" does not universally
    # imply "cough" across the population at this budget.
    assert cp.covers_at("fever", {"cough"}, budget=0) is False
    # alice's whole profile at this budget is confined to {fever, cough}.
    assert cp.positive_at("fever", {"fever", "cough"}, budget=0) is True


def test_suggest_next_test_returns_certificate() -> None:
    cf: CostForcing[str, str] = CostForcing(domain=LawvereDomain())
    cf.set_cost("flu_case", "fever", 0)
    cf.set_cost("flu_case", "cough", 0)
    cf.set_cost("cold_case", "cough", 0)
    cf.set_cost("cold_case", "runny_nose", 0)

    cp = CostPosTop(cf)
    suggestion = cp.suggest_next_test(["fever", "runny_nose"], observed={"cough"}, budget=100)

    assert suggestion.reason_code in {"cheapest_discriminator_found", "no_discriminator_within_budget"}
    payload = suggestion.to_dict()
    assert "discriminates" in payload
