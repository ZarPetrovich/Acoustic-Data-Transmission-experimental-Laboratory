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
from adtx_lab.src.constants import PulseShape, BitMappingScheme, ModulationScheme
from adtx_lab.src.logging.formatter import CustomFormatter

# Application Logic (Processing)
from adtx_lab.src.dataclasses.bitseq_models import BitSequence
from adtx_lab.src.dataclasses.signal_models import *
from adtx_lab.src.nrz_mapping.nrz_mapping import PolarNRZMapping, UniPolarNRZMapping
from adtx_lab.src.baseband_modules.shape_generator import CosinePulse, RectanglePulse
from adtx_lab.src.baseband_modules.baseband_signal_generator import (
    BasebandSignalGenerator,
)
from adtx_lab.src.ui.plot_strategies import PlotManager, PulsePlotStrategy, BasebandPlotStrategy
from adtx_lab.src.ui.plot_widgets import PlotWidget

# Application GUI (Widgets)
from adtx_lab.src.ui.qt_widgets import (
    Header,
    FooterWidget,
    PulseTab,
    BitMappingTab,
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
        self.map_pulse_shape = {
            PulseShape.RECTANGLE: "Rectangle",
            PulseShape.COSINE_SQUARED: "Cosine²",
        }
        self.map_bitmapping_scheme = {
            BitMappingScheme.POLARNRZMAPPING: "NRZ Polar",
            BitMappingScheme.UNIPOLARNRZMAPPING: "NRZ Unipolar"
        }
        self.map_modulation_scheme = {
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
        self.content_tab_pulse = PulseTab(pulse_shape_map=self.map_pulse_shape)
        self.tab_widget.addTab(self.content_tab_pulse, "Puls Shaping")

        # BITSEQ

        self.content_tab_bitseq = BitMappingTab(map_bitmapping_scheme = self.map_bitmapping_scheme)
        self.tab_widget.addTab(self.content_tab_bitseq, " Bit Mapping")

        # BASEBAND
        self.content_tab_baseband = BasebandTab()
        self.tab_widget.addTab(self.content_tab_baseband, "Baseband Signal")

        # Modulation

        self.content_tab_modulation = ModulationTab(
            mod_scheme_map=self.map_modulation_scheme
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

        # Plotting

        self.pulse_plot_manager = PlotManager(self.content_tab_pulse.plot_pulses_widget)
        self.baseband_plot_manager = PlotManager(self.content_tab_baseband.plot_bb_widget)

        # region +++ QT SIGNALS +++

        # +++ Main Connections +++

        self.content_tab_pulse.signal_create_Pulse.connect(
            self.create_pulse
        )
        self.content_tab_pulse.signal_tab_pulse_selected.connect(
            self.on_pulse_selected
        )
        self.content_tab_baseband.signal_create_basebandsignal.connect(
            self.create_baseband_signal
        )

        self.content_tab_baseband.signal_tab_baseband_selected.connect(
            self.on_baseband_selected
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

        new_pulse_name = f"{self.map_pulse_shape[shape]}_Pulse_{self.counter_pulse}"
        self.counter_pulse += 1

        generated_pulse_signal = PulseSignal(
            new_pulse_name,
            pulse_data,
            self.fs,
            self.sym_rate,
            shape,
            span
        )

        # LOGINFO
        self.log_info(f"Created Pulse Signal: {generated_pulse_signal.name}")

        # Update Dictionary
        self.dict_pulse_signals[new_pulse_name] = generated_pulse_signal

        # Update Baseband Combobox
        self.content_tab_baseband.update_pulse_signals(
            self.dict_pulse_signals)

        # update Pulse List Widget

        self.content_tab_pulse.update_list(
            self.dict_pulse_signals
        )

    def on_pulse_selected(self, pulse_name):
        signal_object = self.dict_pulse_signals.get(pulse_name)
        if isinstance(signal_object, PulseSignal):
            self.pulse_plot_manager.set_strategy(PulsePlotStrategy())
            self.pulse_plot_manager.update_plot(signal_object)
            self.log_info(f"plotting {signal_object.name}")

    def create_baseband_signal(self):

        #
        sel_pulse_signal = self.content_tab_baseband.combobox_pulse_signals.currentData()

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

        # Init Baseband Signal Generator on selected Puls Signal
        baseband_generator = BasebandSignalGenerator(sel_pulse_signal)

        # Gen Data with specific Bit Sequence
        baseband_signal_data = baseband_generator.generate_baseband_signal(
            bit_seq_polar_no1
        )
        # Create Name with counter
        new_baseband_name = f"Baseband_Signal_{self.counter_baseband}"
        self.counter_baseband += 1

        # Store In Dataclass Container
        generated_baseband_signal = BasebandSignal(
            new_baseband_name,
            baseband_signal_data,
            self.fs,
            self.sym_rate,
            sel_pulse_signal.name,
            bit_seq_polar_no1.name,
        )
        # Update Main Dict of Baseband Signals

        self.dict_baseband_signals[new_baseband_name] = generated_baseband_signal
        # Update List in Tab baseband
        self.content_tab_baseband.update_list(self.dict_baseband_signals)
        # Update Combo in Tab Modulation
        self.content_tab_modulation.update_baseband_signals(
            self.dict_baseband_signals)
        # Log_Info
        self.log_info(
            f"Baseband Signal Created: {generated_baseband_signal.name}")

    def on_baseband_selected(self):
        baseband_name = self.content_tab_baseband.list_baseband_signals.currentItem().text()

        signal_object = self.dict_baseband_signals.get(baseband_name)
        if isinstance(signal_object, BasebandSignal):
            self.baseband_plot_manager.set_strategy(BasebandPlotStrategy())
            self.baseband_plot_manager.update_plot(signal_object)
            self.log_info(f"plotting {signal_object.name}")

    def modulate_update(self):
        self.tab_content_modulation.combo
        None

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
