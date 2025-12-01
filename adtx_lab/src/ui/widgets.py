from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
    QPushButton, QGroupBox, QSlider, QComboBox, QRadioButton,
    QButtonGroup, QGridLayout, QFormLayout, QScrollArea, QFrame, QAbstractButton,
    QLineEdit
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator
from adtx_lab.src.ui.plot_widgets import PlotWidget


# --- Main Widgets ---

class ControlWidget(QWidget):
    # SIGNALS: The outside world listens to these
    sig_pulse_changed = Signal(dict)        # Emits {pulse_type, span, roll_off}
    sig_mod_changed = Signal(dict)          # Emits {mod_scheme, mapping}
    sig_bit_seq_changed = Signal(dict)      # Emits {bit_sequence}

    sig_save_requested = Signal(int)        # Emits slot_index (0-3) to save to
    sig_slot_selection_changed = Signal(int) # Emits slot_index (0-3) selected for viewing

    def __init__(self, parent=None,
                 map_pulse_shape = None):
        super().__init__(parent)

        # Scroll Area setup
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content_widget = QWidget()
        self.vbox = QVBoxLayout(content_widget)

        # 1. Pulse Shaping
        self._init_pulse_group(map_pulse_shape)
        # 2. Constellation
        self._init_constellation_group()
        # 4. Save Controls
        self._init_save_group()
        # 3. IQ Modulator
        self._init_iq_group()

        self.vbox.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _init_pulse_group(self, map_pulse_shape):
        group = QGroupBox("1. Pulse Shaping")
        layout = QVBoxLayout(group)

        # Pulse Type
        pulse_type_layout = QHBoxLayout()
        pulse_type_layout.addWidget(QLabel("Pulse Type:"))
        self.pulse_combo = QComboBox()
        self.pulse_combo.addItems(map_pulse_shape.values())
        pulse_type_layout.addWidget(self.pulse_combo)
        layout.addLayout(pulse_type_layout)

        # Span and Roll-off
        sliders_layout = QVBoxLayout()

        # Span
        span_layout = QHBoxLayout()
        span_layout.addWidget(QLabel("Span:"))
        self.slider_span = QSlider(Qt.Orientation.Horizontal)
        self.slider_span.setRange(1, 5)
        self.slider_span.setValue(1)
        self.lbl_span = QLabel("1")
        span_layout.addWidget(self.slider_span)
        span_layout.addWidget(self.lbl_span)
        sliders_layout.addLayout(span_layout)

        # Roll-off
        rolloff_layout = QHBoxLayout()
        rolloff_layout.addWidget(QLabel("Roll-off (α):"))
        self.slider_roll = QSlider(Qt.Orientation.Horizontal)
        self.slider_roll.setRange(0, 100)
        self.slider_roll.setValue(50)
        self.lbl_roll = QLabel("0.50")
        rolloff_layout.addWidget(self.slider_roll)
        rolloff_layout.addWidget(self.lbl_roll)
        sliders_layout.addLayout(rolloff_layout)

        layout.addLayout(sliders_layout)
        self.vbox.addWidget(group)

        # Internal Connections
        self.pulse_combo.currentTextChanged.connect(self._emit_pulse)
        self.slider_span.valueChanged.connect(self._emit_pulse)
        self.slider_roll.valueChanged.connect(self._emit_pulse)

        self.vbox.addWidget(group)

    def _init_constellation_group(self):
        group = QGroupBox("2. Constellation")
        layout = QVBoxLayout(group)

        # Radio Buttons
        self.mod_bg = QButtonGroup(self)
        h_rad = QHBoxLayout()
        for txt in ["2-ASK", "4-ASK", "8-ASK"]:
            rb = QRadioButton(txt)
            self.mod_bg.addButton(rb)
            h_rad.addWidget(rb)
        self.mod_bg.buttons()[0].setChecked(True)
        layout.addLayout(h_rad)

        self.map_combo = QComboBox()
        self.map_combo.addItems(["Gray", "Binary"])
        layout.addWidget(self.map_combo)

        # Internal Connections

        self.mod_bg.buttonClicked.connect(self._emit_mod)
        self.map_combo.currentTextChanged.connect(self._emit_mod)

        self.vbox.addWidget(group)


    def _init_save_group(self):
        group = QGroupBox("4. Save Baseline")
        layout = QVBoxLayout(group)

        layout.addWidget(QLabel("Enter Bitsequence: "))
        self.entry_bitsequence = QLineEdit()
        self.entry_bitsequence.setText("1010")
        layout.addWidget(self.entry_bitsequence)
        regex = QRegularExpression("^[01]+$")
        bit_validator = QRegularExpressionValidator(regex, self)
        self.entry_bitsequence.setValidator(bit_validator)
        self.slot_bg = QButtonGroup(self)

        h_lay = QHBoxLayout()
        for i in range(1, 5):
            rb = QRadioButton(f"Slot {i}")
            self.slot_bg.addButton(rb, i-1) # ID 0-3
            h_lay.addWidget(rb)
        self.slot_bg.buttons()[0].setChecked(True)
        layout.addLayout(h_lay)

        btn_save = QPushButton("Store Active Signal")
        btn_save.clicked.connect(lambda: self.sig_save_requested.emit(self.slot_bg.checkedId()))
        layout.addWidget(btn_save)

        # Connection for slot changing (viewing)
        self.slot_bg.idClicked.connect(self.sig_slot_selection_changed.emit)
        self.entry_bitsequence.textChanged.connect(self._emit_create_bb_signal)
        self.vbox.addWidget(group)


    def _init_iq_group(self):
        group = QGroupBox("3. IQ Modulator")
        layout = QVBoxLayout(group)

        # self.slider_freq = QSlider(Qt.Orientation.Horizontal)
        # self.slider_freq.setRange(100, 1000)
        # self.slider_freq.setValue(550)
        # layout.addWidget(QLabel("Carrier Freq:"))
        # layout.addWidget(self.slider_freq)

        # self.slider_phase = QSlider(Qt.Orientation.Horizontal)
        # self.slider_phase.setRange(0, 360)
        # layout.addWidget(QLabel("Phase Offset:"))
        # layout.addWidget(self.slider_phase)

        self.vbox.addWidget(group)



    # --- Internal Emitters (Format data before sending) ---
    def _emit_pulse(self):
        val_roll_off = self.slider_roll.value() / 100.0
        val_span = self.slider_span.value()
        self.lbl_span.setText(f"{val_span}")
        self.lbl_roll.setText(f"{val_roll_off:.2f}")
        self.sig_pulse_changed.emit({
            "pulse_type": self.pulse_combo.currentText(),
            "span": val_span,
            "roll_off": val_roll_off,
        })

    def _emit_mod(self):
        self.sig_mod_changed.emit({
            "mod_scheme": self.mod_bg.checkedButton().text(),
            "bit_mapping": self.map_combo.currentText()
        })

    def _emit_create_bb_signal(self):
        self.sig_bit_seq_changed.emit({
            "bit_seq": self.entry_bitsequence.text()
        })


class MatrixWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Grid Layout
        layout = QGridLayout(self)

        # +++ Pulse Plot Widget +++
        self.plot_pulse = PlotWidget(title="Pulse Shape (Time)")

        # 2. Constellation Plot (Scatter)
        self.plot_const = PlotWidget(title="Constellation (I/Q)")
        self.plot_const.plot_widget.setAspectLocked(True) # Important for Constellations
        self.plot_const.plot_widget.showGrid(x=True, y=True)


        # 3. Baseband (Placeholder for now as requested)
        self.plot_baseband = PlotWidget(title="Baseband (Time) - Pending")

        # 4. FFT (Placeholder)
        self.plot_fft = PlotWidget(title="Spectrum - Pending")

        layout.addWidget(self.plot_pulse, 0, 0)
        layout.addWidget(self.plot_const, 0, 1)
        layout.addWidget(self.plot_baseband, 1, 0)
        layout.addWidget(self.plot_fft, 1, 1)




class MetaDataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.group = QGroupBox("5. Selected Baseline Parameters")
        layout.addWidget(self.group)

        form = QFormLayout(self.group)
        self.lbl_mod = QLabel("N/A")
        self.lbl_pulse = QLabel("N/A")
        self.lbl_iq = QLabel("N/A")

        form.addRow("Modulation:", self.lbl_mod)
        form.addRow("Pulse:", self.lbl_pulse)
        form.addRow("IQ Params:", self.lbl_iq)

    def update_info(self, config):
        if not config:
            self.lbl_mod.setText("Empty")
            self.lbl_pulse.setText("Empty")
            self.lbl_iq.setText("Empty")
            return

        self.lbl_mod.setText(f"{config.get('mod_scheme')} ({config.get('bit_mapping')})")
        self.lbl_pulse.setText(f"{config.get('pulse_type')} (a={config.get('roll_off')})")
        self.lbl_iq.setText(f"Freq: {config.get('carrier_freq')}, Phase: {config.get('phase_offset')}")


class MediaPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        group = QGroupBox("6. Media Player")
        layout.addWidget(group)

        vbox = QVBoxLayout(group)
        self.info_lbl = QLabel("Playback Status: Idle")
        vbox.addWidget(self.info_lbl)

        hbox = QHBoxLayout()
        hbox.addWidget(QPushButton("Play"))
        hbox.addWidget(QPushButton("Stop"))
        vbox.addLayout(hbox)

class FooterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Assuming simple footer for layout purposes
        layout = QHBoxLayout(self)
        layout.addStretch()
        self.btn_restart = QPushButton("Restart Application")
        layout.addWidget(self.btn_restart)