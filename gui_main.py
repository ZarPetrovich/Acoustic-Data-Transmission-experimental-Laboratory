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
    QVBoxLayout,
    QDialog
)

# Local Application/Library Specific Imports

from adtx_lab.src.ui.intro_dialog import *
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
    Header,
    FooterWidget,
    PulseTab,
    BasebandTab
)


class MainGUILogic(QMainWindow):

    def __init__(self, initial_values):

        super().__init__()

        self.setWindowTitle("ADM Lab")
        self.setGeometry(100, 100, 900, 600)

        # DEFAULT PARAMETERS

        self.fs = initial_values["fs"]
        self.sym_rate = initial_values["sym_rate"]
        self.dict_pulse_signals = None

        # Set ENUM Constants Name
        self.pulse_shape_map = {
            PulseShape.RECTANGLE: "Rectangle",
            PulseShape.COSINE_SQUARED: "Cosine²"
        }

        self.modulation_scheme_map = {
            ModulationScheme.AMPLITUDE_MODULATION: "Amplitude Modulation"
        }

        # +++ Init Widgets +++

        # Footer
        self.widget_footer = FooterWidget(self)

        # Header "Global Parameters"
        self.widget_header = Header(self.fs, self.sym_rate)

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

        main_layout.addWidget(self.widget_header)
        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(main_content_container)

        # QT SIGNALS

        # +++ Main Connections +++

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

        self.widget_footer.set_info(formatted_text)

    # Main Logic
    def create_pulse(self):

        values = self.content_tab_pulse.get_values()
        shape = values['shape']
        span = values['span']

        if shape == PulseShape.RECTANGLE:
            rect_generator = rect_generator = RectanglePulse(self.sym_rate, self.fs, span)
            rect_pulse_data = rect_generator.generate()
            rectangle_pulse_01 = PulseSignal(
                  "Rectangle Pulse 01",
                  rect_pulse_data,
                  self.fs,
                  self.sym_rate,
                  PulseShape.RECTANGLE,
                  span
                    )
            return rectangle_pulse_01


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

    main_app = MainGUILogic(initial_values = {"fs": 48000, "sym_rate": 100})
    main_app.show()

    sys.exit(app.exec())

    # dialog = IntroDialog()

    # if dialog.exec() == QDialog.Accepted:

    #     values = dialog.get_values()

    #     main_app = MainGUILogic(initial_values = values)
    #     main_app.show()

    #     sys.exit(app.exec())

    # else:
    #     logging.info("Application closed by user before start.")
    #     sys.exit(0)