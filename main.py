"""
Colônia Aurora — SIGER
======================
Entrada: python main.py
"""

import threading

from colonia_aurora.seed import rng
from colonia_aurora.core.storage import DataStorage

rng.set_seed(42)
from colonia_aurora.core.sim_loop import SimulationLoop, THREAD_JOIN_TIMEOUT
from colonia_aurora.sensors.sensors import SensorManager
from colonia_aurora.modules.modules import (
    ModuleManager, CommandModule, LifeSupportModule, HabitatModule, NuclearModule,
)
from colonia_aurora.energy.energy_manager import EnergyManager
from colonia_aurora.events.events import EventManager
from colonia_aurora.crew.crew import CrewMember, CrewManager
from colonia_aurora.logger import Logger
from colonia_aurora.display.dashboard import Dashboard

TICK_RATE  = 0.5
SPAWN_PROB = 0.02
SOL_TICKS  = 24


def main():
    storage        = DataStorage()
    sensor_manager = SensorManager()
    module_manager = ModuleManager()
    event_manager  = EventManager()
    energy_manager = EnergyManager()
    crew_manager   = CrewManager()
    logger         = Logger()

    for ModClass in [CommandModule, LifeSupportModule, HabitatModule, NuclearModule]:
        module_manager.add(ModClass())
    module_manager.mark_spawned(NuclearModule)

    for name, role in [("Ana", "engineer"), ("Bruno", "medic"),
                       ("Carla", "scientist"), ("Diego", "commander")]:
        crew_manager.add(CrewMember(name, role))

    storage.set("config.sol_ticks", SOL_TICKS)

    stop_flag   = threading.Event()
    pause_event = threading.Event()
    pause_event.set()

    sim = SimulationLoop(
        storage=storage,
        sensor_manager=sensor_manager,
        module_manager=module_manager,
        event_manager=event_manager,
        energy_manager=energy_manager,
        crew_manager=crew_manager,
        logger=logger,
        tick_rate=TICK_RATE,
        spawn_prob=SPAWN_PROB,
        sol_ticks=SOL_TICKS,
        stop_flag=stop_flag,
        pause_event=pause_event,
    )
    sim.start()

    dash = Dashboard(
        module_manager=module_manager,
        event_manager=event_manager,
        crew_manager=crew_manager,
        pause_event=pause_event,
        tick_rate=TICK_RATE,
    )
    try:
        dash.run()
    finally:
        stop_flag.set()
        pause_event.set()
        sim.stop(timeout=THREAD_JOIN_TIMEOUT)


if __name__ == "__main__":
    main()
