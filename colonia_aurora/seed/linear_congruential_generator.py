from time import time
from typing import Optional,List,TypeVar,Sequence

T = TypeVar('T') # template type

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
    def __init__(self,seed: Optional[int]= None) -> None:
        """
        Initialize the LCG with a seed.
        
        Using parameters from Numerical Recipes (a well-tested LCG):
        - m = 2^32
        - a = 1664525
        - c = 1013904223
        """
        self.a = 1664525
        self.c = 1013904223
        self.m = 2**32
        
        if seed is None:
            seed = int(time() * 1000000) % self.m
        
        self.state = seed % self.m
        self.initial_seed = self.state
        
    def set_seed(self,seed : int) -> None:
        """
        Reset the generator with a new seed
        """
        
        self.state = seed % self.m
        self.initial_seed = self.state
        
    def next_int(self) -> int:
        """
        Generate the next random integer in range (0,m-1) ==> next step
        """
        self.state = (self.a * self.state + self.c) % self.m
        return self.state
    
    def random(self) -> float:
        """
        Generate a random float with the current generated state divided by the modulus
        """
        
        return self.next_int / self.m
    
    def randint(self,low : int,high: int ) -> int:
        """
        Generate a integer in range of low and high
        """
        
        if low > high:
            raise ValueError("low must be higher them the second parameter.")
        
        range_size = high - low + 1
        
        return low + (self.next_int() % range_size)
    
    def choice(self,sequence: Sequence[T]) -> T:
        """
        Randomly chooses an element from a non empty sequence (obj)
        """
        
        if not sequence : 
            raise ValueError("Cannot select from a empty sequence")
        
        index = self.randint(0,len(sequence) - 1)
        
        return sequence[index]
    
    
    def shuffle(self,array : List[T]) -> None:
        n = len(array)
        
        for i in range(n-1 , 0 , -1) : #backwards
            
            j = self.randint(0,i)
            array[i],array[j] = array[j], array[i] 
            
          # No return statement - modifies original array
    
    def get_state(self) -> int : 
        """
        Get the LCG state at the moment
        """
        return self.state