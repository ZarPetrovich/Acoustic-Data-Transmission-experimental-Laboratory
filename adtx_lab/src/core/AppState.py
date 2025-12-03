from PySide6.QtCore import QObject, Signal
from adtx_lab.src.constants import PulseShape, PULSE_SHAPE_MAP, BitMappingScheme, ModulationScheme
from adtx_lab.src.dataclasses.metadata_models import BasebandSignal, BitStream, ModSchemeLUT, PulseSignal, SymbolStream
from adtx_lab.src.modules.pulse_shapes import CosinePulse, RectanglePulse
from adtx_lab.src.modules.bit_mapping import BinaryMapper, GrayMapper, RandomMapper
from adtx_lab.src.modules.modulation_schemes import AmpShiftKeying
from adtx_lab.src.modules.baseband_modulator import BasebandSignalGenerator


class AppState(QObject):
    """
    Manages the application's state and business logic.
    """
    # Signals to notify the GUI of state changes
    app_config_changed = Signal(dict)
    pulse_signal_changed = Signal(PulseSignal)
    modulation_lut_changed = Signal(ModSchemeLUT)
    baseband_signal_changed = Signal(BasebandSignal)

    def __init__(self, initial_values):
        super().__init__()

        self.fs = initial_values["fs"]
        self.sym_rate = initial_values["sym_rate"]
        self.span = initial_values.get("span")

        self.map_pulse_shape = PULSE_SHAPE_MAP

        # TODO Implement Save Slot Logic
        self.saved_configs = [None] * 4  #  4 Empty slots
        self.selected_slot_index = 0


        # Initialize current Interactive Signals
        self.current_pulse_signal: PulseSignal
        self.current_mod_scheme: ModSchemeLUT = self._init_default_mod_scheme()
        self.current_bitstream: BitStream
        self.current_symbol_stream: SymbolStream
        self.current_baseband_signal: BasebandSignal

        self.app_config_changed.emit({"map_pulse_shape": self.map_pulse_shape})



    def on_pulse_update(self, partial_data):

        pulse_type = partial_data.get("pulse_type", PulseShape.RECTANGLE)
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


    def _init_default_mod_scheme(self):


        mapper = BinaryMapper()


        lut_data = AmpShiftKeying(2, mapper=mapper).codebook

        self.current_mod_scheme = ModSchemeLUT(
            name=f"2-ASK LUT",
            data=None,
            look_up_table=lut_data,
            mapper = "Binary",
            mod_scheme="2-ASK",
        )

        self.modulation_lut_changed.emit(self.current_mod_scheme)
    def on_mod_update(self, partial_data):

        sel_mod_scheme = partial_data.get("mod_scheme", "2-ASK")
        sel_mapper = partial_data.get("bit_mapping", "Binary")

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
            mapper = sel_mapper,
            mod_scheme=sel_mod_scheme,
        )

        self.modulation_lut_changed.emit(self.current_mod_scheme)

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
            pulse = self.current_pulse_signal,
            symbol_stream = bit_seq,
            sym_name = self.current_sym_signal.name
        )
        self.baseband_signal_changed.emit(self.active_baseband_signal)

    def on_save_slot(self, slot_idx):
        # Deep copy current config to saved array
        self.saved_configs[slot_idx] = self.current_live_config.copy()
        # This should be handled by the GUI
        # self.statusBar().showMessage(f"Configuration saved to Slot {slot_idx + 1}", 3000)
