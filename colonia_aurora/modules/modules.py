import heapq
import random
from colonia_aurora.core.storage import DataStorage
from colonia_aurora.core.manager import GenericManager
from colonia_aurora.modules.module import Module


# ─── Módulos de geração ───────────────────────────────────────────────────────
# Cada instância carrega sua própria capacidade — múltiplas instâncias somam.

class SolarModule(Module):
    def __init__(self, solar_area: float = 200.0, instance_num: int = 1, _id: int = None):
        name = "Solar" if instance_num == 1 else f"Solar-{instance_num}"
        super().__init__(id=_id or 4, name=name, type="solar", priority=4,
                         consumption_kw=2.0, criticality=5)
        self.solar_area = solar_area  # m² — escala a geração solar

    def energy_logic(self, level: str):
        self.active = True
        self.consumption_kw = 2.0
        return self.consumption_kw


class NuclearModule(Module):
    def __init__(self, rated_kw: float = 40.0, instance_num: int = 1, _id: int = None):
        name = "Nuclear" if instance_num == 1 else f"Nuclear-{instance_num}"
        super().__init__(id=_id or 5, name=name, type="nuclear", priority=5,
                         consumption_kw=3.0, criticality=5)
        self.rated_kw = rated_kw  # kW constante gerado por este reator

    def energy_logic(self, level: str):
        # Redução de 20% em SURPLUS é controlada pelo EnergyManager ao calcular geração
        self.active = True
        self.consumption_kw = 3.0
        return self.consumption_kw


class WindModule(Module):
    def __init__(self, wind_k: float = 0.002, instance_num: int = 1, _id: int = None):
        name = "Eólico" if instance_num == 1 else f"Eólico-{instance_num}"
        super().__init__(id=_id or 6, name=name, type="wind", priority=6,
                         consumption_kw=1.0, criticality=5)
        self.wind_k = wind_k  # coeficiente da curva de potência cúbica

    def energy_logic(self, level: str):
        # Embandeiramento é tratado pelo EnergyManager (lê sensor.wind_speed)
        self.active = True
        self.consumption_kw = 1.0
        return self.consumption_kw


# ─── Módulos de consumo ───────────────────────────────────────────────────────

class CommandModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        super().__init__(id=_id or 1, name="Command", type="command", priority=1,
                         consumption_kw=5.0, criticality=5)

    def energy_logic(self, level: str):
        self.active = True
        self.consumption_kw = 3.0 if level == "CRITICAL" else 5.0
        return self.consumption_kw


class LifeSupportModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        super().__init__(id=_id or 2, name="ECLSS", type="life_support", priority=2,
                         consumption_kw=20.0, criticality=5)

    def energy_logic(self, level: str):
        self.active = True
        self.consumption_kw = 12.0 if level == "CRITICAL" else 20.0
        return self.consumption_kw


class HabitatModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        super().__init__(id=_id or 3, name="Habitat", type="habitat", priority=3,
                         consumption_kw=15.0, criticality=4)

    def energy_logic(self, level: str):
        self.active = True
        if level == "CRITICAL":
            self.consumption_kw = 8.0
        elif level == "LOW":
            self.consumption_kw = 10.0
        elif level == "SURPLUS":
            self.consumption_kw = 18.0
        else:
            self.consumption_kw = 15.0
        return self.consumption_kw


class CommsModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        name = "Comms" if instance_num == 1 else f"Comms-{instance_num}"
        super().__init__(id=_id or 7, name=name, type="comms", priority=7,
                         consumption_kw=8.0, criticality=4)

    def energy_logic(self, level: str):
        if level == "CRITICAL":
            self.active = True
            self.consumption_kw = 2.0
        elif level == "LOW":
            self.active = True
            self.consumption_kw = 4.0
        else:
            self.active = True
            self.consumption_kw = 8.0
        return self.consumption_kw


class MedicalModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        name = "Medical" if instance_num == 1 else f"Medical-{instance_num}"
        super().__init__(id=_id or 8, name=name, type="medical", priority=8,
                         consumption_kw=10.0, criticality=4)

    def energy_logic(self, level: str):
        if level == "CRITICAL":
            self.active = True
            self.consumption_kw = 6.0
        elif level == "LOW":
            self.active = True
            self.consumption_kw = 8.0
        else:
            self.active = True
            self.consumption_kw = 10.0
        return self.consumption_kw


class FoodModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        name = "Food" if instance_num == 1 else f"Food-{instance_num}"
        super().__init__(id=_id or 9, name=name, type="food", priority=9,
                         consumption_kw=12.0, criticality=3)

    def energy_logic(self, level: str):
        if level == "CRITICAL":
            self.active = False
            self.consumption_kw = 0.0
        elif level == "LOW":
            self.active = True
            self.consumption_kw = 4.0
        else:
            self.active = True
            self.consumption_kw = 12.0
        return self.consumption_kw


class LogisticsModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        name = "Logistics" if instance_num == 1 else f"Logistics-{instance_num}"
        super().__init__(id=_id or 10, name=name, type="logistics", priority=10,
                         consumption_kw=6.0, criticality=3)

    def energy_logic(self, level: str):
        if level == "CRITICAL":
            self.active = False
            self.consumption_kw = 0.0
        elif level == "LOW":
            self.active = True
            self.consumption_kw = 3.0
        else:
            self.active = True
            self.consumption_kw = 6.0
        return self.consumption_kw


class ISRUModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        name = "ISRU" if instance_num == 1 else f"ISRU-{instance_num}"
        super().__init__(id=_id or 11, name=name, type="isru", priority=11,
                         consumption_kw=18.0, criticality=2)

    def energy_logic(self, level: str):
        if level in ("CRITICAL", "LOW"):
            self.active = False
            self.consumption_kw = 0.0
        elif level == "SURPLUS":
            self.active = True
            self.consumption_kw = round(18.0 * 1.2, 2)
        else:
            self.active = True
            self.consumption_kw = 18.0
        return self.consumption_kw


class WorkshopModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        name = "Workshop" if instance_num == 1 else f"Workshop-{instance_num}"
        super().__init__(id=_id or 12, name=name, type="workshop", priority=12,
                         consumption_kw=8.0, criticality=2)

    def energy_logic(self, level: str):
        if level == "CRITICAL":
            self.active = True
            self.consumption_kw = 3.0
        elif level == "LOW":
            self.active = True
            self.consumption_kw = 5.0
        else:
            self.active = True
            self.consumption_kw = 8.0
        return self.consumption_kw


class LabModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        name = "Lab" if instance_num == 1 else f"Lab-{instance_num}"
        super().__init__(id=_id or 13, name=name, type="lab", priority=13,
                         consumption_kw=10.0, criticality=2)

    def energy_logic(self, level: str):
        if level in ("CRITICAL", "LOW"):
            self.active = False
            self.consumption_kw = 0.0
        else:
            self.active = True
            self.consumption_kw = 10.0
        return self.consumption_kw


class SensorsModule(Module):
    def __init__(self, instance_num: int = 1, _id: int = None):
        name = "Sensors" if instance_num == 1 else f"Sensors-{instance_num}"
        super().__init__(id=_id or 14, name=name, type="sensors", priority=14,
                         consumption_kw=3.0, criticality=4)

    def energy_logic(self, level: str):
        if level == "CRITICAL":
            self.active = True
            self.consumption_kw = 1.0
        elif level == "LOW":
            self.active = True
            self.consumption_kw = 2.0
        else:
            self.active = True
            self.consumption_kw = 3.0
        return self.consumption_kw


# ─── Listas de módulos disponíveis para spawn ─────────────────────────────────

SPAWNABLE_GENERATION = [SolarModule, NuclearModule, WindModule]

SPAWNABLE_CONSUMPTION = [
    CommsModule, MedicalModule, FoodModule, LogisticsModule,
    ISRUModule, WorkshopModule, LabModule, SensorsModule,
]

ALL_MODULE_CLASSES = [
    CommandModule, LifeSupportModule, HabitatModule,
    SolarModule, NuclearModule, WindModule,
] + SPAWNABLE_CONSUMPTION


# ─── ModuleManager ────────────────────────────────────────────────────────────

class ModuleManager(GenericManager):
    def __init__(self):
        super().__init__()
        self._heap = []
        self._map  = {}           # id → Module
        self._id_counter = 100    # IDs ≥ 101 são auto-gerados (evita conflito com IDs fixos 1–14)
        self._type_count = {}     # cls → quantidade de instâncias já adicionadas

    def _next_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def _register_type(self, cls) -> int:
        count = self._type_count.get(cls, 0) + 1
        self._type_count[cls] = count
        return count

    def add(self, module: Module):
        # Conta instâncias para nomenclatura correta de duplicatas
        cls = type(module)
        self._type_count[cls] = self._type_count.get(cls, 0) + 1
        heapq.heappush(self._heap, module)
        self._map[module.id] = module

    def remove(self, module_id: int):
        if module_id in self._map:
            self._map[module_id].active = False
            del self._map[module_id]

    def find(self, module_id: int) -> Module:
        return self._map.get(module_id)

    def find_by_name(self, name: str) -> Module:
        return next((m for m in self._map.values() if m.name == name), None)

    def run_all(self):
        snapshot = sorted(self._heap)
        for module in snapshot:
            if module.active and not module.broken:
                module.do()

    def do_all(self):
        self.run_all()

    def active_modules(self) -> list:
        return [m for m in self._map.values() if m.active and not m.broken]

    def all_modules(self) -> list:
        return sorted(self._heap)

    def spawn_random(self, available_types: list) -> Module:
        """Spawna módulo aleatório SEM filtro de tipo — duplicatas permitidas."""
        if not available_types:
            return None
        ModuleClass = random.choice(available_types)
        # inst_num = contagem APÓS o add (add incrementa _type_count)
        current_count = self._type_count.get(ModuleClass, 0)
        inst_num = current_count + 1
        new_module = ModuleClass(instance_num=inst_num, _id=self._next_id())
        self.add(new_module)  # incrementa _type_count para current_count+1
        return new_module

    def spawn_generation(self) -> Module:
        """Força spawn de módulo de geração — chamado quando energia está LOW/CRITICAL."""
        return self.spawn_random(SPAWNABLE_GENERATION)
