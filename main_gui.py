import sys
import os
import json
import logging
from PySide6.QtCore import (
    QSize, Qt, QPoint, QTimer, Slot, Signal
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import *

import numpy as np  # Needed for array manipulation in plot update


# Local Application/Library Specific Imports
# Logic
from adtx_lab.src.ui.intro_dialog import *
from adtx_lab.src.constants import PulseShape
from adtx_lab.src.logging.formatter import CustomFormatter
from adtx_lab.src.dataclasses.bitseq_models import SymbolSequence
from adtx_lab.src.dataclasses.signal_models import PulseSignal, BasebandSignal
from adtx_lab.src.baseband_modules.shape_generator import CosinePulse, RectanglePulse
from adtx_lab.src.bitmapping.mod_symbol_generator import AmpShiftKeying
from adtx_lab.src.baseband_modules.baseband_signal_generator import BasebandSignalGenerator
# UI Files

from adtx_lab.src.ui.widgets import MatrixWidget, FooterWidget


class MainGui(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADTX Labor - Acoustic Data Transmission Experiment Lab")
        self.resize(1200, 800)

        # Create a central widget for the QMainWindow
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        outer_v_box = QVBoxLayout(central_widget)

        # Add the MatrixWidget
        self.matrix_widget = MatrixWidget()
        outer_v_box.addWidget(self.matrix_widget)

        # Add the FooterWidget (optional, if needed)
        self.footer_widget = FooterWidget()
        outer_v_box.addWidget(self.footer_widget)

    @Slot()
    def restart_application(self):
        """Simulates restarting the application by simply printing a message."""
        print("--- RESTART APPLICATION TRIGGERED ---")
        self.statusBar().showMessage("Application Restart Simulated.", 3000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainGui()
    window.show()
    sys.exit(app.exec())