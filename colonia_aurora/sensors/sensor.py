from colonia_aurora.seed import rng
from colonia_aurora.core.item import Item


class Sensor(Item):
    def __init__(self, name: str, min_val: float, max_val: float, variation: float, initial: float = None):
        super().__init__(name)
        self.min_val = min_val
        self.max_val = max_val
        self.variation = variation
        self.current_val = initial if initial is not None else (min_val + max_val) / 2

    def __eq__(self, other: "Sensor") -> bool:
        return self.current_val == other.current_val

    def __lt__(self, other: "Sensor") -> bool:
        return self.current_val < other.current_val

    def do(self) -> float:
        self.current_val += rng.uniform(-self.variation, self.variation)
        self.current_val = max(self.min_val, min(self.max_val, self.current_val))
        return self.current_val

    def apply_modifier(self, factor: float):
        self.current_val *= factor
        self.current_val = max(self.min_val, min(self.max_val, self.current_val))
