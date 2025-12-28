import sys
import os
import argparse
import time

# --- Third-Party Libraries ---
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PySide6.QtCore import Slot

# --- Internal: Constants & Dataclasses ---
from src.constants import DEFAULT_FS, DEFAULT_SYM_RATE, DEFAULT_SPAN
from src.dataclasses.dataclass_models import (
    ModSchemeLUT, PulseSignal, BasebandSignal, BandpassSignal
)

# --- Internal: Core Logic ---
from src.core.AppState import AppState

# --- Internal: UI Components ---
from src.ui.intro_dialog import IntroDialog
from src.ui.footer_widget import FooterWidget
from src.ui.ctrl_widgets.main_controls import ControlWidget
from src.ui.plots.signal_matrix_view import SignalMatrixView

# --- Internal: Plotting Strategies ---
from src.ui.plots.strategies import (
    PlotManager, PulsePlotStrategy, ConstellationPlotStrategy,
    BasebandPlotStrategy, BandpassPlotStrategy, FFTPlotStrategy,
    PeriodogrammPlotStrategy, SpectogramPlotStrategy, FrequencyResponse
)

# --- Internal: Styling ---
from src.ui.style.color_pallete import LIGHT_THEME_HEX
# ===========================================================
#   GUI Constructor Logic
# ===========================================================

class MainGUILogic(QMainWindow):
    def __init__(self, initial_values):
        super().__init__()
        self.setWindowTitle(f"ADTX Labor Sym Rate: {initial_values['sym_rate']} baud")
        self.resize(1600, 900)

        # --- 1. Initialize UI Elements First ---
        #self.ctrl_widget = ControlWidget()
        self.ctrl_widget = ControlWidget()
        self.matrix_widget = SignalMatrixView()
        #self.meta_widget = MetaDataWidget()
        #self.media_widget = MediaPlayerWidget()
        self.footer = FooterWidget(self)

        self._setup_ui()

        # region Init PLOTS
        # ---- Init Pulse Tab View Plot Manager ----
        self.pulse_time_plotter = PlotManager(self.matrix_widget.plot_pulse.plot_time)
        self.pulse_time_plotter.set_strategy(PulsePlotStrategy())

        self.pulse_fft_plotter = PlotManager(self.matrix_widget.plot_pulse.plot_fft)
        self.pulse_fft_plotter.set_strategy(FFTPlotStrategy())

        #self.pulse_periodogram_plotter = PlotManager(self.matrix_widget.plot_pulse.plot_imp_response)
        #self.pulse_periodogram_plotter.set_strategy(FrequencyResponse())

        # ---- Init Constellation Diagramm ----
        self.const_plotter = PlotManager(self.matrix_widget.plot_const)
        self.const_plotter.set_strategy(ConstellationPlotStrategy())

        # ---- Init Time Plot Baseband ----
        self.baseband_plotter = PlotManager(self.matrix_widget.plot_baseband)
        self.baseband_plotter.set_strategy(BasebandPlotStrategy())


        # ---- Init Baseband Spectrums ----
        self.bb_spectrogram_plotter = PlotManager(self.matrix_widget.bb_spectrum_container.plot_spectrogram)
        self.bb_spectrogram_plotter.set_strategy(SpectogramPlotStrategy())

        #self.bb_periodogram_plotter = PlotManager(self.matrix_widget.bb_spectrum_container.plot_periodogram)
        #self.bb_periodogram_plotter.set_strategy(PeriodogrammPlotStrategy())

        self.bb_fft_plotter = PlotManager(self.matrix_widget.bb_spectrum_container.plot_fft)
        self.bb_fft_plotter.set_strategy(FFTPlotStrategy())

        # ---- Init Time Bandpass Plotter ----
        self.bandpass_plotter = PlotManager(self.matrix_widget.plot_bandpass)
        self.bandpass_plotter.set_strategy(BandpassPlotStrategy())

        # ---- Init Bandpass Spectrums ----
        self.bp_spectrogram_plotter = PlotManager(self.matrix_widget.bp_spectrum_container.plot_spectrogram)
        self.bp_spectrogram_plotter.set_strategy(SpectogramPlotStrategy())

        # self.bp_periodogram_plotter = PlotManager(self.matrix_widget.bp_spectrum_container.plot_periodogram)
        # self.bp_periodogram_plotter.set_strategy(PeriodogrammPlotStrategy())

        self.bp_fft_plotter = PlotManager(self.matrix_widget.bp_spectrum_container.plot_fft)
        self.bp_fft_plotter.set_strategy(FFTPlotStrategy())
        # endregion

        # --- 3. Initialize AppState (which may emit signals) ---
        self.app_state = AppState(initial_values)

        self._setup_connections()

        # --- 5. Manually trigger initial UI updates ---
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
        h_top.addWidget(self.ctrl_widget, 30)
        h_top.addWidget(self.matrix_widget, 70)

        #h_btm.addWidget(self.meta_widget, 33)
        #h_btm.addWidget(self.media_widget, 66)

        main_vbox.addLayout(h_top, 100)
        main_vbox.addLayout(h_btm,0)
        main_vbox.addWidget(self.footer)

        # Status Bar
        self.setStatusBar(QStatusBar())

    def _setup_connections(self):
        # # ---- Connect control widget signals to app_state slots ----
        #self.ctrl_widget.sig_pulse_changed.connect(self.app_state.on_pulse_update)

        # self.ctrl_widget.sig_mod_changed.connect(self.app_state.on_mod_update)
        # self.ctrl_widget.sig_bit_stream_changed.connect(self.app_state.on_bitseq_update)
        # self.ctrl_widget.sig_carrier_freq_changed.connect(self.app_state.on_carrier_freq_update)
        # self.ctrl_widget.sig_clear_plots.connect(self._clear_bitstream_plot)
        # self.ctrl_widget.sig_export_pulse_path.connect(self.app_state.on_export_pulse)

        # ---- Connect Media Player widget signals to app_state slots ----

        # self.ctrl_widget.sig_play_button_pressed.connect(self.app_state.on_play_btn_pressed)
        # self.ctrl_widget.sig_stop_button_pressed.connect(self.app_state.on_stop_signal_pressed)
        # self.ctrl_widget.sig_export_wav_path.connect(self.app_state.on_export_path_changed)

        # # ---- Connect app_state signals to GUI update slots ----
        self.app_state.sig_pulse_changed.connect(self._on_pulse_update)
        self.app_state.sig_mod_lut_changed.connect(self._on_mod_scheme_lut_update)
        self.app_state.sig_baseband_changed.connect(self._on_baseband_update)
        self.app_state.sig_bandpass_changed.connect(self._on_bandpass_update)

        # # ---- Footer ----
        self.footer.btn_restart.clicked.connect(self.restart_application)

    @Slot(PulseSignal)
    def _on_pulse_update(self, pulse_container):
        self.pulse_time_plotter.update_plot(pulse_container)
        self.pulse_fft_plotter.update_plot(pulse_container)
        #self.pulse_periodogram_plotter.update_plot(pulse_container)

    @Slot(ModSchemeLUT)
    def _on_mod_scheme_lut_update(self, mod_scheme_container):
        self.const_plotter.update_plot(mod_scheme_container)

    @Slot(BasebandSignal)
    def _on_baseband_update(self, baseband_container):
        #start = time.perf_counter()
        self.baseband_plotter.update_plot(baseband_container)
        self.bb_fft_plotter.update_plot(baseband_container)
        self.bb_spectrogram_plotter.update_plot(baseband_container)
        #self.bb_periodogram_plotter.update_plot(baseband_container)
        # elapsed = (time.perf_counter() - start) * 1000
        # print(f"🎨 Baseband plots: {elapsed:.2f}ms")

    @Slot(BandpassSignal)
    def _on_bandpass_update(self, bandpass_container):
        # start = time.perf_counter()
        self.bandpass_plotter.update_plot(bandpass_container)
        self.bp_fft_plotter.update_plot(bandpass_container)
        # elapsed = (time.perf_counter() - start) * 1000
        # print(f"🎨 Bandpass plots: {elapsed:.2f}ms")

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
        self.bb_spectrogram_plotter.clear_plot()
        #self.bb_periodogram_plotter.clear_plot()
        self.bb_fft_plotter.clear_plot()
        self.bandpass_plotter.clear_plot()
        self.bp_spectrogram_plotter.clear_plot()
        #self.bp_periodogram_plotter.clear_plot()
        self.bp_fft_plotter.clear_plot()

        # Clear underlying data to prevent memory leaks
        self.app_state.clear_signals()

        # Clear bitstream entry
        self.ctrl_widget.clear_bitstream_entry()


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
    parser.add_argument('--sym-rate', type=int, default=DEFAULT_SYM_RATE, help='Set the symbol rate in sps.')
    args = parser.parse_args()

    app = QApplication(sys.argv)

    initial_values = {"sym_rate": args.sym_rate}

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


# TODO Implement all Spectogram and FFT option
# TODO Implement Interpolater
