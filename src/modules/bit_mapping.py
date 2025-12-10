from abc import ABC,abstractmethod
import numpy as np


class BitMapper(ABC):
    """Abstract Base Class for Bit-to-Symbol Index Mapping."""

    @abstractmethod
    def get_indices(self, k: int) -> np.ndarray:
        """Returns the mapping array for M=2^k symbols."""
        pass

class GrayMapper(BitMapper):
    """Concrete Strategy for Gray Code Mapping."""

    def get_indices(self, k: int) -> np.ndarray:
        """Generates the Gray code mapping array for k bits."""
        M = 2**k
        # Gray code formula: G = B XOR (B >> 1)
        gray_indices = np.array([i ^ (i >> 1) for i in range(M)], dtype=int)
        return gray_indices

class BinaryMapper(BitMapper):
    """Concrete Strategy for Simple Binary Code Mapping."""

    def get_indices(self, k: int) -> np.ndarray:
        """Generates the simple binary mapping array (index i maps to i)."""
        M = 2**k
        # Binary map: Index i -> i
        return np.arange(M, dtype=int)

class RandomMapper(BitMapper):
    """Concrete Strategy for generating a fixed, pseudo-random bit-to-symbol index mapping."""

    def __init__(self, seed: int = None):
        """
        Initializes the mapper with an optional seed for reproducible randomness.
        The same seed will always produce the same random mapping array.
        """
        self.seed = seed

    def get_indices(self, k: int) -> np.ndarray:
        """
        Generates a random permutation of the indices 0 to M-1.
        The value at array index 'i' is the randomized symbol index corresponding
        to the binary index 'i'.
        """
        M = 2**k

        # Initialize a reproducible random number generator
        rng = np.random.default_rng(self.seed)

        # Generate the ordered indices [0, 1, ..., M-1]
        ordered_indices = np.arange(M, dtype=int)

        # Randomly shuffle the indices (creates the random mapping)
        random_mapping = rng.permutation(ordered_indices)

        return random_mapping

