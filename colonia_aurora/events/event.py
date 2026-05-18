from colonia_aurora.core.item import Item


class Event(Item):
    def __init__(self, name: str, type: str, severity: int, duration_ticks: int):
        super().__init__(name)
        self.type = type
        self.severity = severity
        self.duration_ticks = duration_ticks

    def __eq__(self, other: "Event") -> bool:
        return self.type == other.type

    def __lt__(self, other: "Event") -> bool:
        return self.severity < other.severity

    def do(self):
        if self.duration_ticks > 0:
            self.duration_ticks -= 1

    def apply(self, storage):
        raise NotImplementedError

    def revert(self, storage):
        raise NotImplementedError

    @property
    def expired(self) -> bool:
        return self.duration_ticks <= 0
