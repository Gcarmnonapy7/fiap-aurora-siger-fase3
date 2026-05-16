"""Flat list of the 13 colony modules.

The first 12 keep the identity from Fase 2 (same names and priorities).
The 13th — Wind Power — is added in Fase 3 to support item 1.3 of the
official assignment, which requires linear regression on wind and wind energy.
"""

MODULES = [
    {
        "id": 1, "name": "Command and Control", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 2, "adequate": 8, "surplus": 8},
        "scales_with_surplus": False,
        "thermal_factor": 0.0,
        "current_mode": "adequate",
    },
    {
        "id": 2, "name": "Life Support (ECLSS)", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 4, "adequate": 12, "surplus": 12},
        "scales_with_surplus": False,
        "thermal_factor": 0.4,
        "current_mode": "adequate",
    },
    {
        "id": 3, "name": "Habitat", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 5, "adequate": 15, "surplus": 15},
        "scales_with_surplus": False,
        "thermal_factor": 1.0,
        "current_mode": "adequate",
    },
    {
        "id": 4, "name": "Solar Power", "type": "solar_generator",
        "max_capacity_kw": 100.0,
        "consumption_by_mode": {"off": 0, "minimum": 0.5, "adequate": 1, "surplus": 1},
        "scales_with_surplus": False,
        "thermal_factor": 0.0,
        "current_mode": "adequate",
    },
    {
        "id": 5, "name": "Nuclear Power", "type": "nuclear_generator",
        "max_capacity_kw": 80.0,
        "consumption_by_mode": {"off": 0, "minimum": 2, "adequate": 3, "surplus": 3},
        "scales_with_surplus": False,
        "thermal_factor": 0.0,
        "current_mode": "adequate",
    },
    {
        "id": 6, "name": "Communications", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 1, "adequate": 5, "surplus": 5},
        "scales_with_surplus": False,
        "thermal_factor": 0.0,
        "current_mode": "adequate",
    },
    {
        "id": 7, "name": "Medical Support", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 2, "adequate": 6, "surplus": 6},
        "scales_with_surplus": False,
        "thermal_factor": 0.2,
        "current_mode": "adequate",
    },
    {
        "id": 8, "name": "Food Production", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 3, "adequate": 10, "surplus": 18},
        "scales_with_surplus": True,
        "thermal_factor": 0.0,
        "current_mode": "adequate",
    },
    {
        "id": 9, "name": "Logistics and Storage", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 1, "adequate": 4, "surplus": 4},
        "scales_with_surplus": False,
        "thermal_factor": 0.0,
        "current_mode": "adequate",
    },
    {
        "id": 10, "name": "ISRU (Local Resources)", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 2, "adequate": 8, "surplus": 20},
        "scales_with_surplus": True,
        "thermal_factor": 0.0,
        "current_mode": "adequate",
    },
    {
        "id": 11, "name": "Workshop and Maintenance", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 0.5, "adequate": 3, "surplus": 3},
        "scales_with_surplus": False,
        "thermal_factor": 0.2,
        "current_mode": "off",
    },
    {
        "id": 12, "name": "Science Lab", "type": "consumer",
        "consumption_by_mode": {"off": 0, "minimum": 1, "adequate": 5, "surplus": 12},
        "scales_with_surplus": True,
        "thermal_factor": 0.2,
        "current_mode": "adequate",
    },
    {
        "id": 13, "name": "Wind Power", "type": "wind_generator",
        "max_capacity_kw": 30.0,
        "consumption_by_mode": {"off": 0, "minimum": 0.3, "adequate": 0.5, "surplus": 0.5},
        "scales_with_surplus": False,
        "thermal_factor": 0.0,
        "current_mode": "adequate",
    },
]


def find_module(id_):
    """Returns the module with the given id. Raises KeyError if not found."""
    for m in MODULES:
        if m["id"] == id_:
            return m
    raise KeyError(f"Module with id={id_} not found")
