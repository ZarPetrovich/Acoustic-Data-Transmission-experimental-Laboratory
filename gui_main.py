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
    QDialog,
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
from adtx_lab.src.baseband_modules.baseband_signal_generator import (
    BasebandSignalGenerator,
)

# Application GUI (Widgets)
from adtx_lab.src.ui.qt_widgets import (
    Header,
    FooterWidget,
    PulseTab,
    BasebandTab,
    ModulationTab,
)


class MainGUILogic(QMainWindow):

    def __init__(self, initial_values):
        # region
        super().__init__()

        self.setWindowTitle("ADM Lab")
        self.setGeometry(100, 100, 900, 600)
        # endregion

        # region DEFAULT PARAMETERS

        self.fs = initial_values["fs"]
        self.sym_rate = initial_values["sym_rate"]
        self.dict_pulse_signals = {}
        self.counter_pulse = 1

        self.dict_baseband_signals = {}
        self.counter_baseband = 1

        # Set ENUM Constants Name
        self.pulse_shape_map = {
            PulseShape.RECTANGLE: "Rectangle",
            PulseShape.COSINE_SQUARED: "Cosine²",
        }

        self.modulation_scheme_map = {
            ModulationScheme.AMPLITUDE_MODULATION: "Amplitude Modulation"
        }
        # endregion

        # region +++ Init Widgets +++

        # Footer
        self.widget_footer = FooterWidget(self)

        # Header "Global Parameters"
        self.widget_header = Header(self.fs, self.sym_rate)
        # endregion

        # region +++ Init Tabs +++
        # PULSE
        self.tab_widget = QTabWidget()
        self.content_tab_pulse = PulseTab(pulse_shape_map=self.pulse_shape_map)
        self.tab_widget.addTab(self.content_tab_pulse, "Puls Shaping")

        # BASEBAND
        self.content_tab_baseband = BasebandTab()
        self.tab_widget.addTab(self.content_tab_baseband, "Baseband Signal")

        # Modulation

        self.content_tab_modulation = ModulationTab(
            mod_scheme_map=self.modulation_scheme_map
        )
        self.tab_widget.addTab(self.content_tab_modulation, "Modulation")
        # endregion

        # region +++ Main Layout +++
        #
        main_content_container = QWidget()

        main_layout = QVBoxLayout(main_content_container)
        main_layout.setContentsMargins(0, 10, 0, 0)

        # Add Header Widget & Tab Widget to Main Layout

        main_layout.addWidget(self.widget_header)
        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(main_content_container)
        # endregion

        # region +++ QT SIGNALS +++

        # +++ Main Connections +++

        self.content_tab_pulse.signal_create_Pulse.connect(
            self.create_pulse
        )
        self.content_tab_baseband.signal_create_basebandsignal.connect(
            self.create_baseband_signal
        )
        self.content_tab_modulation.signal_create_Modulation.connect(
            self.modulate_transmit_signal
        )

        # endregion
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

    def log_error(self, message, *args):

        logging.error(message, *args)

        if args:
            formatted_text = message % args
        else:
            formatted_text = message

        self.widget_footer.set_info(formatted_text)

    # Main

    def create_pulse(self):
        # Init Values
        values = self.content_tab_pulse.get_values()
        shape = values["shape"]
        span = values["span"]

        # Init Generators
        pulse_generators = {
            PulseShape.RECTANGLE: RectanglePulse,
            PulseShape.COSINE_SQUARED: CosinePulse,
        }

        generator_cls = pulse_generators.get(shape)

        if not generator_cls:
            self.log_error("Unknown Pulse Shape")

        generator = generator_cls(self.sym_rate, self.fs, span)
        pulse_data = generator.generate()

        new_pulse_name = f"{self.pulse_shape_map[shape]}_Pulse_{self.counter_pulse}"
        self.counter_pulse += 1

        generated_pulse_signal = PulseSignal(
            new_pulse_name, pulse_data, self.fs, self.sym_rate, shape, span
        )

        # LOGINFO
        self.log_info(f"Created Pulse Signal: {generated_pulse_signal.name}")

        # Update Dictionary
        self.dict_pulse_signals[new_pulse_name] = generated_pulse_signal

        # Update Baseband Combobox
        self.content_tab_baseband.update_pulse_signals(
            self.dict_pulse_signals.keys())

    def get_sel_pulse_signal(self):
        try:
            sel_pulse_signal_name = self.content_tab_baseband.get_values().get(
                "pulse_signal"
            )

            sel_pulse_signal = self.dict_pulse_signals.get(
                sel_pulse_signal_name)

            if not sel_pulse_signal:
                self.log_info(
                    f"Pulse Signal '{sel_pulse_signal_name}' not found")
                return None

            return sel_pulse_signal

        except Exception as e:
            self.log_info(f"Error retrieving pulse signal: {e}")

    def create_baseband_signal(self):
        sel_pulse_signal = self.get_sel_pulse_signal()
        if not sel_pulse_signal:
            return

        # For simplicity, we use a fixed bit sequence here
        bit_seq_no1 = np.array([1, 0, 1, 0])  # Example binary sequence

        raw_bit_seq = BitSequence(
            "Raw Bit Seq No_1",
            bit_seq_no1,
            data_rate=1,
        )

        polar_mapper = PolarNRZMapping()
        bit_seq_polar_no1 = BitSequence(
            "Polar Mapped Seq No_1",
            polar_mapper.generate(raw_bit_seq.data),
            data_rate=1,
        )

        baseband_generator = BasebandSignalGenerator(sel_pulse_signal)

        baseband_signal_data = baseband_generator.generate_baseband_signal(
            bit_seq_polar_no1
        )

        new_baseband_name = f"Baseband_Signal_{self.counter_baseband}"
        self.counter_baseband += 1

        generated_baseband_signal = BasebandSignal(
            new_baseband_name,
            baseband_signal_data,
            self.fs,
            self.sym_rate,
            sel_pulse_signal.name,
            bit_seq_polar_no1.name,
        )

        self.dict_baseband_signals[new_baseband_name] = generated_baseband_signal

        self.content_tab_modulation.update_baseband_signals(
            self.dict_baseband_signals)

        self.log_info(
            f"Baseband Signal Created: {generated_baseband_signal.name}")

    def modulate_transmit_signal(self):

        self.log_info("Modulation not yet implemented.")


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

    main_app = MainGUILogic(initial_values={"fs": 48000, "sym_rate": 100})
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
