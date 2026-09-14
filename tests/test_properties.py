"""
Lightweight property checks over random finite incidence tables.

Deliberately dependency-free (plain `random`, stdlib only) rather than
adding Hypothesis: this repo keeps runtime/test dependencies minimal, and
a small number of seeded random trials is enough to catch adjunction-law
regressions cheaply. If heavier property-based testing is wanted later,
add `hypothesis` to the `dev` extra only -- never to core dependencies.
"""

import random

from postop import IncidenceSystem, from_dict

POINTS = [f"x{i}" for i in range(6)]
OBSERVABLES = [f"a{i}" for i in range(5)]


def _random_system(rng: random.Random) -> IncidenceSystem[str, str]:
    data = {}
    for x in POINTS:
        profile = {a for a in OBSERVABLES if rng.random() < 0.4}
        if profile:
            data[x] = list(profile)
    return IncidenceSystem(from_dict(data))


def _random_subset(rng: random.Random, universe):
    universe = list(universe)
    return {a for a in universe if rng.random() < 0.5}


def test_ext_box_adjunction_holds_on_random_systems() -> None:
    rng = random.Random(1234)
    for _ in range(30):
        system = _random_system(rng)
        # Sample from the system's own known domain: a point or observable
        # never registered with the forcing relation is outside X/S for
        # this instance (box/rest/saturation/reduction all iterate over
        # forcing.points / forcing.observables), so testing against it
        # would compare against a "phantom" element outside the model.
        U = _random_subset(rng, system.forcing.observables)
        E = _random_subset(rng, system.forcing.points)
        # ext(U) ⊆ E  <=>  U ⊆ box(E)
        assert (system.ext(U) <= E) == (U <= system.box(E))


def test_diamond_rest_adjunction_holds_on_random_systems() -> None:
    rng = random.Random(5678)
    for _ in range(30):
        system = _random_system(rng)
        D = _random_subset(rng, system.forcing.points)
        U = _random_subset(rng, system.forcing.observables)
        # diamond(D) ⊆ U  <=>  D ⊆ rest(U)
        assert (system.diamond(D) <= U) == (D <= system.rest(U))


def test_reduction_contractive_monotone_idempotent_on_random_systems() -> None:
    rng = random.Random(2468)
    for _ in range(30):
        system = _random_system(rng)
        U = _random_subset(rng, system.forcing.observables)
        V = U | _random_subset(rng, system.forcing.observables)  # V ⊇ U

        reduced_U = system.reduction(U)
        assert reduced_U <= U  # contractive
        assert system.reduction(reduced_U) == reduced_U  # idempotent
        assert system.reduction(U) <= system.reduction(V)  # monotone


def test_saturation_extensive_monotone_idempotent_on_random_systems() -> None:
    rng = random.Random(1357)
    for _ in range(30):
        system = _random_system(rng)
        U = _random_subset(rng, system.forcing.observables)
        V = U | _random_subset(rng, system.forcing.observables)

        saturated_U = system.saturation(U)
        assert U <= saturated_U  # extensive
        assert system.saturation(saturated_U) == saturated_U  # idempotent
        assert system.saturation(U) <= system.saturation(V)  # monotone


def test_compatibility_axiom_holds_on_random_systems() -> None:
    rng = random.Random(9876)
    trials = 0
    for _ in range(60):
        system = _random_system(rng)
        if not system.forcing.observables:
            continue
        a = rng.choice(sorted(system.forcing.observables))
        U = _random_subset(rng, system.forcing.observables) | {a}
        V = _random_subset(rng, system.forcing.observables)
        if not (system.covers(a, U) and system.positive(a, V)):
            continue
        trials += 1
        cert = system.compatibility_certificate(a, U, V)
        assert cert.holds is True
        assert cert.surviving_refinement in U
        assert system.positive(cert.surviving_refinement, V)
    assert trials > 0  # sanity: the preconditions were exercised at least once
