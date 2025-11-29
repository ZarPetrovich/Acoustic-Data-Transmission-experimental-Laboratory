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
    def __init__(self, m: int):
        if m <= 1 or (m & (m - 1)) != 0:
            raise ValueError("Cardinality (m) must be a power of 2 and greater than 1.")
        self.cardinality = m
        self.k = int(np.log2(m))

    @abstractmethod
    def generate(self, bit_stream: np.ndarray):
        raise NotImplementedError("This method should be implemented by subclasses.")

class AmpShiftKeying(SymbolModulation):
    def generate(self, bit_stream: np.ndarray):
        """
        Generates normalized M-ASK symbols from the bit sequence.
        The cardinality (M) is taken from the constructor.
        """
        if len(bit_stream) % self.k != 0:
            raise ValueError(
                "Length of bit sequence is not a multiple of log2(cardinality).")

        look_up_book = {
            2: np.array([-1, 1]),
            4: np.array([-3, -1, 1, 3]),
            8: np.array([-7, -5, -3, -1, 1, 3, 5, 7]),
            16: np.array([-15, -13, -11, -9, -7, -5, -3, -1,
                          1, 3, 5, 7, 9, 11, 13, 15])
        }

        if self.cardinality not in look_up_book:
            raise ValueError(f"Unsupported cardinality for ASK: {self.cardinality}")
        symbols = look_up_book[self.cardinality]
        num_symbols = len(bit_stream) // self.k
        symbol_sequence = np.zeros(num_symbols)

        for i in range(num_symbols):
            bit_chunk = bit_stream[i * self.k:(i + 1) * self.k]
            symbol_idx = int("".join(str(b) for b in bit_chunk), 2)
            symbol_sequence[i] = symbols[symbol_idx]
        # Normalize power to 1
        power = np.mean(symbol_sequence ** 2)
        symbol_sequence /= np.sqrt(power)

        return symbol_sequence





