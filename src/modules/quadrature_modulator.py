'''

This is a Strategy Pattern implementation for different Modulatioan Schemes.

Each Scheme class implements a `modulate` method to create the a bandpass Signal.

The Datacan be stored in a Signal dataclass Container for further Action.

'''

from abc import abstractmethod
import numpy as np
from src.dataclasses.dataclass_models import BasebandSignal



class Modulator():

    def __init__(self,f_carrier):

        self.f_carrier = f_carrier

    @abstractmethod
    def modulate(self,baseband_signal):
        raise NotImplementedError("This method should be implemented by subclasses.")


class QuadratureModulator(Modulator):

    def modulate(self, bandpass_signal: BasebandSignal):

        num_samples = len(bandpass_signal.data)
        time_vector = np.arange(num_samples) / bandpass_signal.fs

        carrier_cos = np.cos( 2 * np.pi * time_vector * self.f_carrier)
        carrier_sin = np.sin( 2 * np.pi * time_vector * self.f_carrier)

        real_bb = np.real(bandpass_signal.data)
        q_bb = np.imag(bandpass_signal.data)

        mod_signal = np.sqrt(2) * (real_bb * carrier_cos - q_bb * carrier_sin)

        return mod_signal


class QuadratureDemodulator(Modulator):

    def demodulate(self, bandpass_signal: np.ndarray, fs: int):

        time_vector = np.arange(len(bandpass_signal)) / fs

        carrier_cos = np.cos( 2 * np.pi * time_vector * self.f_carrier)
        carrier_sin = np.sin( 2 * np.pi * time_vector * self.f_carrier)

        i_component = 2 * bandpass_signal * carrier_cos
        q_component = -2 * bandpass_signal * carrier_sin

        baseband_signal = i_component + 1j * q_component

        return baseband_signal




