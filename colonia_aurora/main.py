import random
import time
import threading

from colonia_aurora.core.storage import DataStorage
from colonia_aurora.sensors.sensors import SensorManager
from colonia_aurora.modules.modules import (
    ModuleManager, CommandModule, LifeSupportModule, HabitatModule,
    SolarModule, NuclearModule, WindModule, CommsModule, MedicalModule,
    FoodModule, LogisticsModule, ISRUModule, WorkshopModule, LabModule,
    SensorsModule,
)
from colonia_aurora.energy.energy_manager import EnergyManager
from colonia_aurora.events.events import EventManager
from colonia_aurora.crew.crew import CrewMember, CrewManager
from colonia_aurora.logger import Logger

TICK_RATE  = 0.5
SPAWN_PROB = 0.02
SOL_TICKS  = 24

_stop_event = threading.Event()


def game_loop():
    storage        = DataStorage()
    sensor_manager = SensorManager()
    module_manager = ModuleManager()
    event_manager  = EventManager()
    energy_manager = EnergyManager()
    crew_manager   = CrewManager()
    logger         = Logger()

    for ModClass in [CommandModule, LifeSupportModule, HabitatModule,
                     SolarModule, NuclearModule, WindModule]:
        module_manager.add(ModClass())

    for name, role in [("Ana", "engineer"), ("Bruno", "medic"),
                       ("Carla", "scientist"), ("Diego", "commander")]:
        crew_manager.add(CrewMember(name, role))

    tick = 0
    try:
        while not _stop_event.is_set():
            tick += 1
            storage.set("tick", tick)
            storage.set("sol",  tick // SOL_TICKS)

            sensor_manager.do_all()
            event_manager.check_and_roll(module_manager, crew_manager, storage)
            energy_manager.calculate(module_manager)
            module_manager.run_all()
            crew_manager.do_all()
            logger.log(tick, storage)

            # Spawn aleatório de módulo + tripulante
            if random.random() < SPAWN_PROB:
                available = [CommsModule, MedicalModule, FoodModule, LogisticsModule,
                             ISRUModule, WorkshopModule, LabModule, SensorsModule]
                new_mod = module_manager.spawn_random(available)
                if new_mod:
                    crew_manager.add(
                        CrewMember(f"Tripulante_{tick}", random.choice(CrewMember.ROLES))
                    )

            _stop_event.wait(TICK_RATE)
    finally:
        logger.close()


def start_simulation():
    t = threading.Thread(target=game_loop, daemon=True, name="SimLoop")
    t.start()
    return t


def stop_simulation():
    _stop_event.set()
