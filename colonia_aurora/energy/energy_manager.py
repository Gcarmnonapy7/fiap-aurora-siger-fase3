from colonia_aurora.core.storage import DataStorage
from colonia_aurora.energy.regression import LinearRegression

SOLAR_EFFICIENCY = 0.22
BATTERY_MAX      = 1000.0
WIND_CUT_IN      = 5.0
WIND_FURL        = 50.0
WIND_CUTOUT      = 100.0
HISTORY_WINDOW   = 48
SLOPE_CRITICAL   = -2.0
SLOPE_LOW        = -0.5


def _wind_curve(wind: float, wind_k: float) -> float:
    if wind < WIND_CUT_IN:
        return 0.0
    elif wind < WIND_FURL:
        return wind_k * wind ** 3
    elif wind < WIND_CUTOUT:
        return wind_k * WIND_FURL ** 3 * 0.3
    return 0.0


class EnergyManager:
    def __init__(self):
        self._regression = LinearRegression()

    def _calculate_generation(self, storage: DataStorage, module_manager) -> tuple:
        # Import local para evitar circular (energy → modules → energy)
        from colonia_aurora.modules.modules import SolarModule, NuclearModule, WindModule

        phase = storage.get("sensor.day_phase", 0)
        irrad = storage.get("sensor.solar_irradiance", 0)
        wind  = storage.get("sensor.wind_speed", 0)
        level = storage.get("energy.level", "NOMINAL")

        solar_gen = nuclear_gen = wind_gen = 0.0

        for mod in module_manager._heap:
            if not mod.active or mod.broken:
                continue
            if isinstance(mod, SolarModule):
                solar_gen += mod.solar_area * irrad * SOLAR_EFFICIENCY * phase / 1000
            elif isinstance(mod, NuclearModule):
                # Em SURPLUS, reduz 20% para evitar desperdício
                factor = 0.8 if level == "SURPLUS" else 1.0
                nuclear_gen += mod.rated_kw * factor
            elif isinstance(mod, WindModule):
                wind_gen += _wind_curve(wind, mod.wind_k)

        return (
            round(solar_gen + wind_gen + nuclear_gen, 2),
            round(solar_gen, 2),
            round(wind_gen, 2),
            round(nuclear_gen, 2),
        )

    def _calculate_consumption(self, module_manager) -> float:
        total = sum(
            mod.consumption_kw
            for mod in module_manager._heap
            if mod.active and not mod.broken
        )
        return round(total, 2)

    def _determine_level(self, battery_pct: float, predicted_delta: float, slope: float) -> str:
        if battery_pct < 20:
            base = "CRITICAL"
        elif battery_pct < 40:
            base = "LOW"
        elif battery_pct > 90:
            base = "SURPLUS"
        elif predicted_delta > 0:
            base = "HIGH"
        else:
            base = "NOMINAL"

        if slope <= SLOPE_CRITICAL:
            if base in ("NOMINAL", "HIGH", "SURPLUS"):
                return "LOW"
            if base == "LOW":
                return "CRITICAL"
        elif slope <= SLOPE_LOW:
            if base in ("HIGH", "SURPLUS"):
                return "NOMINAL"
            if base == "NOMINAL":
                return "LOW"

        return base

    def _generate_alert(self, level: str, generated: float, consumed: float, slope: float) -> str:
        if level == "CRITICAL":
            return f"ALERTA: consumo maior que geração (slope={slope:+.2f} kW/tick)"
        elif level == "LOW":
            return "ALERTA: reduzir consumo — tendência negativa detectada"
        elif level == "SURPLUS":
            return "SUGESTÃO: armazenar energia excedente"
        elif generated > consumed:
            return f"Geração: {generated:.1f} kW  Consumo: {consumed:.1f} kW  Saldo: {generated-consumed:+.1f} kW"
        return "Operação nominal"

    def calculate(self, module_manager):
        storage = DataStorage()

        generated, solar_gen, wind_gen, nuclear_gen = self._calculate_generation(storage, module_manager)
        consumed  = self._calculate_consumption(module_manager)
        delta     = round(generated - consumed, 2)

        battery_kwh = storage.get("energy.battery_kwh", BATTERY_MAX * 0.65)
        battery_kwh = max(0.0, min(BATTERY_MAX, battery_kwh + delta))
        battery_pct = round((battery_kwh / BATTERY_MAX) * 100, 2)

        delta_history = storage.history("energy.delta", last_n=HISTORY_WINDOW)

        xs = list(range(len(delta_history)))
        ys = delta_history
        self._regression.fit(xs, ys)

        predicted_delta = round(self._regression.predict(len(xs)), 2)
        slope           = round(self._regression.slope, 4)

        level = self._determine_level(battery_pct, predicted_delta, slope)
        alert = self._generate_alert(level, generated, consumed, slope)

        storage.set("energy.battery_kwh",     battery_kwh)
        storage.set("energy.battery",         battery_pct)
        storage.set("energy.generated",       generated)
        storage.set("energy.solar_gen",       solar_gen)
        storage.set("energy.wind_gen",        wind_gen)
        storage.set("energy.nuclear_gen",     nuclear_gen)
        storage.set("energy.consumed",        consumed)
        storage.set("energy.delta",           delta)
        storage.set("energy.predicted_delta", predicted_delta)
        storage.set("energy.slope",           slope)
        storage.set("energy.level",           level)
        storage.set("energy.alert",           alert)
