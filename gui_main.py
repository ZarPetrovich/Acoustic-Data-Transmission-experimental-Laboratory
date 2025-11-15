"""
Main application module
"""

# Standard Library Imports
import logging
import os
import sys

# Third-Party Imports
import colorama
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout
)

# Local Application/Library Specific Imports

# Application Constants & Logging
from adtx_lab.src.constants import PulseShape, ModulationScheme
from adtx_lab.src.logging.formatter import CustomFormatter

# Application Logic (Processing)
from adtx_lab.src.dataclasses.bitseq_models import BitSequence
from adtx_lab.src.dataclasses.signal_models import *
from adtx_lab.src.nrz_mapping.nrz_mapping import PolarNRZMapping, UniPolarNRZMapping
from adtx_lab.src.baseband_modules.shape_generator import CosinePulse, RectanglePulse

# Application GUI (Widgets)
from adtx_lab.src.ui.qt_widgets import (
    GlobalParameterWidget,
    FooterWidget,
    PulseTab,
    BasebandTab
)


class MainGUILogic(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("ADM Lab")
        self.setGeometry(100, 100, 900, 600)

        # DEFAULT PARAMETERS

        self.fs = 48000
        self.sym_sec = 100
        self.pulse_parameters = None
        self.pulse_object = None

        self.pulse_shape_map = {
            PulseShape.RECTANGLE: "Rectangle",
            PulseShape.COSINE_SQUARED: "Cosine²"
        }

        self.modulation_scheme_map = {
            ModulationScheme.AMPLITUDE_MODULATION: "Amplitude Modulation"
        }

        # +++ Init Widgets +++
        # Footer
        self.footer = FooterWidget(self)

        # Header "Global Parameters"
        self.global_params_widget = GlobalParameterWidget()
        self.global_params_widget.txt_input_param_fs.setText(str(self.fs))
        self.global_params_widget.spinbox_sym_sec.setValue(self.sym_sec)

        # +++ Init Tabs +++
        # PULSE
        self.tab_widget = QTabWidget()
        self.content_tab_pulse = PulseTab(
            pulse_shape_map=self.pulse_shape_map
        )
        self.tab_widget.addTab(self.content_tab_pulse, "Puls Shaping")

        # BASEBAND
        self.content_tab_baseband = BasebandTab(
            mod_scheme_map=self.modulation_scheme_map
        )
        self.tab_widget.addTab(self.content_tab_baseband, "Baseband Signal")

        # +++ Main Layout +++

        main_content_container = QWidget()

        main_layout = QVBoxLayout(main_content_container)
        main_layout.setContentsMargins(0, 10, 0, 0)

        # Add Header Widget & Tab Widget to Main Layout

        main_layout.addWidget(self.global_params_widget)
        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(main_content_container)

        # QT SIGNALS

        # +++ Main Connections +++
        self.global_params_widget.signal_global_changes.connect(
            self.save_global_param)
        self.content_tab_pulse.signal_pulse_created.connect(
            self.create_pulse)
        self.content_tab_baseband.signal_create_basebandsignal.connect(
            self.create_baseband_signal)

        # END __INIT__

    # Helper Functions

    def restart_application(self):
        logging.info("Restarting application...")
        QApplication.instance().quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def log_info(self, message, *args):

        logging.info(message, *args)

        if args:
            formatted_text = message % args
        else:
            formatted_text = message

        self.footer.set_info(formatted_text)

    # Main Logic

    def save_global_param(self):
        fs_value = self.global_params_widget.txt_input_param_fs.text()
        sym_rate_value = self.global_params_widget.spinbox_sym_sec.value()

        self.log_info("Fs and Sym/s saved: Fs=%s, Symbols/s=%d",
                      fs_value, sym_rate_value)

    def create_pulse(self):

        try:
            self.content_tab_pulse.get_values()

            self.pulse_parameters = self.content_tab_pulse.get_values()

        except Exception as e:
            logging.error(
                "An error occurred while saving pulse parameters: %s", e)

        # ELIF for every Pulse

        if self.pulse_parameters['shape'] == PulseShape.RECTANGLE:
            None

        elif self.pulse_parameters['shape'] == PulseShape.COSINE_SQUARED:
            None

    def create_baseband_signal(self):

        None


if __name__ == "__main__":
    colorama.init()
    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)

    app = QApplication(sys.argv)

    main_app = MainGUILogic()
    main_app.show()

    sys.exit(app.exec())
