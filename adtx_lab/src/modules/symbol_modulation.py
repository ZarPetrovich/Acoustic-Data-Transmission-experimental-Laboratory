"""
    here happens the magic of Bit Mapping.

    Takes user Input from Bit Mapping QT Tab Widget!

    Creates desired Modulation Symbols from a desired Scheme.

    Implemented Schemes:

    2 - ASK: Amplitude Shit Keying with M = 2 (1 bit / Symbol)
    2 - PSK: Phase Shift Keying with M = 2 (1 bit / Symbol)


    """

from abc import ABC,abstractmethod
import numpy as np
from typing import Dict, Union # You likely have this
from adtx_lab.src.modules.bitmapper import *


class SymbolModulation(ABC):
    def __init__(self, m: int, mapper: BitMapper):
    # def __init__(self, m: int):
        if m <= 1 or (m & (m - 1)) != 0:
            raise ValueError("Cardinality (m) must be a power of 2 and greater than 1.")
        self.cardinality = m
        self.k = int(np.log2(m))
        self.mapper = mapper

    @abstractmethod
    def generate(self, bit_stream: np.ndarray):
        raise NotImplementedError("This method should be implemented by subclasses.")


class AmpShiftKeying(SymbolModulation):


    _ask_amplitude_levels: Dict[int, np.ndarray] = {
        # The base un-ordered/un-coded amplitude levels
        # (These are always arranged in increasing amplitude)
        2: np.array([0, 1]),                       # OOK (0, A)
        4: np.array([-3, -1, 1, 3]),
        8: np.array([-7, -5, -3, -1, 1, 3, 5, 7]),

    }
    _ask_bit_book: Dict[int,np.ndarray] = {
        2: np.array([0,1]),
        4: np.array([[0,0],[0,1],[1,1],[1,0]])
    }

    def __init__(self, cardinality: int, mapper: BitMapper):
        super().__init__(cardinality, mapper)
        # Generate the Gray-coded look-up table upon initialization
        self.codebook = self._generate_coded_codebook()

    def _generate_coded_codebook(self) -> Dict[int, complex]:
        """
        Generates the complex, power-normalized symbol look-up book
        based on the injected mapping strategy.
        """
        if self.cardinality not in self._ask_amplitude_levels:
            raise ValueError(f"Unsupported cardinality for ASK: {self.cardinality}")

        # 1. Get the base amplitude levels (Binary Index order)
        amplitude_levels = self._ask_amplitude_levels[self.cardinality]

        # 2. Get the Mapping Indices from the Strategy
        # If GrayMapper is used, map = [0, 1, 3, 2] for 4-ASK.
        # If BinaryMapper is used, map = [0, 1, 2, 3] for 4-ASK.
        map_indices = self.mapper.get_indices(self.k)

        # 3. Apply the Mapping and Normalization
        # Rearrange the base amplitudes according to the map
        coded_real_symbols = amplitude_levels[map_indices]

        # Normalization
        power = np.mean(amplitude_levels ** 2)
        normalization_factor = np.sqrt(power)
        normalized_real_symbols = coded_real_symbols / normalization_factor

        # 4. Create the Final Dictionary Look-up Book
        # The value is the Complex Symbol (I + j0)
        complex_codebook = normalized_real_symbols + 0.0j

        # Create a dictionary mapping the input binary index (0, 1, ...)
        # to the complex symbol.
        look_up_book = {i: complex_codebook[i] for i in range(self.cardinality)}

        return look_up_book

    def generate(self, bit_stream: str) -> np.ndarray:
        """
        Generates the complex symbol sequence using the look-up book.
        """
        if isinstance(bit_stream, str):
            bit_stream = np.array([int(b) for b in bit_stream])

        if len(bit_stream) % self.k != 0:
            raise ValueError("Length of bit sequence is not a multiple of log2(cardinality).")
        # 1. Bit Grouping and Binary-to-Decimal Indexing
        bit_groups = bit_stream.reshape(-1, self.k)
        weights = 2**np.arange(self.k - 1, -1, -1)
        # This index IS the binary index (0, 1, 2, 3, ...), which is the key for the lookup book.
        binary_symbol_indices = np.dot(bit_groups, weights)
        # 2. Look-up Symbols (Map each index to its complex symbol)
        symbol_sequence = np.array([self.codebook[i] for i in binary_symbol_indices])
        return symbol_sequence


