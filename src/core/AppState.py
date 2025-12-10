from PySide6.QtCore import QObject, Signal, QTimer, Slot
import numpy as np

from src.constants import PulseShape, PULSE_SHAPE_MAP
from src.dataclasses.dataclass_models import BasebandSignal, BandpassSignal, BitStream, ModSchemeLUT, PulseSignal, SymbolStream
from src.modules.pulse_shapes import CosineSquarePulse, RectanglePulse, RaisedCosinePulse
from src.modules.bit_mapping import BinaryMapper, GrayMapper, RandomMapper
from src.modules.modulation_schemes import AmpShiftKeying
from src.modules.symbol_sequencer import SymbolSequencer
from src.modules.baseband_modulator import BasebandSignalGenerator
from src.modules.iq_modulator import QuadratureModulator
from src.modules.audio_player import AudioPlaybackHandler


class AppState(QObject):
    """
    Manages the application's state and business logic.
    """
    # Signals to notify the GUI of state changes
    app_config_changed = Signal(dict)
    pulse_signal_changed = Signal(PulseSignal)
    modulation_lut_changed = Signal(ModSchemeLUT)
    baseband_signal_changed = Signal(BasebandSignal)
    bandpass_signal_changed = Signal(BandpassSignal)


    playback_status_changed = Signal(str)
    start_audio_playback = Signal()
    stop_audio_playback = Signal()

    def __init__(self, initial_values):
        super().__init__()

        self.fs = initial_values["fs"]
        self.sym_rate = initial_values["sym_rate"]
        self.span = initial_values.get("span")

        self.audio_handler = AudioPlaybackHandler()
        # Connect audio handler feedback signals to AppState slots
        self.audio_handler.playback_started.connect(self._on_playback_started)
        self.audio_handler.playback_finished.connect(self._on_playback_finished)
        self.audio_handler.playback_error.connect(self._on_playback_error)

        self.map_pulse_shape = PULSE_SHAPE_MAP # TODO Maybe move into INIT VALUE somehow

        # TODO Implement Save Slot Logic
        self.saved_configs = [None] * 4  #  4 Empty slots
        self.selected_slot_index = 0


        # Initialize current Interactive Signals
        self.current_pulse_signal: PulseSignal = self._init_default_pulse()
        self.current_mod_scheme: ModSchemeLUT = self._init_default_mod_scheme()
        self.current_bitstream: BitStream
        self.current_symbol_stream: SymbolStream
        self.current_baseband_signal: BasebandSignal
        self.current_bandpass_signal: BandpassSignal

        self.app_config_changed.emit({"map_pulse_shape": self.map_pulse_shape})

    def _init_default_pulse(self):

        init_two_ask = RectanglePulse(self.sym_rate, self.fs, self.span, roll_off = None)

        pulse_data = init_two_ask.generate() # generate the actual Data

        # Update current pulse signal
        self.current_pulse_signal = PulseSignal(
            name=f"Rectangle Pulse",
            data=pulse_data,
            fs=self.fs,
            sym_rate=self.sym_rate,
            shape=PulseShape.RECTANGLE,
            span=self.span
        )

        self.pulse_signal_changed.emit(self.current_pulse_signal)
        return self.current_pulse_signal

    def _init_default_mod_scheme(self):

        mapper = BinaryMapper()

        lut_data = AmpShiftKeying(2, mapper=mapper).codebook

        self.current_mod_scheme = ModSchemeLUT(
            name=f"2-ASK LUT",
            data=None,
            look_up_table=lut_data,
            cardinality = 2,
            mapper = "Binary",
            mod_scheme="2-ASK",
        )
        print("INIT MOD SCHEM LUT")
        self.modulation_lut_changed.emit(self.current_mod_scheme)

        return self.current_mod_scheme

    def on_pulse_update(self, partial_data):
        pulse_type = partial_data.get("pulse_type")
        span = partial_data.get("span")
        roll_off = partial_data.get("roll_off", 0.0)  # Default roll-off to 0.0 if not provided

        if pulse_type is None or span is None:
            print("Missing required pulse parameters: 'pulse_type' or 'span'")
            return

        pulse_generators = {
            PulseShape.RECTANGLE: RectanglePulse,
            PulseShape.COSINE_SQUARED: CosineSquarePulse,
            PulseShape.RAISED_COSINE: RaisedCosinePulse,
        }

        # Validate if shape is available
        generator_cls = pulse_generators.get(pulse_type)
        if not generator_cls:
            print(f"Unknown Pulse Shape: {pulse_type}")
            return

        # Create Generator Object
        try:
            generator = generator_cls(self.sym_rate, self.fs, span, roll_off)
            pulse_data = generator.generate()  # Generate the actual data
        except Exception as e:
            print(f"Failed to generate pulse: {e}")
            return

        # Update current pulse signal
        self.current_pulse_signal = PulseSignal(
            name=f"{pulse_type} Pulse",
            data=pulse_data,
            fs=self.fs,
            sym_rate=self.sym_rate,
            shape=pulse_type,
            span=span
        )

        # Emit signal to notify GUI
        self.pulse_signal_changed.emit(self.current_pulse_signal)

        try:
            if isinstance(self.current_symbol_stream, SymbolStream):
                self.update_baseband_signal()
        except:
            pass

    def on_mod_update(self, partial_data):

        sel_mod_scheme = partial_data.get("mod_scheme")
        sel_mapper = partial_data.get("bit_mapping")

        if sel_mapper == "Binary":
            mapper = BinaryMapper()
        elif sel_mapper == "Gray":
            mapper = GrayMapper()
        elif sel_mapper == "Random":
            mapper = RandomMapper()
        else:
            raise ValueError(f"Unsupported bit mapping: {sel_mapper}")

        if sel_mod_scheme == "2-ASK":
            lut_data = AmpShiftKeying(2, mapper=mapper).codebook
        elif sel_mod_scheme == "4-ASK":
            lut_data = AmpShiftKeying(4, mapper=mapper).codebook
        elif sel_mod_scheme == "8-ASK":
            lut_data = AmpShiftKeying(8, mapper=mapper).codebook
        else:
            raise ValueError(f"Unsupported modulation scheme: {sel_mod_scheme}")

        self.current_mod_scheme = ModSchemeLUT(
            name=f"{sel_mod_scheme} LUT",
            data=None,
            look_up_table=lut_data,
            cardinality = int(sel_mod_scheme.split("-")[0]),
            mapper = sel_mapper,
            mod_scheme=sel_mod_scheme,
        )

        self.modulation_lut_changed.emit(self.current_mod_scheme)

        if hasattr(self, 'current_bitstream'):
            self.update_symbol_stream()

    def on_bitseq_update(self, partial_data):
        bit_stream_str = partial_data.get("bit_seq")

        if not bit_stream_str:
            self.current_bitstream = BitStream(name="Empty Bit Stream", data=np.array([], dtype=np.int8))
            return

        try:
            # Convert String into Numpy Array full of Int
            bit_stream_arr = np.array([int(char) for char in bit_stream_str], dtype=np.int8)
        except (ValueError, TypeError):
            # Handle cases where the string is not valid for conversion
            print(f"Invalid characters in bit sequence: {bit_stream_str}")
            return

        self.current_bitstream = BitStream(
            name="Current Bit Stream",
            data=bit_stream_arr
        )

        # Trigger the update chain
        self.update_symbol_stream()

    def update_symbol_stream(self):
        """Generates a new symbol stream and triggers a baseband signal update."""

        if not hasattr(self, 'current_bitstream') or self.current_bitstream.data is None:
            return

        # Create Symbol Sequence with Symbol Sequencer Module
        symbol_stream_data = SymbolSequencer(self.current_mod_scheme).generate(self.current_bitstream.data)

        self.current_symbol_stream = SymbolStream(
            name="Current Symbol Stream",
            data=symbol_stream_data,
            mod_scheme=self.current_mod_scheme,
            bit_stream=self.current_bitstream
        )

        # Automatically update the baseband signal after the symbol stream is updated
        self.update_baseband_signal()

    def update_baseband_signal(self):
        """Generates a new baseband signal."""
        if not hasattr(self, 'current_symbol_stream') or not hasattr(self, 'current_pulse_signal'):
            return

        # Init Baseband generator with active Pulse Object
        baseband_gen_obj = BasebandSignalGenerator(self.current_pulse_signal)

        # Generate Baseband Signal
        bb_data = baseband_gen_obj.generate_baseband_signal(self.current_symbol_stream)

        self.current_baseband_signal = BasebandSignal (
            name = "Current Baseband Signal",
            data = bb_data,
            fs = self.fs,
            sym_rate = self.sym_rate,
            pulse = self.current_pulse_signal,
            symbol_stream = self.current_symbol_stream
        )

        self.baseband_signal_changed.emit(self.current_baseband_signal)

    def on_carrier_freq_update(self, partial_data):

        carrier_freq = partial_data.get("carrier_freq")
        if carrier_freq is None:
            print("Carrier frequency is missing in the provided data.")
            return
        try:
            carrier_freq = int(carrier_freq)
        except ValueError:
            print(f"Invalid carrier frequency value: {carrier_freq}")
            return

        iq_data = QuadratureModulator(carrier_freq).modulate(self.current_baseband_signal)

        self.current_bandpass_signal = BandpassSignal (
            name = "Current Bandpass Signal",
            data = iq_data,
            fs = self.fs,
            sym_rate = self.sym_rate,
            baseband_signal = self.current_baseband_signal,
            carrier_freq = carrier_freq
        )
        self.bandpass_signal_changed.emit(self.current_bandpass_signal)

    def play_audio(self):
        """
        Plays the real part of the current bandpass signal if it exists.
        """
        if hasattr(self, 'current_bandpass_signal') and self.current_bandpass_signal.data is not None:
            # Audio hardware typically plays real-valued signals.
            # We take the real part of the complex bandpass signal.
            audio_data = np.real(self.current_bandpass_signal.data)
            self.audio_handler.play(audio_data, self.fs)
        else:
            self.playback_status_changed.emit("Error: No signal generated to play.")
            print("No bandpass signal available to play.")

    def on_save_slot(self, slot_idx):
        self.saved_configs[slot_idx] = self.current_baseband_signal

    @Slot()
    def on_play_btn_pressed(self):
        """ Slot to be connected to the UI's play button. """
        self.play_audio()

    @Slot()
    def on_stop_signal_pressed(self):
        """ Slot to be connected to the UI's stop button. """
        self.audio_handler.stop()

    # --- Audio Handler Feedback Slots ---
    @Slot()
    def _on_playback_started(self):
        self.playback_status_changed.emit("Status: Playing...")

    @Slot()
    def _on_playback_finished(self):
        self.playback_status_changed.emit("Status: Idle")

    @Slot(str)
    def _on_playback_error(self, error_message):
        self.playback_status_changed.emit(f"Error: {error_message}")