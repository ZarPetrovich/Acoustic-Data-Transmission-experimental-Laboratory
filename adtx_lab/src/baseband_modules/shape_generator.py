'''
This is a Strategy Pattern implementation for different pulse shapes.

Each pulse shape class implements a `generate` method to create the pulse data.


'''

from abc import abstractmethod
import numpy as np

class PulseShape():

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
        pulse = np.ones(self.samples_per_symbol)
        return pulse


class CosinePulse(PulseShape):

    def generate(self):
        total_samples = self.samples_per_symbol * self.span

        t = np.linspace(- (self.symbol_period * self.span) / 2,
                        (self.symbol_period * self.span) / 2, total_samples, endpoint=True)
        pulse = np.cos(np.pi * t / self.symbol_period) ** 2
        return pulse


if __name__ == "__main__":

    rect_pulse = RectanglePulse(symbol_rate=2, fs=60, span=1)
    rect_pulse_data = rect_pulse.generate()

