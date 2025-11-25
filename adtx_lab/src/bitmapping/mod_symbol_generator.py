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


class SymbolModulation(ABC):

    def __init__(self, bit_seq: int, symbol_rate: int, cardinality):
        self.bit_sequence = bit_seq
        self.symbol_rate = symbol_rate
        self.cardinality = cardinality

    @abstractmethod
    def generate(self):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")

class AmpShiftKeying(SymbolModulation):

    def generate(self):
        """
        Generates normalized M-ASK symbols from the bit sequence.
        The cardinality (M) is taken from the constructor.
        """
        if self.cardinality <= 1 or (self.cardinality & (self.cardinality - 1)) != 0:
            raise ValueError("Cardinality must be a power of 2 and greater than 1.")

        k = int(np.log2(self.cardinality))

        if len(self.bit_sequence) % k != 0:
            raise ValueError(
                "Length of bit sequence is not a multiple of log2(cardinality).")

        # Group bits into symbols
        bit_groups = self.bit_sequence.reshape(-1, k)
        weights = 2**np.arange(k - 1, -1, -1)
        # Convert bit groups to integer symbol indices {0, 1, ..., M-1}
        symbol_indices = np.dot(bit_groups, weights)

        # --- Normalization to achieve average energy of 1 ---
        M = self.cardinality

        # The un-normalized symbols are {0, 1, ..., M-1}
        unnormalized_symbols = np.arange(M)

        # Calculate average energy of the un-normalized symbol set
        avg_energy = np.mean(np.square(unnormalized_symbols))

        # Calculate scaling factor
        scaling_factor = 1 / np.sqrt(avg_energy)

        # Map indices to scaled amplitude levels
        scaled_amplitudes = unnormalized_symbols * scaling_factor

        # Create the final symbol sequence
        symbol_sequence = scaled_amplitudes[symbol_indices]

        return symbol_sequence




