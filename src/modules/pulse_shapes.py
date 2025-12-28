'''
This is a Strategy Pattern implementation for different pulse shapes.

Each pulse shape class implements a `generate` method to create the pulse data.


'''

from abc import ABC,abstractmethod
import numpy as np

class PulseShape(ABC):

    def __init__(self, symbol_rate, fs, span, roll_off = None):

        self.symbol_rate = symbol_rate
        self.fs = fs                                        # 1/T
        self.span = span
        self.roll_off = roll_off
        self.symbol_period = float(1 / symbol_rate)         # T
        self.samples_per_symbol = int(fs * self.symbol_period) # fs/T

    @abstractmethod
    def generate(self):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")

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


class CosineSquarePulse(PulseShape): # Renamed for clarity
    def generate(self):

        total_samples = self.samples_per_symbol * self.span

        Ts = self.symbol_period

        t = np.linspace(- (Ts * self.span) / 2,
                        (Ts * self.span) / 2, total_samples, endpoint=True)

        pulse = np.zeros_like(t, dtype=float)

        # The Cosine-Squared pulse is non-zero only for |t| <= Ts (one full symbol period, not Ts/2)
        non_zero_mask = np.abs(t) <= Ts
        t_non_zero = t[non_zero_mask]

        # h(t) = cos^2(pi*t / (2*Ts)) for |t| <= Ts
        #
        pulse[non_zero_mask] = np.square(np.cos(np.pi * t_non_zero / (2 * Ts)))

        return pulse


class RaisedCosinePulse(PulseShape):

    def generate(self):

        total_samples = self.samples_per_symbol * self.span

        # 1. Create the time vector (t)
        t = np.linspace(- (self.symbol_period * self.span) / 2,
                        (self.symbol_period * self.span) / 2, total_samples, endpoint=True)

        pulse = np.zeros_like(t, dtype=float)

        t_norm = t / self.symbol_period  # Normalized time (t / Ts)

        # # ---- 2. Create Masks for Calculations ----

        # Define idx in timeaxis where calculations will be 0 (on all x-axis crossing points)
        # as Treu/False Array. True where these conditions are true
        t_is_zero = np.isclose(t, 0)
        t_is_singular = np.isclose(np.abs(t), self.symbol_period / (2 * self.roll_off))

        # Flip the Mask for Calculation True--> False --> Do not Calculate on these idx
        general_mask = ~t_is_zero & ~t_is_singular

        # --- 3. Calculate Raised Cosine Pulse for General Cases ---
        t_norm_gen = t_norm[general_mask]

        # Numerator: sin(pi*t_norm) * cos(pi*alpha*t_norm)
        numerator = np.sin(np.pi * t_norm_gen) * np.cos(np.pi * self.roll_off * t_norm_gen)

        # Denominator: (pi*t_norm) * (1 - (2*alpha*t_norm)^2)
        denumerator = (np.pi * t_norm_gen) * (1 - np.square(2 * self.roll_off * t_norm_gen))

        with np.errstate(divide='ignore', invalid='ignore'):
             pulse[general_mask] = numerator / denumerator

        # --- 4. Enforce Correct Values at Singularities ---

        # a) At t = 0: h_RC(0) = 1.0
        pulse[t_is_zero] = 1.0

        # b) At t = +/- Ts / (2*alpha): h_RC(t) = 0.0 (Zero-crossing)
        pulse[t_is_singular] = 0.0

        return pulse

if __name__ == "__main__":
    pass

