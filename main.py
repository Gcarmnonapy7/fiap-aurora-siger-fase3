"""
Colônia Aurora — SIGER
======================
Entrada: python main.py
"""

import random
import threading

from colonia_aurora.core.storage import DataStorage
from colonia_aurora.sensors.sensors import SensorManager
from colonia_aurora.modules.modules import (
    ModuleManager, CommandModule, LifeSupportModule, HabitatModule,
    SolarModule, NuclearModule, WindModule,
    SPAWNABLE_GENERATION, SPAWNABLE_CONSUMPTION,
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

    for ModClass in [CommandModule, LifeSupportModule, HabitatModule,
                     SolarModule, NuclearModule, WindModule]:
        module_manager.add(ModClass())

    for name, role in [("Ana", "engineer"), ("Bruno", "medic"),
                       ("Carla", "scientist"), ("Diego", "commander")]:
        crew_manager.add(CrewMember(name, role))

    stop_flag = threading.Event()

    def game_loop():
        tick = 0
        try:
            while not stop_flag.is_set():
                tick += 1
                storage.set("tick", tick)
                storage.set("sol",  tick // SOL_TICKS)

                sensor_manager.do_all()
                event_manager.check_and_roll(module_manager, crew_manager, storage)
                energy_manager.calculate(module_manager)
                module_manager.run_all()
                crew_manager.do_all()
                logger.log(tick, storage)

                if random.random() < SPAWN_PROB:
                    level = storage.get("energy.level", "NOMINAL")
                    if level in ("CRITICAL", "LOW"):
                        # Energia insuficiente — força instalação de módulo de geração
                        new_mod = module_manager.spawn_generation()
                        tag = "GERAÇÃO FORÇADA"
                    else:
                        # Operação normal — qualquer tipo pode chegar
                        new_mod = module_manager.spawn_random(
                            SPAWNABLE_CONSUMPTION + SPAWNABLE_GENERATION
                        )
                        tag = "aleatório"
                    if new_mod:
                        logger.log_event(f"[Spawn {tag}] {new_mod.name}")
                        crew_manager.add(
                            CrewMember(f"Tripulante_{tick}", random.choice(CrewMember.ROLES))
                        )

                stop_flag.wait(TICK_RATE)
        finally:
            logger.close()

    sim_thread = threading.Thread(target=game_loop, daemon=True, name="SimLoop")
    sim_thread.start()

    dash = Dashboard(
        module_manager=module_manager,
        event_manager=event_manager,
        crew_manager=crew_manager,
    )
    try:
        dash.run()
    finally:
        stop_flag.set()
        sim_thread.join(timeout=2.0)


if __name__ == "__main__":
    main()
