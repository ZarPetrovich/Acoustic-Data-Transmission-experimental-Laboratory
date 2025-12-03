import numpy as np
from adtx_lab.src.dataclasses.metadata_models import ModSchemeLUT


class SymbolSequencer:

    def __init__(self, mod_scheme: ModSchemeLUT):
        self.mod_scheme_lut = mod_scheme.look_up_table
        self.k = int(np.log2(mod_scheme.mod_scheme.cardinality))

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
        symbol_sequence = np.array([self.mod_scheme_lut[i] for i in binary_symbol_indices])
        return symbol_sequence