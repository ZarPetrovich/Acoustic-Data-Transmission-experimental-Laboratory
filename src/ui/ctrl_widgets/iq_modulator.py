from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup, QPushButton
from PySide6.QtCore import Signal
from src.dataclasses.dataclass_models import CarrierUpdateTask

class IQModulatorWidget(QGroupBox):
    # Signal for the Mediator (main_model.py)
    sig_modulate_clicked = Signal(CarrierUpdateTask)

    def __init__(self, parent=None):
        super().__init__("4. IQ Modulator", parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.addWidget(QLabel("Carrier Frequency:"))

        # Radio Buttons for Frequency
        self.freq_bg = QButtonGroup(self)
        h_rad = QHBoxLayout()

        # Restoring your exact frequencies from widgets.py
        for txt in ["440 Hz", "4400 Hz", "8800 Hz"]:
            rb = QRadioButton(txt)
            self.freq_bg.addButton(rb)
            h_rad.addWidget(rb)

        self.freq_bg.buttons()[0].setChecked(True)
        layout.addLayout(h_rad)

        # The Action Button
        self.btn_modulate = QPushButton("Modulate")
        layout.addWidget(self.btn_modulate)

        # Connections
        self.btn_modulate.clicked.connect(self._emit_carrier_freq)

    def _emit_carrier_freq(self):
        """
        Extracts the numeric value from the button text
        and sends it as a DTO.
        """
        raw_text = self.freq_bg.checkedButton().text()
        # "440 Hz" -> 440
        freq_val = int(raw_text.split(" ")[0])

        task = CarrierUpdateTask(carrier_freq=freq_val)

        self.sig_modulate_clicked.emit(task)