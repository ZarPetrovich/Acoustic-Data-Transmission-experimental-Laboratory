from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Signal
from src.dataclasses.dataclass_models import (
    PulseUpdateTask, ModSchemeUpdateTask,
    BitstreamUpdateTask, CarrierUpdateTask
)

from .pulse_shaping import PulseShapingWidget
from .mod_scheme import ModSchemeWidget
from .bitstream import BitstreamWidget
from .iq_modulator import IQModulatorWidget
from .media_player import MediaPlayerWidget

class ControlWidget(QWidget):

    sig_pulse_ui_event = Signal(PulseUpdateTask)
    sig_mod_ui_event = Signal(ModSchemeUpdateTask)
    sig_bitstream_ui_event = Signal(BitstreamUpdateTask)
    sig_carrier_ui_event = Signal(CarrierUpdateTask)

    sig_clear_plots = Signal()
    sig_export_pulse_path = Signal(str)

    # Media Player Signals
    sig_play_pressed = Signal()
    sig_stop_pressed = Signal()
    sig_export_wav_path = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)


        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        self.vbox = QVBoxLayout(content_widget)


        self.pulse_group = PulseShapingWidget()
        self.mod_group = ModSchemeWidget()
        self.bitstream_group = BitstreamWidget()
        self.iq_group = IQModulatorWidget()
        self.media_group = MediaPlayerWidget()


        self.vbox.addWidget(self.pulse_group)
        self.vbox.addWidget(self.mod_group)
        self.vbox.addWidget(self.bitstream_group)
        self.vbox.addWidget(self.iq_group)
        self.vbox.addWidget(self.media_group)
        self.vbox.addStretch()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)


        self.pulse_group.sig_changed.connect(self.sig_pulse_ui_event)
        self.pulse_group.sig_export_pulse_path.connect(self.sig_export_pulse_path)

        self.mod_group.sig_changed.connect(self.sig_mod_ui_event)

        self.bitstream_group.sig_changed.connect(self.sig_bitstream_ui_event)
        self.bitstream_group.sig_clear_requested.connect(self.sig_clear_plots)

        self.iq_group.sig_modulate_clicked.connect(self.sig_carrier_ui_event)

        self.media_group.sig_play.connect(self.sig_play_pressed)
        self.media_group.sig_stop.connect(self.sig_stop_pressed)
        self.media_group.sig_export_wav.connect(self.sig_export_wav_path)