"""
    here happens the magic of Bit Mapping.

    Takes user Input from Bit Mapping QT Tab Widget!

    Creates desired Modulation Symbols from a desired Scheme.

    Implemented Schemes:

    2 - ASK: Amplitude Shit Keying with M = 2 (1 bit / Symbol)
    2 - PSK: Phase Shift Keying with M = 2 (1 bit / Symbol)


    """

from abc import ABC,abstractmethod
from typing import Dict
import numpy as np
from src.modules.bit_mapping import BitMapper


class ModulationScheme(ABC):
    def __init__(self, m: int, mapper: BitMapper):
    # def __init__(self, m: int):
        if m <= 1 or (m & (m - 1)) != 0:
            raise ValueError("Cardinality (m) must be a power of 2 and greater than 1.")
        self.cardinality = m
        self.k = int(np.log2(m))
        self.mapper = mapper

    @abstractmethod
    def _generate_lut(self):
        raise NotImplementedError("This method should be implemented by subclasses")


class AmpShiftKeying(ModulationScheme):
    """
    Revised Amplitude Shift Keying modulator.
    Uses an algorithmic approach to generate symmetric, odd-integer amplitude levels.
    """

    def _generate_lut(self) -> Dict[int, complex]:
        """
        Generates the complex, power-normalized symbol look-up table.
        """
        M = self.cardinality
        k = self.k

        if not (M > 0 and (M & (M - 1) == 0)):
             raise ValueError(f"Cardinality M={M} must be a power of 2.")

        amplitude_levels = np.arange(-M + 1, M, 2)

        map_indices = self.mapper.get_indices(k)

        coded_real_symbols = amplitude_levels[map_indices]

        # Normalization (Crucial for consistent BER performance comparison)
        # Power = Mean of |symbol|^2
        power = np.mean(amplitude_levels ** 2)
        normalization_factor = np.sqrt(power) # Amplitude scaling factor

        normalized_real_symbols = coded_real_symbols / normalization_factor

        # 4. Create the Final Dictionary Look-up Book
        # The value is the Complex Symbol (I + j0)
        complex_codebook = normalized_real_symbols + 0.0j

        look_up_book = {i: complex_codebook[i] for i in range(M)}

        return look_up_book

    def __init__(self, cardinality: int, mapper: BitMapper):
        super().__init__(cardinality, mapper)
        self.codebook = self._generate_lut()



class PhaseShiftKeying(ModulationScheme):


    def _generate_lut(self) -> Dict[int, complex]:
        """
        Generates the complex, power-normalized symbol look-up book
        based on the injected mapping strategy.
        """
        M = self.cardinality
        k = self.k

        if not (M > 0 and (M & (M - 1) == 0)):
             raise ValueError(f"Cardinality M={M} must be a power of 2.")

        # 1. Generate the Base Phase Angles for M-PSK
        base_phase_angles = np.array([2 * np.pi * i / M for i in range(M)])

        # 2. Get the Mapping Indices from the Injected Mapper Strategy
        map_indices = self.mapper.get_indices(k)

        # 3. Apply the Mapping to get Coded Phase Angles
        coded_phase_angles = base_phase_angles[map_indices]

        # 4. Convert Phase Angles to Complex Symbols (Unit Circle)
        complex_codebook = np.exp(1j * coded_phase_angles)

        # 5. Create the Final Dictionary Look-up Book
        look_up_book = {i: complex_codebook[i] for i in range(M)}

        return look_up_book

    def __init__(self, cardinality: int, mapper: BitMapper):
        super().__init__(cardinality, mapper)
        self.codebook = self._generate_lut()

