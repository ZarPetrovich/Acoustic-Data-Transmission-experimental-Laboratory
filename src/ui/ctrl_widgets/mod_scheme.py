from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QPushButton, QFileDialog, QButtonGroup, QRadioButton
from PySide6.QtCore import Qt, Signal, QTimer
from src.constants import PulseShape
from src.dataclasses.dataclass_models import ModSchemeUpdateTask

class ModSchemeWidget(QGroupBox):
    sig_changed = Signal(ModSchemeUpdateTask)


    def __init__(self, parent= None):
        super().__init__("2. Constellation", parent)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Radio Buttons
        self.modulation_bg = QButtonGroup(self)
        hbox_ask_radio_btn = QHBoxLayout()
        for txt in ["2-ASK", "4-ASK", "8-ASK"]:
            rb_ask = QRadioButton(txt)
            self.modulation_bg.addButton(rb_ask)
            hbox_ask_radio_btn.addWidget(rb_ask)
        self.modulation_bg.buttons()[0].setChecked(True)

        layout.addLayout(hbox_ask_radio_btn)

        hbox_psk_radio_btn = QHBoxLayout()
        for txt in ["2-PSK", "4-PSK", "8-PSK"]:
            rb_psk = QRadioButton(txt)
            self.modulation_bg.addButton(rb_psk)
            hbox_psk_radio_btn.addWidget(rb_psk)

        layout.addLayout(hbox_psk_radio_btn)

        self.map_combo = QComboBox()
        self.map_combo.addItems(["Gray", "Binary"])

        layout.addWidget(self.map_combo)

        # Internal Connections

        self.modulation_bg.buttonClicked.connect(self._emit_mod)
        self.map_combo.currentTextChanged.connect(self._emit_mod)

    def _emit_mod(self):
        task = ModSchemeUpdateTask(
            mod_scheme = self.modulation_bg.checkedButton().text(),
            bit_mapping = self.map_combo.currentText()
        )

