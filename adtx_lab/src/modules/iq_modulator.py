'''

This is a Strategy Pattern implementation for different Modulatioan Schemes.

Each Scheme class implements a `modulate` method to create the a bandpass Signal.

The Datacan be stored in a Signal dataclass Container for further Action.

'''

from abc import abstractmethod
import numpy as np
from adtx_lab.src.dataclasses.models import BasebandSignal



class Modulator():

    def __init__(self,f_carrier, amplitude, fs):

        self.f_carrier = f_carrier
        self.amplitude = amplitude
        self.fs = fs

    @abstractmethod
    def modulate(self,baseband_signal):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def display_info(self):
        print(f"Modulation Type: {self.__class__.__name__}")
        print(f"Carrier Frequency: {self.f_carrier} Hz")
        print(f"Amplitude: {self.amplitude}")
        print(f"Sampling Frequency: {self.fs} Hz")


class AmplitudeModulator(Modulator):

    def modulate(self, baseband_obj: BasebandSignal):
        time_vector = np.arange(len(baseband_obj.data)) / self.fs
        carrier = np.cos( 2 * np.pi * time_vector * self.f_carrier)
        mod_signal = self.amplitude * carrier * baseband_obj.data
        return mod_signal


def load_signal_from_txt(filename="baseband_signal.txt"):
    """Loads a signal from a text file into a NumPy array."""
    try:
        signal = np.loadtxt(filename)
        print(f"Successfully loaded signal from {filename}")
        return signal
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return None





