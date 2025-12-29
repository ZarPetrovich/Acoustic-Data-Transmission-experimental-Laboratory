from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QPushButton, QFileDialog
from PySide6.QtCore import Qt, Signal, QTimer
from src.constants import PulseShape
from src.dataclasses.dataclass_models import PulseUpdateTask


class PulseShapingWidget(QGroupBox):
    sig_changed = Signal(PulseUpdateTask)
    sig_export_pulse_path = Signal(str) # Signal to request export from Controller

    def __init__(self, parent=None):
        super().__init__("1. Pulse Shaping", parent)

        # Debounce timer for sliders
        self.pulse_debounce_timer = QTimer(self)
        self.pulse_debounce_timer.setSingleShot(True)
        self.pulse_debounce_timer.setInterval(150)
        self.pulse_debounce_timer.timeout.connect(self._emit_pulse)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # --- Pulse Type ---
        self.pulse_combo = QComboBox()
        self.pulse_combo.addItems([shape.name for shape in PulseShape])
        layout.addWidget(QLabel("Pulse Type:"))
        layout.addWidget(self.pulse_combo)

        # --- Span Slider ---
        self.slider_span = QSlider(Qt.Orientation.Horizontal)
        self.slider_span.setRange(1, 20)
        self.slider_span.setValue(2)
        self.lbl_span = QLabel(str(self.slider_span.value()))

        span_h = QHBoxLayout()
        span_h.addWidget(QLabel("Span:"))
        span_h.addWidget(self.slider_span)
        span_h.addWidget(self.lbl_span)
        layout.addLayout(span_h)

        # --- Roll-off Slider ---
        self.slider_roll = QSlider(Qt.Orientation.Horizontal)
        self.slider_roll.setRange(1, 100)
        self.slider_roll.setValue(50)
        self.lbl_roll = QLabel("0.50")

        roll_h = QHBoxLayout()
        roll_h.addWidget(QLabel("Roll-off (α):"))
        roll_h.addWidget(self.slider_roll)
        roll_h.addWidget(self.lbl_roll)
        layout.addLayout(roll_h)

        # --- Export Pulse ---
        export_vbox = QVBoxLayout()
        file_path_hbox = QHBoxLayout()
        file_path_hbox.addWidget(QLabel("Export Pulse as JSON"))
        self.btn_export_pulse = QPushButton("Export")
        file_path_hbox.addWidget(self.btn_export_pulse)
        export_vbox.addLayout(file_path_hbox)
        layout.addLayout(export_vbox)

        # --- Connections ---
        self.pulse_combo.currentTextChanged.connect(self._emit_pulse)
        self.slider_span.valueChanged.connect(self._on_slider_visual_update)
        self.slider_roll.valueChanged.connect(self._on_slider_visual_update)
        self.btn_export_pulse.clicked.connect(self._open_export_pulse_dialog)

    def _on_slider_visual_update(self):
        """Instant label updates"""
        self.lbl_span.setText(str(self.slider_span.value()))
        self.lbl_roll.setText(f"{self.slider_roll.value()/100:.2f}")
        self.pulse_debounce_timer.start()

    def _open_export_pulse_dialog(self):
        """Logic migrated from your original widgets.py"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Pulse Signal", "", "Json Files (*.json)")
        if file_path:
            self.sig_export_pulse_path.emit(file_path)

    def _emit_pulse(self):
        """Emits the Transfer Dataclass."""
        task = PulseUpdateTask(
            shape_name=self.pulse_combo.currentText(),
            span=self.slider_span.value(),
            roll_off=self.slider_roll.value() / 100.0
        )

        self.sig_changed.emit(task)