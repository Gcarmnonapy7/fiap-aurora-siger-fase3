from colonia_aurora.core.item import Item
from colonia_aurora.core.storage import DataStorage
from colonia_aurora.core.manager import GenericManager


class CrewMember(Item):
    ROLES = ["commander", "engineer", "medic", "scientist", "technician"]

    def __init__(self, name: str, role: str):
        super().__init__(name)
        self.role = role
        self.health = 1.0
        self.status = "idle"
        self.assigned_module = None
        self.repair_ticks_left = 0

    def __eq__(self, other: "CrewMember") -> bool:
        return self.health == other.health

    def __lt__(self, other: "CrewMember") -> bool:
        return self.health < other.health

    def do(self):
        self._update_health()
        self._update_repair()

    def _update_health(self):
        level = DataStorage().get("energy.level", "NOMINAL")
        if level == "CRITICAL":
            self.health = max(0.0, self.health - 0.05)
            if self.health == 0.0:
                self.status = "incapacitated"
        elif level in ("HIGH", "SURPLUS"):
            self.health = min(1.0, self.health + 0.01)
            if self.status == "incapacitated" and self.health > 0.0:
                self.status = "idle"

    def _update_repair(self):
        if self.status == "repairing" and self.repair_ticks_left > 0:
            self.repair_ticks_left -= 1
            if self.repair_ticks_left == 0:
                if self.assigned_module and self.assigned_module.broken:
                    self.assigned_module.broken = False
                    self.assigned_module.active = True
                self.status = "idle"
                self.assigned_module = None

    def assign_repair(self, module, ticks: int):
        self.status = "repairing"
        self.assigned_module = module
        self.repair_ticks_left = ticks


class CrewManager(GenericManager):
    def assign_repair(self, module, ticks: int) -> bool:
        available = self.available_engineers()
        if available:
            available[0].assign_repair(module, ticks)
            return True
        return False

    def available_engineers(self) -> list:
        return [
            m for m in self._items
            if m.role in ("engineer", "technician") and m.status == "idle"
        ]

    def do_all(self):
        for member in self._items:
            member.do()
