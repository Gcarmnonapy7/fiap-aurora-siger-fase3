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

TICK_RATE  = 1.0
SPAWN_PROB = 0.02
SOL_TICKS  = 48


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

    stop_flag   = threading.Event()
    pause_event = threading.Event()
    pause_event.set()  # começa em estado running (setado = não bloqueado)

    def game_loop():
        tick = 0
        try:
            while not stop_flag.is_set():
                pause_event.wait()  # bloqueia enquanto pausado (evento não setado)
                if stop_flag.is_set():
                    break

                tick += 1
                storage.set("tick", tick)
                storage.set("sol",  tick // SOL_TICKS)

                sensor_manager.do_all()
                event_manager.check_and_roll(module_manager, crew_manager, storage)
                energy_manager.calculate(module_manager)
                module_manager.run_all()
                crew_manager.do_all()

                module_snapshot = [
                    {
                        "id": m.id, "name": m.name, "type": m.type,
                        "priority": m.priority, "criticality": m.criticality,
                        "consumption_kw": m.consumption_kw,
                        "active": m.active, "broken": m.broken,
                    }
                    for m in module_manager.all_modules()
                ]
                storage.set("modules.snapshot", module_snapshot)
                storage.set("event.name", event_manager.active_event_name)
                storage.set("event.duration_ticks", event_manager.active_event_ticks)
                storage.set("event.log", event_manager.log)

                logger.log(tick, storage)

                if random.random() < SPAWN_PROB:
                    level = storage.get("energy.level", "NOMINAL")
                    if level in ("CRITICAL", "LOW"):
                        new_mod = module_manager.spawn_generation()
                        tag = "GERAÇÃO FORÇADA"
                    else:
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
        pause_event=pause_event,
    )
    try:
        dash.run()
    finally:
        stop_flag.set()
        pause_event.set()  # garante que o thread não fique bloqueado no wait
        sim_thread.join(timeout=2.0)


if __name__ == "__main__":
    main()
