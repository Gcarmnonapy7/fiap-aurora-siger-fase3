"""Energy allocation policy (4-stage load shedding).

Walks the criticality tree and sets each module's current_mode based on
available supply. Generators stay 'adequate' (own consumption is small,
generation is physics-defined, not policy-driven).

Stage 1: try everyone at 'adequate'; if it fits, distribute surplus.
Stage 2: downgrade Expansion → Sustenance → Vital to 'minimum', bottom-up.
Stage 3: shut Expansion → Sustenance off (Vital never).
Stage 4: emergency — critical alert (battery reserve handled outside
this function, in state.py / simulator.py).
"""

from colony.constants import CRITICALITY_LEVELS, GENERATOR_TYPES
from colony.consumption import heating_consumption_kw


def _consumption_at_mode(module, mode, climate):
    """Consumption of the module IF it were in `mode` (does not mutate)."""
    base = module["consumption_by_mode"][mode]
    extra = heating_consumption_kw(climate["temperature_c"], module["thermal_factor"])
    return base + extra


def _leaves_by_level(tree):
    """Returns (consumers_by_level, generators)."""
    levels = {}
    generators = []
    for level_child in tree.children:
        consumers = []
        for m in level_child.leaves():
            (generators if m["type"] in GENERATOR_TYPES else consumers).append(m)
        # sort by id (smaller = higher priority) for consistent tie-breaking
        consumers.sort(key=lambda m: m["id"])
        levels[level_child.name] = consumers
    return levels, generators


def allocate_energy(criticality_tree, supply_kw, climate):
    """Applies the 4-stage policy. Mutates module['current_mode'] in place.

    Generators are not downgraded by the policy (mode fixed at 'adequate'),
    but their own consumption IS included in the cost — otherwise the
    policy would under-estimate demand and silently violate supply.
    """
    levels, generators = _leaves_by_level(criticality_tree)
    everyone = [m for level in CRITICALITY_LEVELS for m in levels[level]]

    # Stage 1: everyone at 'adequate'
    for m in everyone:
        m["current_mode"] = "adequate"
    consumer_cost = sum(_consumption_at_mode(m, "adequate", climate) for m in everyone)
    generator_fixed_cost = sum(_consumption_at_mode(m, "adequate", climate) for m in generators)
    cost = consumer_cost + generator_fixed_cost

    if cost <= supply_kw:
        # distribute surplus to scalable consumers (smaller id first)
        remaining = supply_kw - cost
        for m in sorted([x for x in everyone if x["scales_with_surplus"]], key=lambda x: x["id"]):
            delta = _consumption_at_mode(m, "surplus", climate) - _consumption_at_mode(m, "adequate", climate)
            if remaining >= delta:
                m["current_mode"] = "surplus"
                remaining -= delta
        return

    # Stage 2: downgrade bottom-up across every level (Vital included as last resort).
    for level_name in reversed(CRITICALITY_LEVELS):
        for m in reversed(levels[level_name]):  # lowest priority first = highest id first
            if cost <= supply_kw:
                return
            before = _consumption_at_mode(m, m["current_mode"], climate)
            m["current_mode"] = "minimum"
            after = _consumption_at_mode(m, "minimum", climate)
            cost -= (before - after)

    if cost <= supply_kw:
        return

    # Stage 3: shut off bottom-up across every level except Vital.
    for level_name in reversed(CRITICALITY_LEVELS[1:]):
        for m in reversed(levels[level_name]):
            if cost <= supply_kw:
                return
            before = _consumption_at_mode(m, m["current_mode"], climate)
            m["current_mode"] = "off"
            after = _consumption_at_mode(m, "off", climate)
            cost -= (before - after)

    # Stage 4: emergency — Vital stays in 'minimum' even with negative balance.
    # Alert is emitted by the simulator comparing total consumption vs supply
    # after this call returns.
