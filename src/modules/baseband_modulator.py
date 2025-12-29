import numpy as np
from scipy.signal import fftconvolve
from src.dataclasses.dataclass_models import SymbolStreamModel, PulseModel


class BasebandSignalGenerator:
    """
    Creates a instance that can generate baseband signals
    from pulse shapes. Each Pulse Shape need it´s own Generator
    Attributes:
        PulseSignal pulse_signal_container: The Pulse Signal Dataclass Object containing the pulse shape data
    """
    def __init__(self, pulse_signal_container: PulseModel):

        self.pulse_data = pulse_signal_container.data
        self.pulse_len = len(pulse_signal_container.data)
        self.fs = pulse_signal_container.fs
        self.sym_rate = pulse_signal_container.sym_rate
        self.samples_per_symbol = self.fs // self.sym_rate
        self.span = pulse_signal_container.span

    # def generate_baseband_signal(self, symbol_stream: SymbolStream) -> np.ndarray:
    #     """
    #     Creates the baseband signal by adding scaled and shifted pulses.
    #     This avoids a large convolution.
    #     The Baseband Signal is also Complex to support M-PSK/QA Modulations.

    #     Args:
    #         symbol_stream (Symbol Data Container): The Dataclass Object containing the mapped symbols.
    #     Returns:
    #         BasebandData: The generated baseband signal wrapped in a data container.
    #     """
    #     symbols = symbol_stream.data
    #     num_sym = len(symbols)

    #     output_len = (num_sym - 1) * self.samples_per_symbol + self.pulse_len

    #     baseband = np.zeros(output_len, dtype=complex)

    #     for i, symbol in enumerate(symbols):
    #         start_index = i * self.samples_per_symbol
    #         baseband[start_index : start_index + self.pulse_len] += self.pulse_data * symbol
    #     return baseband

    def generate_baseband_signal(self, symbol_stream: SymbolStreamModel) -> np.ndarray:

        symbols = symbol_stream.data
        num_symbols = len(symbols)

        # Calculate the required length for the impulse stream
        # (num_symbols - 1) * self.samples_per_symbol + 1
        impulse_stream_len = (num_symbols - 1) * self.samples_per_symbol + 1
        impulse_stream = np.zeros(impulse_stream_len, dtype=complex)

        # Place the complex symbol values at the correct symbol intervals
        # The slice [::self.samples_per_symbol] targets indices 0, S, 2S, 3S, ...
        impulse_stream[::self.samples_per_symbol] = symbols

        # 2. Convolve the upsampled symbol stream with the pulse shape.
        baseband = fftconvolve(impulse_stream, self.pulse_data)
        return baseband




    def generate_iteration_breakdown(self, symbol_stream: SymbolStreamModel):
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
