from scipy import signal
import numpy as np

from src.dataclasses.dataclass_models import BasebandModel

class PulseFilter:


    def __init__(self,interpolation_factor):

        self.L = interpolation_factor
        self.cutoff_frequency = 1.0 / interpolation_factor
        self.taps = interpolation_factor * 10 + 1 # uneven | 10 is something like taps per phase
        self.group_delay = self.taps - 1 // 2

        self.imp_response = self._create_filter_imp_response()


    def _create_filter_imp_response(self):

        imp_response = signal.firwin(numtaps = self.taps,
                                   cutoff = self.cutoff_frequency,
                                   window = ('kaiser', 4.0)
                                   ) * self.L
        return imp_response

    def upscale(self, bandpass_signal: BasebandModel):

        interpolate_bb = signal.upfirdn(
            h= self.imp_response,
            x = bandpass_signal.data,
            up =self.L
            )

        return interpolate_bb







    # taps, f_c = 101, 1.0 / GLOBAL_INTERPOLATION_FACTOR
    # fir_imp = signal.firwin(taps, f_c) * GLOBAL_INTERPOLATION_FACTOR

    # interpolate_bb = signal.upfirdn(fir_imp, bb_internal_fs_data, up=GLOBAL_INTERPOLATION_FACTOR)