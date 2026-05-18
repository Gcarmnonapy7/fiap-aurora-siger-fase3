from colonia_aurora.core.item import Item
from colonia_aurora.core.storage import DataStorage


class Module(Item):
    def __init__(self, id: int, name: str, type: str, priority: int,
                 consumption_kw: float, criticality: int):
        super().__init__(name)
        self.id = id
        self.type = type
        self.priority = priority
        self.consumption_kw = consumption_kw
        self.criticality = criticality
        self.active = True
        self.broken = False

    def __eq__(self, other: "Module") -> bool:
        return self.priority == other.priority

    def __lt__(self, other: "Module") -> bool:
        return self.priority < other.priority

    def do(self):
        storage = DataStorage()
        level = storage.get("energy.level", "NOMINAL")
        return self.energy_logic(level)

    def energy_logic(self, level: str):
        raise NotImplementedError
