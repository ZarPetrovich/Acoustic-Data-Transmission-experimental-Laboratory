from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QPushButton, QFileDialog, QButtonGroup, QRadioButton
from PySide6.QtCore import Qt, Signal, QTimer
from src.constants import PulseShape, MOD_SCHEME_MAP, AVAILABLE_MOD_SCHEMES, BitMappingScheme
from src.dataclasses.dataclass_models import ModSchemeUpdateTask

class ModSchemeWidget(QGroupBox):

    sig_changed = Signal(ModSchemeUpdateTask)

    def __init__(self, parent= None):
        super().__init__("2. Constellation", parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        self.modulation_bg = QButtonGroup(self)

        for scheme_enum, m_values in AVAILABLE_MOD_SCHEMES.items():
                    hbox = QHBoxLayout()
                    short_name = MOD_SCHEME_MAP[scheme_enum] # "ASK" or "PSK"

                    for M in m_values:
                        display_text = f"{M}-{short_name}" # "2-ASK"
                        rb = QRadioButton(display_text)

                        rb.setProperty("scheme_enum", scheme_enum)
                        rb.setProperty("cardinality", M)

                        self.modulation_bg.addButton(rb)
                        hbox.addWidget(rb)
                    layout.addLayout(hbox)

        self.map_combo = QComboBox()
        self.map_combo.addItems(mapper.name for mapper in BitMappingScheme)

        layout.addWidget(self.map_combo)

        # Internal Connections

        self.modulation_bg.buttonClicked.connect(self._emit_mod)
        self.map_combo.currentTextChanged.connect(self._emit_mod)

    def _emit_mod(self):
            btn = self.modulation_bg.checkedButton()

            # Pull the clean objects from the button properties
            task = ModSchemeUpdateTask(
                scheme_enum=btn.property("scheme_enum"),
                cardinality=btn.property("cardinality"),
                mapper_enum=BitMappingScheme[self.map_combo.currentText().upper()],
                display_name=btn.text()
            )

            self.sig_changed.emit(task)

