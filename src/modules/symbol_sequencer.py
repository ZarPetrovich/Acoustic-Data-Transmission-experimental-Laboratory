import numpy as np
from src.dataclasses.dataclass_models import ModSchemeLUT


class SymbolSequencer:

    def __init__(self, mod_scheme_container: ModSchemeLUT):
        self.mod_scheme_lut = mod_scheme_container.look_up_table
        self.k = mod_scheme_container.cardinality

    def generate(self, bit_stream: np.array) -> np.ndarray:
        """
        Generates the complex symbol sequence using the look-up book.

        """
        bits_per_symbol = int(np.log2(self.k))
        num_symbols = len(bit_stream) // bits_per_symbol

        # Convert Bit stream to chunks of size bit/symbol

        truncated_bits = bit_stream[:num_symbols * bits_per_symbol] # slice Bitstream to fit complete symbols

        chunk_array = truncated_bits.reshape((num_symbols, bits_per_symbol))

        sym_idx_array = [] # Hold Mapped IDX from binary --> Integer loop Calculation

        # The Loop Converts each chunk of bits into its corresponding symbol index for LUT Dictionary
        # for eg. 01 --> 1 | 11 --> 3 | 10 --> 2 | 110 --> 5
        for chunks in chunk_array:
            index = chunks.dot(1 << np.arange(bits_per_symbol)[::-1])
            sym_idx_array.append(index)

        # Map Indices to Symbols using the Look-Up Table and Index from the loop
        symbol_sequence = np.array([self.mod_scheme_lut[idx] for idx in sym_idx_array], dtype=object)

        return symbol_sequence

