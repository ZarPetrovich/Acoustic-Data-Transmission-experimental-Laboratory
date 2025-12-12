import sys, os, argparse
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PySide6.QtCore import Slot

# Local Application/Library Specific Imports
from src.ui.intro_dialog import IntroDialog
from src.core.AppState import AppState
from src.constants import DEFAULT_FS, DEFAULT_SYM_RATE, DEFAULT_SPAN

# Application Logic (Processing)
from src.dataclasses.dataclass_models import ModSchemeLUT, PulseSignal, BasebandSignal, BandpassSignal

from src.ui.widgets import ControlWidget, MatrixWidget, MetaDataWidget, MediaPlayerWidget, FooterWidget
from src.ui.plot_strategies import (
    PlotManager, PulsePlotStrategy, ConstellationPlotStrategy,
    BasebandPlotStrategy, BandpassPlotStrategy, FFTPlotStrategy, PeriodogrammPlotStrategy)

from src.ui.style.color_pallete import LIGHT_THEME_HEX

# ===========================================================
#   GUI Constructor Logic
# ===========================================================

class MainGUILogic(QMainWindow):
    def __init__(self, initial_values):
        super().__init__()
        self.setWindowTitle(f"ADTX Labor - Main FS: {initial_values['fs']} Hz | Sym Rate: {initial_values['sym_rate']} sps")
        self.resize(1400, 900)

        # --- 1. Initialize UI Elements First ---
        self.ctrl_widget = ControlWidget()
        self.matrix_widget = MatrixWidget()
        self.meta_widget = MetaDataWidget()
        self.media_widget = MediaPlayerWidget()
        self.footer = FooterWidget(self)

        self._setup_ui()

        # --- 2. Init Plotters ---
        self.pulse_plotter = PlotManager(self.matrix_widget.plot_pulse)
        self.pulse_plotter.set_strategy(PulsePlotStrategy())

        self.const_plotter = PlotManager(self.matrix_widget.plot_const)
        self.const_plotter.set_strategy(ConstellationPlotStrategy())

        self.baseband_plotter = PlotManager(self.matrix_widget.plot_baseband)
        self.baseband_plotter.set_strategy(BasebandPlotStrategy())

        self.bb_fft_plotter = PlotManager(self.matrix_widget.plot_bb_fft)
        self.bb_fft_plotter.set_strategy(PeriodogrammPlotStrategy())

        self.bandpass_plotter = PlotManager(self.matrix_widget.plot_bandpass)
        self.bandpass_plotter.set_strategy(BandpassPlotStrategy())

        self.bp_fft_plotter = PlotManager(self.matrix_widget.plot_bp_fft)
        self.bp_fft_plotter.set_strategy(PeriodogrammPlotStrategy())


        # --- 3. Initialize AppState (which may emit signals) ---
        self.app_state = AppState(initial_values)

        self._setup_connections()
        # --- 4. Setup Connections ---

        # --- 5. Manually trigger initial UI updates ---
        self._on_app_config_update({"map_pulse_shape": self.app_state.map_pulse_shape})
        self._on_pulse_update(self.app_state.current_pulse_signal)
        self._on_mod_scheme_lut_update(self.app_state.current_mod_scheme)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        # Main Layout
        main_vbox = QVBoxLayout(central)

        # Top/Bottom split
        h_top = QHBoxLayout()
        h_btm = QHBoxLayout()

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
        # # ---- Connect control widget signals to app_state slots ----
        self.ctrl_widget.sig_pulse_changed.connect(self.app_state.on_pulse_update)
        self.ctrl_widget.sig_mod_changed.connect(self.app_state.on_mod_update)
        self.ctrl_widget.sig_bit_stream_changed.connect(self.app_state.on_bitseq_update)
        self.ctrl_widget.sig_carrier_freq_changed.connect(self.app_state.on_carrier_freq_update)
        self.ctrl_widget.sig_clear_plots.connect(self._clear_bitstream_plot)

        # ---- Connect Media Player widget signals to app_state slots ----

        self.media_widget.sig_play_button_pressed.connect(self.app_state.on_play_btn_pressed)
        self.media_widget.sig_stop_button_pressed.connect(self.app_state.on_stop_signal_pressed)

        # # ---- Connect app_state signals to GUI update slots ----
        self.app_state.sig_app_config_changed.connect(self._on_app_config_update)
        self.app_state.sig_pulse_changed.connect(self._on_pulse_update)
        self.app_state.sig_mod_lut_changed.connect(self._on_mod_scheme_lut_update)
        self.app_state.sig_baseband_changed.connect(self._on_baseband_update)
        self.app_state.sig_bandpass_changed.connect(self._on_bandpass_update)

        # # ---- Footer ----
        self.footer.btn_restart.clicked.connect(self.restart_application)

    @Slot(dict)
    def _on_app_config_update(self, config):
        self.ctrl_widget.set_pulse_shape_map(config["map_pulse_shape"])

    @Slot(PulseSignal)
    def _on_pulse_update(self, pulse_container):
        self.pulse_plotter.update_plot(pulse_container)

    @Slot(ModSchemeLUT)
    def _on_mod_scheme_lut_update(self, mod_scheme_container):
        self.const_plotter.update_plot(mod_scheme_container)

    @Slot(BasebandSignal)
    def _on_baseband_update(self, baseband_container):
        start = time.perf_counter()
        self.baseband_plotter.update_plot(baseband_container)
        self.bb_fft_plotter.update_plot(baseband_container)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"🎨 Baseband plots: {elapsed:.2f}ms")

    @Slot(BandpassSignal)
    def _on_bandpass_update(self, bandpass_container):
        start = time.perf_counter()
        self.bandpass_plotter.update_plot(bandpass_container)
        self.bp_fft_plotter.update_plot(bandpass_container)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"🎨 Bandpass plots: {elapsed:.2f}ms")

    @Slot()
    def restart_application(self):
        QApplication.instance().quit()
        # Add the --no-intro flag to the arguments when restarting
        # We can remove the explicit --no-intro flag now, as argparse handles it
        os.execl(sys.executable, sys.executable, *sys.argv)

    @Slot()
    def _clear_bitstream_plot(self):
        # Clear visual plots
        self.baseband_plotter.clear_plot()
        self.bb_fft_plotter.clear_plot()
        self.bandpass_plotter.clear_plot()
        self.bp_fft_plotter.clear_plot()

        # Clear underlying data to prevent memory leaks
        self.app_state.clear_signals()

        # Clear bitstream entry
        self.ctrl_widget.clear_bitstream_entry()

        self.statusBar().showMessage("All signals and data cleared", 3000)

#------------------------------------------------------------
# +++++ Stylesheet loader (if needed) +++++
#------------------------------------------------------------
def load_stylesheet_with_palette(qss_path, palette):
    with open(qss_path, "r") as f:
        qss = f.read()
    for key, value in palette.items():
        qss = qss.replace(f"{{{{{key}}}}}", value)
    return qss

def get_resource_path(relative_path):
    """
    Get the absolute path to a resource, works for development and for
    PyInstaller/cx_Freeze compiled executables.
    """
    # Check if the app is frozen (e.g., by PyInstaller)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # In a frozen environment, the base path is sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # In development, the base path is the directory of the script
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


#------------------------------------------------------------
# +++++ Main Loop +++++
#------------------------------------------------------------
def main():


    parser = argparse.ArgumentParser(description="ADTx Laboratory")
    parser.add_argument('--no-intro', action='store_true', help='Skip the intro dialog and use default values.')
    parser.add_argument('--fs', type=int, default=DEFAULT_FS, help='Set the sample rate in Hz.')
    parser.add_argument('--sym-rate', type=int, default=DEFAULT_SYM_RATE, help='Set the symbol rate in sps.')
    parser.add_argument('--span', type = int, default = DEFAULT_SPAN, help="Set the pulse span as integer.")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    initial_values = {"fs": args.fs, "sym_rate": args.sym_rate, "span": args.span}

    # Load and apply the stylesheet with the color palette
    qss_path = get_resource_path("src/ui/style/style.qss")
    stylesheet = load_stylesheet_with_palette(qss_path, LIGHT_THEME_HEX)


    if not args.no_intro:
        intro_dialog = IntroDialog(initial_values=initial_values)
        intro_dialog.setStyleSheet(stylesheet)
        if intro_dialog.exec():
            updated_values = intro_dialog.get_values()
            # Ensure 'span' is preserved if not explicitly updated
            initial_values.update(updated_values)
        else:
            sys.exit()  # ! Exit if the user cancels the dialog

    app.setStyleSheet(stylesheet)
    main_app = MainGUILogic(initial_values=initial_values)
    main_app.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
