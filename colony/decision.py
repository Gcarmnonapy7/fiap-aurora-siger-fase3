"""Simple decision rules — covers item 1.2 of the official assignment.

Wraps the rule-based logic ("if energy < 50 → reduce consumption") in the
exact shape requested in the syllabus. Distinct from `allocation.py`,
which runs a richer 4-stage load-shedding policy: this module is the
human-facing, didactic layer.

Inputs are snapshots (plain dicts), so the module has no dependency on
the simulator runtime — it can be evaluated against any data source.
"""

LOW_ENERGY_THRESHOLD_KW = 50.0
HIGH_CONSUMPTION_THRESHOLD_KW = 70.0
STORM_ALERT_LEVELS = ("moderate", "severe")

ACTION_REDUCE = "ALERTA: reduzir consumo"
ACTION_ECONOMY = "ATIVAR MODO ECONOMIA"
ACTION_CLIMATE = "ALERTA CLIMÁTICO: priorizar Vital e Sustento"
ACTION_EMERGENCY = "EMERGÊNCIA ENERGÉTICA"


def evaluate_rules(snapshot):
    """Returns a list of action strings derived from a state snapshot.

    snapshot keys:
        energy_kw       — current/available power (kW)
        consumption_kw  — current demand (kW)
        storm           — one of {"clear", "light", "moderate", "severe"}
    """
    energy = snapshot["energy_kw"]
    consumption = snapshot["consumption_kw"]
    storm = snapshot.get("storm", "clear")

    actions = []
    if energy < LOW_ENERGY_THRESHOLD_KW:
        actions.append(ACTION_REDUCE)
    if energy < LOW_ENERGY_THRESHOLD_KW and consumption > HIGH_CONSUMPTION_THRESHOLD_KW:
        actions.append(ACTION_ECONOMY)
    if consumption > energy:
        actions.append(ACTION_EMERGENCY)
    if storm in STORM_ALERT_LEVELS:
        actions.append(ACTION_CLIMATE)
    return actions


def priority_order():
    """Returns the priority order of system tiers (highest first)."""
    return ["Vital", "Sustenance", "Expansion"]
