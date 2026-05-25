import csv
import os
from datetime import datetime
from colonia_aurora.core.storage import DataStorage

COLUMNS = [
    "tick", "sol", "sensor.temperature", "sensor.wind_speed",
    "sensor.solar_irradiance", "sensor.day_phase", "sensor.dust",
    "energy.generated", "energy.solar_gen", "energy.wind_gen", "energy.nuclear_gen",
    "energy.consumed", "energy.delta", "energy.battery",
    "energy.predicted_delta", "energy.slope", "energy.level",
    "event.active", "energy.alert",
]


class Logger:
    def __init__(self):
        os.makedirs("logs", exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = os.path.join("logs", f"{ts}.csv")
        self._f      = open(log_path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._f, fieldnames=COLUMNS, extrasaction="ignore")
        self._writer.writeheader()

    def log(self, tick: int, storage: DataStorage):
        snap = storage.snapshot()
        snap["tick"] = tick
        snap["sol"]  = storage.get("sol", 0)

        # CSV
        self._writer.writerow(snap)
        self._f.flush()

    def log_event(self, message: str):
        pass

    def close(self):
        self._f.close()
