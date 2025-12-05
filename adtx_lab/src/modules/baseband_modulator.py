import numpy as np
from adtx_lab.src.dataclasses.dataclass_models import SymbolStream, PulseSignal


class BasebandSignalGenerator:
    """
    Creates a instance that can generate baseband signals
    from pulse shapes. Each Pulse Shape need it´s own Generator
    Attributes:
        PulseSignal pulse_signal_container: The Pulse Signal Dataclass Object containing the pulse shape data
    """
    def __init__(self, pulse_signal_container: PulseSignal):

        self.pulse_data = pulse_signal_container.data
        self.pulse_len = len(pulse_signal_container.data)
        self.fs = pulse_signal_container.fs
        self.sym_rate = pulse_signal_container.sym_rate
        self.samples_per_symbol = self.fs // self.sym_rate
        self.span = pulse_signal_container.span

    def generate_baseband_signal(self, symbol_stream: SymbolStream) -> np.ndarray:
        """
        Creates the baseband signal by adding scaled and shifted pulses.
        This avoids a large convolution.
        The Baseband Signal is also Complex to support M-PSK/QA Modulations.

        Args:
            symbol_stream (Symbol Data Container): The Dataclass Object containing the mapped symbols.
        Returns:
            BasebandData: The generated baseband signal wrapped in a data container.
        """
        symbols = symbol_stream.data
        num_sym = len(symbols)

        output_len = (num_sym - 1) * self.samples_per_symbol + self.pulse_len

        baseband = np.zeros(output_len, dtype=complex)

        for i, symbol in enumerate(symbols):
            start_index = i * self.samples_per_symbol
            baseband[start_index : start_index + self.pulse_len] += self.pulse_data * symbol
        return baseband

    def generate_iteration_breakdown(self, symbol_stream: SymbolStream):
        """
        Generates the baseband signal while yielding the iteration breakdown.
        This is useful for debugging or visualization purposes.

        Args:
            symbol_stream (Symbol Data Container): The object containing the mapped symbols.
        Yields:
            Tuple: (current_index, start_index, end_index, current_baseband)
        """
        symbols = symbol_stream.data
        num_sym = len(symbols)

        output_len = (num_sym - 1) * self.samples_per_symbol + self.pulse_len

        baseband = np.zeros(output_len, dtype=complex)

        for i, symbol in enumerate(symbols):
            start_index = i * self.samples_per_symbol
            end_index = start_index + self.pulse_len
            baseband[start_index:end_index] += self.pulse_data * symbol
            yield (i, start_index, end_index, baseband.copy())

if __name__ == "__main__":
    None
