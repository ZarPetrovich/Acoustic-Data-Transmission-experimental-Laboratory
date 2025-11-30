import sys, os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PySide6.QtCore import Slot


# Local Application/Library Specific Imports

from adtx_lab.src.ui.intro_dialog import *

# Application Constants & Logging
from adtx_lab.src.constants import PulseShape
from adtx_lab.src.logging.formatter import CustomFormatter

# Application Logic (Processing)
from adtx_lab.src.dataclasses.bitseq_models import SymbolSequence
from adtx_lab.src.dataclasses.signal_models import PulseSignal, BasebandSignal
from adtx_lab.src.baseband_modules.shape_generator import CosinePulse, RectanglePulse
from adtx_lab.src.bitmapping.symbol_modulation import AmpShiftKeying
from adtx_lab.src.baseband_modules.baseband_signal_generator import (
    BasebandSignalGenerator,
)
from adtx_lab.src.ui.widgets import ControlWidget, MatrixWidget, MetaDataWidget, MediaPlayerWidget, FooterWidget
from adtx_lab.src.ui.plot_strategies import PlotManager, PulsePlotStrategy, ConstellationPlotStrategy

class MainGUILogic(QMainWindow):
    def __init__(self, initial_values):
        # region
        super().__init__()
        self.setWindowTitle(f"ADTX Labor - Main FS: {initial_values['fs']} Hz | Sym Rate: {initial_values['sym_rate']} sps")
        self.resize(1200, 800)

        # --- 1. Initialize Values ----

        self.fs = initial_values["fs"]
        self.sym_rate = initial_values["sym_rate"]

        self.map_pulse_shape = {
            PulseShape.RECTANGLE: "Rectangle",
            PulseShape.COSINE_SQUARED: "Cosine",
        }

        self.saved_configs = [None] * 4 # 4 Empty slots
        self.selected_slot_index = 0

        self._setup_ui()
        self._setup_connections()

        # Init Pulse Plotter
        self.pulse_plotter = PlotManager(self.matrix_widget.plot_pulse)
        self.pulse_plotter.set_strategy(PulsePlotStrategy())


        self.current_pulse_signal = self._on_pulse_update
        #self.current_const_signal = self._init_active_const_signal()


    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        # Main Layout
        main_vbox = QVBoxLayout(central)

        # Top/Bottom split
        h_top = QHBoxLayout()
        h_btm = QHBoxLayout()

        # Instantiate Widgets
        self.ctrl_widget = ControlWidget(
            map_pulse_shape = self.map_pulse_shape)
        self.matrix_widget = MatrixWidget()
        self.meta_widget = MetaDataWidget()
        self.media_widget = MediaPlayerWidget()
        self.footer = FooterWidget() # Just a button wrapper

        # Layout Assembly
        h_top.addWidget(self.ctrl_widget, 33)
        h_top.addWidget(self.matrix_widget, 66)

        h_btm.addWidget(self.meta_widget, 33)
        h_btm.addWidget(self.media_widget, 66)

        main_vbox.addLayout(h_top, 75)
        main_vbox.addLayout(h_btm, 25)
        main_vbox.addWidget(self.footer)

        # Status Bar
        self.setStatusBar(QStatusBar())

    def _setup_connections(self):

        # 4. Footer
        self.footer.btn_restart.clicked.connect(self.restart_application)
        self.ctrl_widget.sig_pulse_changed.connect(self._on_pulse_update)

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

        self.pulse_plotter.update_plot(init_pulse_signal)

        return init_pulse_signal

    def _init_active_const_signal(self):
        ask_modulator = AmpShiftKeying(m=2)
        init_symbols = ask_modulator.generate(init_bits)

        init_const_signal = BasebandSignal(
            name="BPSK Signal",
            data=init_symbols,
            fs=self.fs,
            sym_rate=self.sym_rate,
            mod_scheme="BPSK",
            mapping="Gray"
        )

        return init_const_signal

    # --- Logic Handlers ---

    @Slot(dict)
    def _on_pulse_update(self, partial_data):
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

        # Update Plot
        self.pulse_plotter.update_plot(self.current_pulse_signal)

    @Slot(dict)
    def _on_mod_update(self, partial_data):
        pass

    @Slot(dict)
    def _on_iq_update(self, partial_data):
        pass


    @Slot(int)
    def _on_save_slot(self, slot_idx):
        # Deep copy current config to saved array
        self.saved_configs[slot_idx] = self.current_live_config.copy()
        self.statusBar().showMessage(f"Configuration saved to Slot {slot_idx + 1}", 3000)

    @Slot()
    def restart_application(self):
        QApplication.instance().quit()
        os.execl(sys.executable, sys.executable, *sys.argv)
from color_pallete import LIGHT_THEME
def load_stylesheet_with_palette(qss_path, palette):
    with open(qss_path, "r") as f:
        qss = f.read()
    for key, value in palette.items():
        qss = qss.replace(f"{{{{{key}}}}}", value)
    return qss

if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_app = MainGUILogic(initial_values={"fs": 48000, "sym_rate": 100})
    main_app.show()
    # Load and apply stylesheet with palette
    # qss = load_stylesheet_with_palette("style.qss", LIGHT_THEME)
    # app.setStyleSheet(qss)

    sys.exit(app.exec())