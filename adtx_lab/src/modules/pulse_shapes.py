'''
This is a Strategy Pattern implementation for different pulse shapes.

Each pulse shape class implements a `generate` method to create the pulse data.


'''

from abc import ABC,abstractmethod
import numpy as np

class PulseShape(ABC):

    def __init__(self, symbol_rate, fs, span):

        self.symbol_rate = symbol_rate
        self.fs = fs                                        # 1/T
        self.span = span
        self.symbol_period = float(1 / symbol_rate)         # T
        self.samples_per_symbol = int(fs * self.symbol_period) # fs/T

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


# class RaisedCosinePulse(PulseShape):

#     def __init__(self, symbol_rate, fs, span, roll_off):
#         super().__init__(symbol_rate, fs, span)
#         self.roll_off = roll_off

#     def generate(self):

#         total_samples = self.samples_per_symbol * self.span

#         t = np.linspace(- (self.symbol_period * self.span) / 2,
#                         (self.symbol_period * self.span) / 2, total_samples, endpoint=True)

#         si =np.sin(np.pi* t / self.symbol_period)

#         cos =np.cos(np.pi * self.roll_off * t / self.symbol_period)

#         pulse = si/ (np.pi*t /self.symbol_period) * cos/ (1- np.square(2*roll_off*t/ self.symbol_period ))
#         return pulse


if __name__ == "__main__":

    rect_pulse = RectanglePulse(symbol_rate=2, fs=60, span=1)
    rect_pulse_data = rect_pulse.generate()

