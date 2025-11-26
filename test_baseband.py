from abc import ABC,abstractmethod
import numpy as np
import matplotlib.pyplot as plt

SAMPLES_PER_SYMBOL = 4
SYMBOL_RATE = 1  # symbols per second
FS = SYMBOL_RATE * SAMPLES_PER_SYMBOL


class PulseShape(ABC):

    def __init__(self, symbol_rate, fs, span):

        self.symbol_rate = symbol_rate
        self.fs = fs
        self.span = span
        self.symbol_period = float(1 / symbol_rate)
        self.samples_per_symbol = int(fs * self.symbol_period)

    @abstractmethod
    def generate(self):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")

    def display_info(self):
        print(f"Pulse Shape: {self.__class__.__name__}")
        print(f"Symbol Rate: {self.symbol_rate} symbols/second")
        print(f"Sampling Frequency: {self.fs} Hz")
        print(f"Number of Samples per Symbol: {self.samples_per_symbol}")
        print(f"Pulse Span: {self.span}")

class RectanglePulse(PulseShape):

    def generate(self):
        total_samples = self.samples_per_symbol * self.span
        pulse = np.zeros(total_samples)
        ones_of_rect_pulse = np.ones(self.samples_per_symbol)
        tail_len = total_samples - self.samples_per_symbol
        start_index = tail_len // 2
        end_index = start_index + self.samples_per_symbol
        pulse[start_index:end_index] = ones_of_rect_pulse
        return pulse


class CosinePulse(PulseShape):

    def generate(self):
        total_samples = self.samples_per_symbol * self.span

        t = np.linspace(- (self.symbol_period * self.span) / 2,
                        (self.symbol_period * self.span) / 2, total_samples, endpoint=True)
        pulse = np.cos(np.pi * t / self.symbol_period) ** 2
        return pulse

class BasebandSignalGenerator:

    def __init__(self, pulse,fs=FS, samples_per_symbol=SAMPLES_PER_SYMBOL):

        self.pulse_data = pulse
        self.pulse_len = len(pulse)
        self.fs = fs
        self.sym_rate = FS // len(pulse)  # Calculate symbol rate from FS and pulse length
        self.samples_per_symbol = samples_per_symbol
        self.span = self.pulse_len // self.samples_per_symbol

    def generate_baseband_signal(self, symbols) -> np.ndarray:
        """
        Creates the baseband signal by adding scaled and shifted pulses.
        This avoids a large convolution.
        The Baseband Signal is also Complex to support M-PSK/QA Modulations.

        Args:
            symbols (list): The list containing the mapped symbols.
        Returns:
            np.ndarray: The generated baseband signal.
        """
        num_sym = len(symbols)

        output_len = (num_sym - 1) * self.samples_per_symbol + self.pulse_len

        baseband = np.zeros(output_len, dtype=complex)

        for i, symbol in enumerate(symbols):
            start_index = i * self.samples_per_symbol
            baseband[start_index : start_index + self.pulse_len] += self.pulse_data * symbol
        return baseband

if __name__ == "__main__":

    rect_pulse_obj = RectanglePulse(symbol_rate=SYMBOL_RATE, fs=FS, span=2)
    cosine_pulse_obj = CosinePulse(symbol_rate=SYMBOL_RATE, fs=FS, span=2)



    rect_pulse_data = rect_pulse_obj.generate()
    cosine_pulse_data = cosine_pulse_obj.generate()

    symbol_seq = [1,1]

    rect_baseband_generator = BasebandSignalGenerator(rect_pulse_data)

    rect_baseband_signal = rect_baseband_generator.generate_baseband_signal(symbol_seq)

    plt.stem(rect_baseband_signal)
    plt.show()



