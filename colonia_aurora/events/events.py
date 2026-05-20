import random
from colonia_aurora.core.storage import DataStorage
from colonia_aurora.core.manager import GenericManager
from colonia_aurora.events.event import Event


class ColdFront(Event):
    def __init__(self):
        super().__init__(
            name="Frente Fria",
            type="ColdFront",
            severity=2,
            duration_ticks=random.randint(12, 48),
        )

    def apply(self, storage: DataStorage):
        storage.set("event.active", self.type)

    def revert(self, storage: DataStorage):
        storage.set("event.active", None)


class Sandstorm(Event):
    def __init__(self):
        super().__init__(
            name="Tempestade de Areia",
            type="Sandstorm",
            severity=3,
            duration_ticks=random.randint(6, 72),
        )

    def apply(self, storage: DataStorage):
        storage.set("event.active", self.type)

    def revert(self, storage: DataStorage):
        storage.set("event.active", None)


class EquipmentFailure(Event):
    def __init__(self, module, repair_ticks: int):
        super().__init__(
            name=f"Falha: {module.name}",
            type="EquipmentFailure",
            severity=1,
            duration_ticks=repair_ticks,
        )
        self.module = module
        module.broken = True
        module.active = False

    def apply(self, storage: DataStorage):
        pass  # efeito já aplicado no __init__

    def revert(self, storage: DataStorage):
        self.module.broken = False
        self.module.active = True


class EventManager(GenericManager):
    def __init__(self):
        super().__init__()
        self._active_event = None
        self._failure_events = []
        self._event_log = []

    def check_and_roll(self, module_manager, crew_manager, storage: DataStorage):
        # Processa evento climático ativo
        if self._active_event:
            self._active_event.do()
            if self._active_event.expired:
                self._event_log.append(f"Encerrado: {self._active_event.name}")
                expired_evt = self._active_event
                self._active_event = None      # limpa referência antes de reverter storage
                expired_evt.revert(storage)
        else:
            # Rola para novo evento climático
            roll = random.random()
            if roll < 0.03:
                evt = ColdFront()
                self._active_event = evt       # atribui antes de storage para dashboard consistente
                self._event_log.append(f"NOVO: {evt.name} ({evt.duration_ticks} ticks)")
                evt.apply(storage)
            elif roll < 0.05:
                evt = Sandstorm()
                self._active_event = evt
                self._event_log.append(f"NOVO: {evt.name} ({evt.duration_ticks} ticks)")
                evt.apply(storage)

        # Garante que event.active esteja correto quando não há evento
        if not self._active_event:
            storage.set("event.active", None)

        # Processa falhas de equipamento em andamento
        resolved = []
        for fail in self._failure_events:
            fail.do()
            if fail.expired:
                fail.revert(storage)
                self._event_log.append(f"Reparado: {fail.module.name}")
                resolved.append(fail)
        for r in resolved:
            self._failure_events.remove(r)

        # Rola falhas de equipamento (0.5% por módulo ativo)
        for mod in module_manager.active_modules():
            if random.random() < 0.005:
                repair_ticks = random.randint(2, 12)
                fail = EquipmentFailure(mod, repair_ticks)
                self._failure_events.append(fail)
                self._event_log.append(f"FALHA: {mod.name} — reparo em {repair_ticks} ticks")
                # Tenta alocar tripulante técnico
                crew_manager.assign_repair(mod, repair_ticks)

    @property
    def active_event(self):
        return self._active_event

    @property
    def active_event_name(self) -> str:
        if self._active_event:
            return self._active_event.name
        return "Nenhum"

    @property
    def active_event_ticks(self) -> int:
        if self._active_event:
            return self._active_event.duration_ticks
        return 0

    @property
    def log(self) -> list:
        return list(self._event_log[-30:])
