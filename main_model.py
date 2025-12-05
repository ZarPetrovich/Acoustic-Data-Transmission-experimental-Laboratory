import sys, os, argparse
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PySide6.QtCore import Slot

# Local Application/Library Specific Imports
from adtx_lab.src.ui.intro_dialog import IntroDialog
from adtx_lab.src.core.AppState import AppState
from adtx_lab.src.constants import DEFAULT_FS, DEFAULT_SYM_RATE, DEFAULT_SPAN

# Application Logic (Processing)
from adtx_lab.src.dataclasses.metadata_models import ModSchemeLUT, PulseSignal, BasebandSignal

from adtx_lab.src.ui.widgets import ControlWidget, MatrixWidget, MetaDataWidget, MediaPlayerWidget, FooterWidget
from adtx_lab.src.ui.plot_strategies import PlotManager, PulsePlotStrategy, ConstellationPlotStrategy, BasebandPlotStrategy

from adtx_lab.src.ui.style.color_pallete import LIGHT_THEME_HEX


class MainGUILogic(QMainWindow):
    def __init__(self, initial_values):
        super().__init__()
        self.setWindowTitle(f"ADTX Labor - Main FS: {initial_values['fs']} Hz | Sym Rate: {initial_values['sym_rate']} sps")
        self.resize(1200, 800)

        # --- 1. Initialize UI Elements First ---
        self.ctrl_widget = ControlWidget()
        self.matrix_widget = MatrixWidget()
        self.meta_widget = MetaDataWidget()
        self.media_widget = MediaPlayerWidget()
        self.footer = FooterWidget()

        self._setup_ui()

        # --- 2. Init Plotters ---
        self.pulse_plotter = PlotManager(self.matrix_widget.plot_pulse)
        self.pulse_plotter.set_strategy(PulsePlotStrategy())

        self.const_plotter = PlotManager(self.matrix_widget.plot_const)
        self.const_plotter.set_strategy(ConstellationPlotStrategy())

        self.baseband_plotter = PlotManager(self.matrix_widget.plot_baseband)
        self.baseband_plotter.set_strategy(BasebandPlotStrategy())

        # --- 3. Initialize AppState (which may emit signals) ---
        self.app_state = AppState(initial_values)

        # --- 4. Setup Connections ---
        self._setup_connections()

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
        # Connect control widget signals to app_state slots
        self.ctrl_widget.sig_pulse_changed.connect(self.app_state.on_pulse_update)
        self.ctrl_widget.sig_mod_changed.connect(self.app_state.on_mod_update)
        self.ctrl_widget.sig_bit_seq_changed.connect(self.app_state.on_bitseq_update)
        self.ctrl_widget.sig_save_requested.connect(self._on_save_slot)
        self.ctrl_widget.sig_carrier_freq_changed.connect(self.app_state.on_carrier_freq_update)

        # Connect app_state signals to GUI update slots
        self.app_state.app_config_changed.connect(self._on_app_config_update)
        self.app_state.pulse_signal_changed.connect(self._on_pulse_update)
        self.app_state.modulation_lut_changed.connect(self._on_mod_scheme_lut_update)
        self.app_state.baseband_signal_changed.connect(self._on_baseband_update)
        # Footer
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
        self.baseband_plotter.update_plot(baseband_container)


    @Slot(int)
    def _on_save_slot(self, slot_idx):
        self.app_state.on_save_slot(slot_idx)
        self.statusBar().showMessage(f"Configuration saved to Slot {slot_idx + 1}", 3000)

    @Slot()
    def restart_application(self):
        QApplication.instance().quit()
        # Add the --no-intro flag to the arguments when restarting
        # We can remove the explicit --no-intro flag now, as argparse handles it
        os.execl(sys.executable, sys.executable, *sys.argv)


def load_stylesheet_with_palette(qss_path, palette):
    with open(qss_path, "r") as f:
        qss = f.read()
    for key, value in palette.items():
        qss = qss.replace(f"{{{{{key}}}}}", value)
    return qss

def main():
    parser = argparse.ArgumentParser(description="ADTx Laboratory")
    parser.add_argument('--no-intro', action='store_true', help='Skip the intro dialog and use default values.')
    parser.add_argument('--fs', type=int, default=DEFAULT_FS, help='Set the sample rate in Hz.')
    parser.add_argument('--sym-rate', type=int, default=DEFAULT_SYM_RATE, help='Set the symbol rate in sps.')
    parser.add_argument('--span', type = int, default = DEFAULT_SPAN, help="Set the pulse span as integer.")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    initial_values = {"fs": args.fs, "sym_rate": args.sym_rate, "span": args.span}

    if not args.no_intro:
        intro_dialog = IntroDialog(initial_values=initial_values)
        if intro_dialog.exec():
            updated_values = intro_dialog.get_values()
            # Ensure 'span' is preserved if not explicitly updated
            initial_values.update(updated_values)
        else:
            sys.exit()  # ! Exit if the user cancels the dialog


    main_app = MainGUILogic(initial_values=initial_values)
    main_app.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
