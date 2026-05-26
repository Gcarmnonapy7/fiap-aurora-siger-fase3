from time import time
from typing import Optional, List, TypeVar, Sequence

T = TypeVar('T')


class RandomLCG:
    """
    Linear Congruential Generator (LCG) implementation from scratch.

    LCG Formula: X_{n+1} = (a * X_n + c) mod m

    Where:
    - X_n is the current state (seed)
    - a is the multiplier
    - c is the increment
    - m is the modulus
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """
        Initialize the LCG with a seed.

        Using parameters from Numerical Recipes (a well-tested LCG):
        - m = 2^32
        - a = 1664525
        - c = 1013904223
        """
        self.a = 1664525
        self.c = 1013904223
        self.m = 2 ** 32

        if seed is None:
            seed = int(time() * 1000000) % self.m

        self.state = seed % self.m
        self.initial_seed = self.state

    def set_seed(self, seed: int) -> None:
        self.state = seed % self.m
        self.initial_seed = self.state

    def next_int(self) -> int:
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def random(self) -> float:
        return self.next_int() / self.m

    def uniform(self, a: float, b: float) -> float:
        """Return a random float N such that a <= N <= b."""
        return a + (b - a) * self.random()

    def randint(self, low: int, high: int) -> int:
        if low > high:
            raise ValueError("low must be less than or equal to high.")
        range_size = high - low + 1
        return low + (self.next_int() % range_size)

    def choice(self, sequence: Sequence[T]) -> T:
        if not sequence:
            raise ValueError("Cannot select from an empty sequence.")
        index = self.randint(0, len(sequence) - 1)
        return sequence[index]

    def shuffle(self, array: List[T]) -> None:
        n = len(array)
        for i in range(n - 1, 0, -1):
            j = self.randint(0, i)
            array[i], array[j] = array[j], array[i]

    def get_state(self) -> int:
        return self.state
