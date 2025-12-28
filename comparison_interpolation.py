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
from matplotlib.widgets import Slider
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
    # region INIT
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
    # endregion
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
    #   Bandlimited Interpolation with not splitting the FIR Filter
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

    #------------------------------------------------------------
    # +++++ Apply Filter +++++
    #------------------------------------------------------------

    taps = 101
    f_c = 1.0 / GLOBAL_INTERPOLATION_FACTOR


    fir_imp = signal.firwin(taps, f_c, window = ('kaiser', 8.0)) * GLOBAL_INTERPOLATION_FACTOR

    interpolate_bb = signal.upfirdn(fir_imp, bb_internal_fs_data, up=GLOBAL_INTERPOLATION_FACTOR)

    #------------------------------------------------------------
    # +++++ Perform Group Delay +++++
    #------------------------------------------------------------

    delay = (len(fir_imp) - 1) // 2
    target_length = len(bb_global_fs.data)

    interpolate_bb = interpolate_bb[delay : delay + target_length]

    bb_internal_fs = BasebandSignal (
        name = "Baseband_Global_FS",
        data = interpolate_bb,
        fs = GLOBAL_FS,
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
    #   Bandlimited Interpolation with splitting the FIR Filter
    # ===========================================================

    num_taps = GLOBAL_INTERPOLATION_FACTOR  # More taps for a sharper cutoff
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



    def get_error(ref, test):
        min_len = min(len(ref), len(test))
        return ref[:min_len] - test[:min_len]


    error_linear = get_error(bandpass_global_fs.data, bp_interpolated_fs.data)
    error_poly = get_error(bandpass_global_fs.data, bp_poly_fs.data)

    def plot_interactive_signals(global_sig, interp_sig, poly_sig):
        fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
        plt.subplots_adjust(bottom=0.25) # Extra room for two sliders

        # Plot data
        l0, = axes[0].plot(global_sig.data, color='#2ca02c')
        l1, = axes[1].plot(interp_sig.data, color='#1f77b4')
        l2, = axes[2].plot(poly_sig.data, color='#d62728')

        titles = ['Direct Global FS', 'Standard FIR Interp', 'Polyphase Interp']
        for ax, title in zip(axes, titles):
            ax.set_title(title, fontweight='bold')
            ax.grid(True, alpha=0.3)

        total_samples = len(global_sig.data)

        # THE ERROR PANEL
        axes[3].plot(error_linear, color='blue', alpha=0.5, label='Linear Error')
        axes[3].plot(error_poly, color='red', alpha=0.5, label='Polyphase Error')
        axes[3].set_title('Residual Error (Reference - Test)', fontweight='bold', color='darkred')
        axes[3].legend()

        # --- Slider Configuration ---
        ax_pos = plt.axes([0.2, 0.1, 0.6, 0.03])    # Position (Scroll)
        ax_zoom = plt.axes([0.2, 0.05, 0.6, 0.03])   # Width (Zoom)

        s_pos = Slider(ax_pos, 'Scroll', 0, total_samples, valinit=total_samples//2)
        s_zoom = Slider(ax_zoom, 'Zoom', 100, total_samples, valinit=total_samples)

        def update(val):
            width = s_zoom.val
            pos = s_pos.val

            # Calculate window limits
            left = max(0, pos - width // 2)
            right = min(total_samples, pos + width // 2)

            axes[0].set_xlim(left, right)
            fig.canvas.draw_idle()

        s_pos.on_changed(update)
        s_zoom.on_changed(update)

        plt.show()

    plot_interactive_signals(bandpass_global_fs, bp_interpolated_fs, bp_poly_fs)



    # --- Frequency Analysis Plot ---
    fig_fft, axes_fft = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
    plt.subplots_adjust(bottom=0.2)

    def plot_fft(ax, signal, fs, color, label):
        N = len(signal)
        freq = np.fft.rfftfreq(N, d=1/fs)
        spectrum = np.abs(np.fft.rfft(signal))
        ax.plot(freq, spectrum, color=color, label=label)
        ax.set_ylabel('Magnitude')
        ax.legend()
        ax.grid(True, alpha=0.2)
        print(f"Max Magnitude Freq: {freq[np.argmax(spectrum)]} Hz")


    # FFT of signals

    plot_fft(axes_fft[0], bandpass_global_fs.data, bandpass_global_fs.fs, 'green', 'Reference')
    axes_fft[0].set_title('FFT: Direct Global FS', fontweight='bold')

    plot_fft(axes_fft[1], bp_interpolated_fs.data, bp_interpolated_fs.fs, 'tab:blue', 'Linear')
    axes_fft[1].set_title('FFT: Standard FIR (Linear)', fontweight='bold')

    plot_fft(axes_fft[2], bp_poly_fs.data, bp_poly_fs.fs, 'tab:red', 'Polyphase')
    axes_fft[2].set_title('FFT: Polyphase Interp', fontweight='bold')

    plt.show()

if __name__ == '__main__':
    main()