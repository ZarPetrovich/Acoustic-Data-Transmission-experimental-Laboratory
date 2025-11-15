import numpy as np
from adtx_lab.src.dataclasses.bitseq_models import BitSequence
from adtx_lab.src.dataclasses.signal_models import PulseSignal


class BasebandSignalGenerator:
    """
    Creates a instance that can generate baseband signals
    from pulse shapes. Each Pulse Shape need it´s own Generator
    Attributes:
        pulse_data (np.ndarray): The pulse shape data.
        sym_rate (int): Symbol rate.
        samples_per_symbol (int): Number of samples per symbol.
    """
    def __init__(self, pulse_obj: PulseSignal):

        self.pulse_data = pulse_obj.data
        self.pulse_len = len(pulse_obj.data)
        self.fs = pulse_obj.fs
        self.sym_rate = pulse_obj.sym_rate
        self.samples_per_symbol = self.fs // self.sym_rate

    def generate_baseband_signal(self, symbol_object: BitSequence) -> np.ndarray:
        """
        Creates the baseband signal by adding scaled and shifted pulses.
        This avoids a large convolution.
        Args:
            symbol_object (BitSequence): The object containing the mapped symbols.
        Returns:
            BasebandData: The generated baseband signal wrapped in a data container.
        """
        symbols = symbol_object.data
        num_sym = len(symbols)

        output_len = (num_sym - 1) * self.samples_per_symbol + self.pulse_len
        baseband = np.zeros(output_len)

        for i, symbol in enumerate(symbols):
            if symbol == 0:  # No need to add anything for a zero
                continue
            start_index = i * self.samples_per_symbol
            end_index = start_index + self.pulse_len
            baseband[start_index:end_index] += self.pulse_data * symbol

        final_len = num_sym * self.samples_per_symbol
        return baseband[:final_len]


if __name__ == "__main__":
    None
