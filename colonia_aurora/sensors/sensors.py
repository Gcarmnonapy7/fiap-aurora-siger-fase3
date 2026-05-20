import math
from colonia_aurora.core.storage import DataStorage
from colonia_aurora.core.manager import GenericManager
from colonia_aurora.sensors.sensor import Sensor


class TemperatureSensor(Sensor):
    def __init__(self):
        super().__init__("temperature", min_val=-140.0, max_val=30.0, variation=2.0, initial=-60.0)


class WindSpeedSensor(Sensor):
    def __init__(self):
        super().__init__("wind_speed", min_val=0.0, max_val=100.0, variation=2.0, initial=12.0)


class SolarIrradianceSensor(Sensor):
    def __init__(self):
        super().__init__("solar_irradiance", min_val=0.0, max_val=590.0, variation=15.0, initial=440.0)


class RainSensor(Sensor):
    def __init__(self):
        super().__init__("rain", min_val=0.0, max_val=1.0, variation=0.05, initial=0.0)


class WindDirectionSensor(Sensor):
    def __init__(self):
        super().__init__("wind_direction", min_val=0.0, max_val=360.0, variation=5.0, initial=180.0)


class DayNightSensor(Sensor):
    def __init__(self):
        super().__init__("day_phase", min_val=0.0, max_val=1.0, variation=0.0, initial=0.0)

    def do(self) -> float:
        tick = DataStorage().get("tick", 0)
        angle = (tick % 48) / 48 * 2 * math.pi
        self.current_val = (math.cos(angle - math.pi) + 1) / 2
        return self.current_val


class DustSensor(Sensor):
    def __init__(self):
        super().__init__("dust", min_val=0.0, max_val=1.0, variation=0.02, initial=0.15)


SENSOR_STORAGE_KEY = {
    "temperature":      "sensor.temperature",
    "wind_speed":       "sensor.wind_speed",
    "solar_irradiance": "sensor.solar_irradiance",
    "day_phase":        "sensor.day_phase",
    "dust":             "sensor.dust",
    "rain":             "sensor.rain",
    "wind_direction":   "sensor.wind_direction",
}


class SensorManager(GenericManager):
    def __init__(self):
        super().__init__()
        for cls in [TemperatureSensor, WindSpeedSensor, SolarIrradianceSensor,
                    RainSensor, WindDirectionSensor, DayNightSensor, DustSensor]:
            self.add(cls())

    def do_all(self):
        storage = DataStorage()
        event = storage.get("event.active")

        for sensor in self._items:
            val = sensor.do()
            key = SENSOR_STORAGE_KEY.get(sensor.name)
            if key:
                storage.set(key, val)

        # Aplica modificadores de evento após leitura base (ajustados para Marte)
        if event == "ColdFront":
            irr = storage.get("sensor.solar_irradiance", 0)
            storage.set("sensor.solar_irradiance", max(0.0, irr * 0.5))
            temp = storage.get("sensor.temperature", -60)
            storage.set("sensor.temperature", max(-140.0, temp - 30))

        elif event == "Sandstorm":
            irr = storage.get("sensor.solar_irradiance", 0)
            storage.set("sensor.solar_irradiance", max(0.0, irr * 0.15))
            wind = storage.get("sensor.wind_speed", 0)
            storage.set("sensor.wind_speed", min(100.0, wind + 40))
            storage.set("sensor.dust", min(1.0, storage.get("sensor.dust", 0.15) + 0.5))
