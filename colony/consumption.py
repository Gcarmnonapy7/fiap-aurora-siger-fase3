"""Module consumption computation.

Combines base consumption (per operating mode) with a thermal term
(Q = U·A·ΔT) for pressurized modules. The thermal term is added even
when the module is 'off', because pressurized habitats cannot be left
to freeze.
"""

from colony.constants import (
    A_ENVELOPE, U_INSULATION, T_TARGET_INTERNAL, INTERNAL_GAIN_W, ETA_HEATER,
)


def heating_consumption_kw(external_temperature, thermal_factor):
    """Electric power spent on heating (kW).

    thermal_factor acts as the module's "relative size": it scales both
    the envelope loss (smaller area → less loss) and the internal gain
    (fewer people/equipment → less free heat).

    Q_loss   = U * A_envelope * ΔT * thermal_factor
    Q_gain   = INTERNAL_GAIN_W * thermal_factor
    Q_net    = max(0, Q_loss - Q_gain)
    Q_elec   = Q_net / eta_heater

    Modules with thermal_factor == 0 naturally yield 0 because every term
    in the numerator is scaled by it — no special-casing needed.
    """
    delta_t = max(0, T_TARGET_INTERNAL - external_temperature)
    loss_W = U_INSULATION * A_ENVELOPE * delta_t * thermal_factor
    net_W = max(0, loss_W - INTERNAL_GAIN_W * thermal_factor)
    return net_W / ETA_HEATER / 1000.0


def current_consumption_kw(module, climate):
    """Total consumption of the module right now (kW)."""
    base = module["consumption_by_mode"][module["current_mode"]]
    thermal = heating_consumption_kw(climate["temperature_c"], module["thermal_factor"])
    return base + thermal
