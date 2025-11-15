from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import(
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QFormLayout,
    QComboBox)


class Header(QWidget):

    def __init__(self, fs,sym_rate, parent=None):

        super().__init__(parent)

        layout = QGridLayout(self)

        self.label_fs = QLabel(f"FS : {fs} Hz ")
        layout.addWidget(self.label_fs)

        self.label_sym_rate = QLabel(f"Symbolrate : {sym_rate} Symbol/s")
        layout.addWidget(self.label_sym_rate)

        self.label_samples_per_symbol = QLabel(f"Samples/Symbol: {int(fs/sym_rate)} samples ")
        layout.addWidget(self.label_samples_per_symbol)




class PulseTab(QWidget):

    signal_pulse_created = Signal()

    def __init__(self,
                 pulse_shape_map,
                 parent=None):

        super().__init__(parent)

        self.reverse_map_pulse_shape = {v: k for k, v in pulse_shape_map.items()}

        outer_layout = QGridLayout(self)

        form_layout = QFormLayout()

        self.combobox_pulse_shapes = QComboBox()
        self.combobox_pulse_shapes.addItems(pulse_shape_map.values())
        form_layout.addRow("Pulse Shape:", self.combobox_pulse_shapes)

        self.spinbox_pulse_span = QSpinBox(self)
        self.spinbox_pulse_span.setRange(1, 5)
        self.spinbox_pulse_span.setSingleStep(1)
        self.spinbox_pulse_span.setValue(1)

        form_layout.addRow("Pulse Span :", self.spinbox_pulse_span)

        outer_layout.addLayout(form_layout, 0, 0)
        outer_layout.setColumnStretch(1, 1)

        btn_create_pulse = QPushButton("Create Pulse")
        form_layout.addRow(btn_create_pulse)

        btn_create_pulse.clicked.connect(self.signal_pulse_created.emit)

    def get_values(self):

        sel_shape_text = self.combobox_pulse_shapes.currentText()

        return {
            'shape': self.reverse_map_pulse_shape.get(sel_shape_text),
            'span': self.spinbox_pulse_span.value()
        }

class BasebandTab(QWidget):

    signal_create_basebandsignal = Signal()

    def __init__(self,
                 mod_scheme_map,
                 parent = None):

        super().__init__(parent)

        self.reverse_map_mod_schemes = {v: k for k, v in mod_scheme_map.items()}

        outer_layout = QGridLayout(self)

        form_layout = QFormLayout()

        self.combobox_mod_schemes = QComboBox()
        self.combobox_mod_schemes.addItems(mod_scheme_map.values())
        form_layout.addRow("Modulation Scheme:", self.combobox_mod_schemes)

        outer_layout.addLayout(form_layout, 0, 0)
        outer_layout.setColumnStretch(1, 1)

        btn_create_baseband_signal = QPushButton("Create Baseband Signal")
        form_layout.addRow(btn_create_baseband_signal)

        btn_create_baseband_signal.clicked.connect(self.signal_create_basebandsignal.emit)


        def get_values(self):

            None



class FooterWidget:

    def __init__(self, main_window):

        self.status_bar = main_window.statusBar()

        # Labels

        # self.pulse_label = QLabel("Pulse: N/A")
        # self.mod_label = QLabel("Mod: N/A")

        # self.pulse_label.setStyleSheet("margin-right: 10px;")
        # self.mod_label.setStyleSheet("margin-right: 10px;")
        # Buttons

        close_button = QPushButton("Exit")
        restart_button = QPushButton("Restart ADM Lab")

        close_button.clicked.connect(main_window.close)
        restart_button.clicked.connect(main_window.restart_application)

        # self.status_bar.addPermanentWidget(self.mod_label)
        # self.status_bar.addPermanentWidget(self.pulse_label)

        self.status_bar.addPermanentWidget(restart_button)
        self.status_bar.addPermanentWidget(close_button)

        self.set_ready()

    # def update_pulse_shape(self, shape_text):
    #     self.pulse_label.setText(f"Pulse: {shape_text}")

    # def update_mod_scheme(self, scheme_text):
    #     self.mod_label.setText(f"Mod: {scheme_text}")

    def set_ready(self):
        self.status_bar.showMessage("Ready for action")

    def set_info(self, text, timeout_ms=3000):
        self.status_bar.showMessage(text, timeout_ms)


    def set_error(self, text, timeout_ms=3000):
        self.status_bar.showMessage(f"Error: {text}", timeout_ms)
