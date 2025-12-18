'''
First Step: Get a Binary Sequence

Second Step: Mapping to Symbols

Third Step: Pulse Shaping

Fourth Step: Create the Transmit Signal in Baseband

Fifth Step: Create the Transmit Signal in Passband

'''

import numpy as np
from scipy import signal, fft
import matplotlib.pyplot as plt
import sounddevice as sd
from icecream import ic

# Application Logic (Processing)
from src.dataclasses.dataclass_models import ModSchemeLUT, PulseSignal, BasebandSignal, BandpassSignal


from src.constants import DEFAULT_FS, DEFAULT_SYM_RATE, DEFAULT_SPAN

# Application Logic (Processing)
from src.dataclasses.dataclass_models import ModSchemeLUT, PulseSignal, BasebandSignal
from src.constants import PulseShape, BitMappingScheme, ModulationScheme
from src.dataclasses.dataclass_models import BasebandSignal, BandpassSignal, BitStream, ModSchemeLUT, PulseSignal, SymbolStream
from src.modules.pulse_shapes import CosineSquarePulse, RectanglePulse, RaisedCosinePulse
from src.modules.bit_mapping import BinaryMapper, GrayMapper, RandomMapper
from src.modules.modulation_schemes import AmpShiftKeying
from src.modules.symbol_sequencer import SymbolSequencer
from src.modules.baseband_modulator import BasebandSignalGenerator
from src.modules.quadrature_modulator import QuadratureModulator
from src.modules.audio_player import AudioPlaybackHandler

# ===========================================================
#   No-Head Main.py
# ===========================================================


GLOBAL_FS = 48000
GLOBAL_SYM_RATE = 1
GLOBAL_SPAN = 2
GLOBAL_ROLL_OFF = 0.2
GLOBAL_SYMBOL_PERIOD = 1 / GLOBAL_SYM_RATE
GLOBAL_SPS = GLOBAL_FS // GLOBAL_SYM_RATE
GLOBAL_INTERPOLATION_FACTOR = 10
INTERNAL_FS = int(GLOBAL_FS / GLOBAL_INTERPOLATION_FACTOR)
INTERNAL_SPS = INTERNAL_FS // GLOBAL_SYM_RATE

def main():

    bit_stream = BitStream(
        name = "Bit Stream",
        data = np.array([1])
    )


    mapper = BinaryMapper()
    ask_lut = AmpShiftKeying(2,mapper).codebook

    mod_scheme = ModSchemeLUT(
        name=f"{ModulationScheme.ASK.name} LUT",
        data=None,
        look_up_table=ask_lut,
        cardinality = 2,
        mapper = "Binary",
        mod_scheme=ModulationScheme.ASK
        )

    symbol_sequencer = SymbolSequencer(mod_scheme)

    symbol_stream = symbol_sequencer.map_bits_to_symbols(bit_stream.data)

    carrier_freq = 440

    iq_modulator = QuadratureModulator(carrier_freq)

    # ===========================================================
    #   GLOBAL FS 48 kHz
    # ===========================================================

    pulse_shape_gen_global_fs = RectanglePulse(GLOBAL_SYM_RATE, GLOBAL_FS, GLOBAL_SPAN)

    pulse_signal_global_fs = PulseSignal(
        name= f"{PulseShape.RECTANGLE.name}_up",
        data=pulse_shape_gen_global_fs.generate(),
        fs = GLOBAL_FS,
        sym_rate = GLOBAL_SYM_RATE,
        shape=PulseShape.RECTANGLE.name,
        span=GLOBAL_SPAN,
        roll_off = None
        )

    bb_global_fs_gen = BasebandSignalGenerator(pulse_signal_global_fs)
    bb_global_fs_gen.generate_baseband_signal(symbol_stream)

    bb_global_fs = BasebandSignal (
        name = "Baseband_Global_FS",
        data = bb_global_fs_gen.generate_baseband_signal(symbol_stream),
        fs = GLOBAL_FS,
        sym_rate = GLOBAL_SYM_RATE,
        pulse = pulse_signal_global_fs,
        symbol_stream = symbol_stream
    )

    bandpass_global_fs = BandpassSignal (
        name = "Bandpass_Global_FS",
        data = iq_modulator.modulate(bb_global_fs),
        fs = GLOBAL_FS,
        sym_rate = GLOBAL_SYM_RATE,
        baseband_signal = bb_global_fs,
        carrier_freq = carrier_freq
    )


    # ===========================================================
    #   Linear Interpolation
    # ===========================================================

    pulse_shape_gen_internal_fs = RectanglePulse(GLOBAL_SYM_RATE, INTERNAL_FS, GLOBAL_SPAN)

    pulse_signal_internal_fs = PulseSignal(
        name= f"{PulseShape.RECTANGLE.name}_Internal FS",
        data=pulse_shape_gen_internal_fs.generate(),
        fs = INTERNAL_FS,
        sym_rate = GLOBAL_SYM_RATE,
        shape=PulseShape.RECTANGLE.name,
        span=GLOBAL_SPAN,
        roll_off = None
        )


    bb_generator_internal_fs = BasebandSignalGenerator(pulse_signal_internal_fs)

    bb_internal_fs_data = bb_generator_internal_fs.generate_baseband_signal(symbol_stream)

    fir_imp = signal.firwin(101, 1.0/GLOBAL_INTERPOLATION_FACTOR) * GLOBAL_INTERPOLATION_FACTOR

    interpolate_bb = signal.upfirdn(fir_imp, bb_internal_fs_data, up=GLOBAL_INTERPOLATION_FACTOR)

    delay = (len(fir_imp) - 1) // 2
    target_length = len(bb_global_fs.data)

    interpolate_bb = interpolate_bb[delay : delay + target_length]

    bb_internal_fs = BasebandSignal (
        name = "Baseband_Global_FS",
        data = interpolate_bb,
        fs = INTERNAL_FS,
        sym_rate = GLOBAL_SYM_RATE,
        pulse = pulse_signal_global_fs,
        symbol_stream = symbol_stream
    )


    # 3. Modulate the Interpolated signal to Passband
    # Now BOTH signals are at 48kHz and 440Hz carrier
    iq_modulator = QuadratureModulator(carrier_freq)
    interpolated_passband = iq_modulator.modulate(bb_internal_fs)

    bp_interpolated_fs = BandpassSignal (
        name = "Bandpass_Linear_Interpolated_FS",
        data = interpolated_passband,
        fs = GLOBAL_FS,
        sym_rate = GLOBAL_SYM_RATE,
        baseband_signal = bb_internal_fs,
        carrier_freq = carrier_freq
    )

    # ===========================================================
    #   Poly Interpolation
    # ===========================================================

    num_taps = 20 * GLOBAL_INTERPOLATION_FACTOR  # More taps for a sharper cutoff
    poly_filter = signal.firwin(
        num_taps + 1,
        1.0 / GLOBAL_INTERPOLATION_FACTOR,
        window='hamming'
        ) * GLOBAL_INTERPOLATION_FACTOR

    poly_bb_raw = signal.upfirdn(poly_filter, bb_internal_fs_data, up=GLOBAL_INTERPOLATION_FACTOR)


    # Create the Signal Object
    bb_poly_fs = BasebandSignal(
        name="Baseband_Polyphase_FS",
        data=poly_bb_raw,
        fs=GLOBAL_FS,
        sym_rate=GLOBAL_SYM_RATE,
        pulse=pulse_signal_global_fs,
        symbol_stream=symbol_stream
    )

    # Modulate to Passband
    interpolated_poly_passband = iq_modulator.modulate(bb_poly_fs)

    bp_poly_fs = BandpassSignal (
        name = "Bandpass_poly_FS",
        data = interpolated_poly_passband,
        fs = GLOBAL_FS,
        sym_rate = GLOBAL_SYM_RATE,
        baseband_signal = bb_internal_fs,
        carrier_freq = carrier_freq
    )

    # Create a figure with 3 vertical subplots, sharing the same X-axis
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    axes[0].plot(bandpass_global_fs.data, color='#2ca02c', label='Direct 48kHz')
    axes[0].set_title('Bandpass: Direct Global FS Generation (Reference)', fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(bp_interpolated_fs.data, color='#1f77b4', label='Standard FIR Interp')
    axes[1].set_title('Bandpass: Standard FIR Interpolation (Linear Approach)', fontweight='bold')
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(bp_poly_fs.data, color='#d62728', label='Polyphase Interp')
    axes[2].set_title('Bandpass: Polyphase Interpolation', fontweight='bold')
    axes[2].set_xlabel('Sample Index')
    axes[2].grid(True, alpha=0.3)

    # Add a general Y-axis label to the middle plot
    fig.text(0.04, 0.5, 'Amplitude', va='center', rotation='vertical', fontsize=12)

    # Global formatting
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()