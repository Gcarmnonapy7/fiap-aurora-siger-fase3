import csv
import os
from colonia_aurora.core.storage import DataStorage

LOG_FILE = "simulation_log.csv"

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
        self._file_ready = False
        self._init_csv()

    def _init_csv(self):
        write_header = not os.path.exists(LOG_FILE)
        self._f = open(LOG_FILE, "a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._f, fieldnames=COLUMNS, extrasaction="ignore")
        if write_header:
            self._writer.writeheader()
        self._file_ready = True

    def log(self, tick: int, storage: DataStorage):
        snap = storage.snapshot()
        snap["tick"] = tick
        snap["sol"]  = storage.get("sol", 0)

        # Console
        level = snap.get("energy.level", "?")
        bat   = snap.get("energy.battery", 0)
        gen   = snap.get("energy.generated", 0)
        con   = snap.get("energy.consumed", 0)
        alert = snap.get("energy.alert", "")

        if "ALERTA" in alert:
            prefix = "⚠ "
        elif "SUGESTÃO" in alert:
            prefix = "✓ "
        else:
            prefix = "  "

        print(
            f"[T{tick:05d} Sol{snap.get('sol',0):02d}] "
            f"Bat:{bat:5.1f}%  Gen:{gen:6.1f}kW  Con:{con:6.1f}kW  "
            f"Nível:{level:<8}  {prefix}{alert}"
        )

        # CSV
        if self._file_ready:
            self._writer.writerow(snap)
            self._f.flush()

    def log_event(self, message: str):
        print(f"  *** {message}")

    def close(self):
        if self._file_ready:
            self._f.close()
