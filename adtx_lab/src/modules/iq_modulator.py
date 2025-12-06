'''

This is a Strategy Pattern implementation for different Modulatioan Schemes.

Each Scheme class implements a `modulate` method to create the a bandpass Signal.

The Datacan be stored in a Signal dataclass Container for further Action.

'''

from abc import abstractmethod
import numpy as np
from adtx_lab.src.dataclasses.dataclass_models import BasebandSignal



class Modulator():

    def __init__(self,f_carrier):

        self.f_carrier = f_carrier

    @abstractmethod
    def modulate(self,baseband_signal):
        raise NotImplementedError("This method should be implemented by subclasses.")


class QuadraturModulator(Modulator):

    def modulate(self, baseband_obj: BasebandSignal):

        time_vector = np.arange(len(baseband_obj.data)) / baseband_obj.fs

        carrier_cos = np.cos( 2 * np.pi * time_vector * self.f_carrier)
        carrier_sin = np.sin( 2 * np.pi * time_vector * self.f_carrier)

        real_bb = np.real(baseband_obj.data)
        q_bb = np.imag(baseband_obj.data)

        mod_signal = np.square(2) * (real_bb * carrier_cos - q_bb * carrier_sin)

        return mod_signal







