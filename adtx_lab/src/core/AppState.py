from PySide6.QtCore import QObject, Signal
from adtx_lab.src.constants import PulseShape, PULSE_SHAPE_MAP
from adtx_lab.src.dataclasses.models import SymbolSequence, PulseSignal, BasebandSignal
from adtx_lab.src.modules.shape_generator import CosinePulse, RectanglePulse
from adtx_lab.src.modules.bitmapper import BinaryMapper, GrayMapper, RandomMapper
from adtx_lab.src.modules.symbol_modulation import AmpShiftKeying
from adtx_lab.src.modules.baseband_signal_generator import (
    BasebandSignalGenerator,
)

class AppState(QObject):
    """
    Manages the application's state and business logic.
    """
    # Signals to notify the GUI of state changes
    app_config_changed = Signal(dict)
    pulse_signal_changed = Signal(PulseSignal)
    symbol_sequence_changed = Signal(SymbolSequence)
    baseband_signal_changed = Signal(BasebandSignal)

    def __init__(self, fs, sym_rate):
        super().__init__()

        self.fs = fs
        self.sym_rate = sym_rate

        self.map_pulse_shape = PULSE_SHAPE_MAP

        self.saved_configs = [None] * 4  # 4 Empty slots
        self.selected_slot_index = 0

        # Initialize Active Signals
        self.active_const_gen_object = AmpShiftKeying(2, mapper=BinaryMapper())
        self.current_pulse_signal = self._init_active_pulse()
        self.current_sym_signal = self._init_active_sym_const_signal()
        self.active_baseband_signal = None

        self.app_config_changed.emit({"map_pulse_shape": self.map_pulse_shape})


    def _init_active_pulse(self):

        init_rect_pulse_obj = RectanglePulse(self.sym_rate, self.fs, span = 2)
        init_rect_data = init_rect_pulse_obj.generate()

        init_pulse_signal = PulseSignal(
            name="Rectangular Pulse",
            data=init_rect_data,
            fs = self.fs,
            sym_rate = self.sym_rate,
            shape = PulseShape.RECTANGLE,
            span = 2
        )
        self.pulse_signal_changed.emit(init_pulse_signal)
        return init_pulse_signal

    def _init_active_sym_const_signal(self):

        two_ask_object = AmpShiftKeying(2, mapper=BinaryMapper())

        look_up_data = two_ask_object.codebook

        init_symbol_seq = SymbolSequence(
            name="2-ASK Symbols",
            data=None,
            look_up_table = look_up_data,
            mod_scheme = "2-ASK"
        )
        self.symbol_sequence_changed.emit(init_symbol_seq)
        return init_symbol_seq

    def on_pulse_update(self, partial_data):
        pulse_type = partial_data.get("pulse_type")
        span = partial_data.get("span", 2)
        roll_off = partial_data.get("roll_off", 0.0)

        if isinstance(pulse_type, str):
            for enum_val, label in self.map_pulse_shape.items():
                if label == pulse_type:
                    pulse_type = enum_val
                    break
            if pulse_type == PulseShape.RECTANGLE:
                pulse_obj = RectanglePulse(self.sym_rate, self.fs, span)
            elif pulse_type == PulseShape.COSINE_SQUARED:
                pulse_obj = CosinePulse(self.sym_rate, self.fs, span)
            else:
                raise ValueError(f"Unsupported pulse type: {pulse_type}")

        pulse_data = pulse_obj.generate()

        # Update current pulse signal
        self.current_pulse_signal = PulseSignal(
            name=f"{pulse_type} Pulse",
            data=pulse_data,
            fs=self.fs,
            sym_rate=self.sym_rate,
            shape=pulse_type,
            span=span
        )
        self.pulse_signal_changed.emit(self.current_pulse_signal)

    def on_mod_update(self, partial_data):

        sel_mod_scheme = partial_data.get("mod_scheme")
        sel_mapper = partial_data.get("bit_mapping")

        if isinstance(sel_mapper, str):
            if sel_mapper == "Binary":
                mapper = BinaryMapper()
            elif sel_mapper == "Gray":
                mapper = GrayMapper()
            elif sel_mapper == "Random":
                mapper = RandomMapper()
            else:
                raise ValueError(f"Unsupported bit mapping: {sel_mapper}")

        if isinstance(sel_mod_scheme, str):
            if sel_mod_scheme == "2-ASK":
                look_up_data = AmpShiftKeying(2, mapper=mapper).codebook
            elif sel_mod_scheme == "4-ASK":
                look_up_data = AmpShiftKeying(4, mapper=mapper).codebook
            elif sel_mod_scheme == "8-ASK":
                look_up_data = AmpShiftKeying(8, mapper=mapper).codebook
            else:
                raise ValueError(f"Unsupported modulation scheme: {sel_mod_scheme}")

        self.active_const_gen_object = AmpShiftKeying(int(sel_mod_scheme.split('-')[0]), mapper=mapper)

        self.current_sym_signal = SymbolSequence(
            name=f"{sel_mod_scheme} Symbols",
            data=None,
            look_up_table=look_up_data,
            mod_scheme=sel_mod_scheme
        )
        self.symbol_sequence_changed.emit(self.current_sym_signal)

    def on_bitseq_update(self, partial_data):
        bit_seq = partial_data.get("bit_seq")

        # Init Baseband generator with active Pulse Object
        baseband_gen_obj = BasebandSignalGenerator(self.current_pulse_signal)

        # Create Symbal Sequence with active Modulator
        symbol_seq = self.active_const_gen_object.generate(bit_seq)

        self.current_sym_signal.data = symbol_seq

        # Generate Baseband Signal

        bb_data = baseband_gen_obj.generate_baseband_signal(self.current_sym_signal)

        self.active_baseband_signal = BasebandSignal (
            name = "Active Baseband Signal",
            data = bb_data,
            fs = self.fs,
            sym_rate = self.sym_rate,
            pulse_name = self.current_pulse_signal.name,
            bit_seq = bit_seq,
            sym_name = self.current_sym_signal.name
        )
        self.baseband_signal_changed.emit(self.active_baseband_signal)

    def on_save_slot(self, slot_idx):
        # Deep copy current config to saved array
        self.saved_configs[slot_idx] = self.current_live_config.copy()
        # This should be handled by the GUI
        # self.statusBar().showMessage(f"Configuration saved to Slot {slot_idx + 1}", 3000)
