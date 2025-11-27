import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QScrollArea, QGroupBox, QLabel, QSlider, QComboBox, QAbstractButton,
    QPushButton, QRadioButton, QButtonGroup, QSizePolicy, QFrame, QFormLayout,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


# --- Custom Plot Placeholder Widget ---
class MatrixPlotPlaceholder(QWidget):
    """
    Placeholder for plots in the comparison matrix, now supporting two stacked sub-plots:
    1. Live Signal (Top) - Dynamically updated by controls.
    2. Saved Signal (Bottom) - Statically set (for future use).
    """
    def __init__(self, title, role, parent=None):
        super().__init__(parent)
        self.role = role
        self.setObjectName(f"MatrixPlotPlaceholder_{role}")

        self.setMinimumSize(250, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("PlotTitleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.plot_live_widget = QWidget()
        self.plot_live_widget.setObjectName("LivePlot")
        layout.addWidget(self.plot_live_widget, 1)

        self.plot_saved_widget = QWidget()
        self.plot_saved_widget.setObjectName("SavedPlot")
        layout.addWidget(self.plot_saved_widget, 1)


# --- Media Player Placeholder Widget ---
class MediaPlayerPlaceholder(QGroupBox):
    """
    Placeholder for the media player which displays the configuration
    of the currently selected saved slot for playback.
    """
    def __init__(self, parent=None):
        super().__init__("6. Signal Playback", parent)
        self.setObjectName("MediaPlayerGroup")

        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(10, 20, 10, 10)

        slot_select_group = QGroupBox("Select Slot for Playback")
        slot_select_group.setObjectName("PlaybackSlotGroup")
        slot_buttons_layout = QHBoxLayout(slot_select_group)

        self.playback_slot_group = QButtonGroup(self)
        self.playback_slot_group.setExclusive(True)

        for i in range(1, 5):
            radio = QRadioButton(f"Slot {i}")
            radio.setObjectName(f"PlaybackRadio_{i}")
            self.playback_slot_group.addButton(radio, i - 1)
            slot_buttons_layout.addWidget(radio)

        self.playback_slot_group.buttons()[0].setChecked(True)
        main_vbox.addWidget(slot_select_group)

        self.info_label = QLabel("Select a slot (1-4) above to view its saved configuration here.")
        self.info_label.setObjectName("MediaPlayerInfoLabel")
        self.info_label.setWordWrap(True)
        main_vbox.addWidget(self.info_label)

        control_hbox = QHBoxLayout()
        control_hbox.setSpacing(10)

        self.play_button = QPushButton("▶️ Play")
        self.stop_button = QPushButton("⏹️ Stop")
        self.loop_checkbox = QRadioButton("Loop Playback")
        self.play_button.setDisabled(True)
        self.stop_button.setDisabled(True)

        control_hbox.addStretch(1)
        control_hbox.addWidget(self.play_button)
        control_hbox.addWidget(self.stop_button)
        control_hbox.addWidget(self.loop_checkbox)
        control_hbox.addStretch(1)

        main_vbox.addLayout(control_hbox)


# --- Config Summary Widget ---
class ConfigSummary(QWidget):
    """
    Displays the detailed configuration metadata for the SAVED signal currently
    selected for comparison (the BASELINE signal).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ConfigSummaryWidget")

        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(0, 0, 0, 0)

        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.mod_scheme_label = QLabel("N/A")
        self.pulse_type_label = QLabel("N/A")
        self.roll_off_label = QLabel("N/A")
        self.bit_mapping_label = QLabel("N/A")
        self.carrier_freq_label = QLabel("N/A")
        self.phase_offset_label = QLabel("N/A")

        self.form_layout.addRow("Modulation Scheme:", self.mod_scheme_label)
        self.form_layout.addRow("Pulse Type:", self.pulse_type_label)
        self.form_layout.addRow("Roll-off Factor (α):", self.roll_off_label)
        self.form_layout.addRow("Bit Mapping:", self.bit_mapping_label)
        self.form_layout.addRow("Carrier Frequency (fc):", self.carrier_freq_label)
        self.form_layout.addRow("Phase Offset:", self.phase_offset_label)

        main_vbox.addLayout(self.form_layout)


# --- Main Application Window ---
class SDRPlaygroundMatrix(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDR Playground: Dynamic Matrix View (Pulse/Constellation)")
        self.resize(1200, 800)

        self._setup_ui()

    def _setup_ui(self):
        central_container = QWidget()
        self.setCentralWidget(central_container)

        main_vbox = QVBoxLayout(central_container)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        content_hbox = QWidget()
        content_hbox.setObjectName("ContentArea")
        main_h_layout = QHBoxLayout(content_hbox)
        main_h_layout.setContentsMargins(10, 10, 10, 10)

        control_panel = self._create_control_area()
        control_panel.setObjectName("ControlPanel")
        main_h_layout.addWidget(control_panel, 30)

        plot_container = self._create_matrix_area()
        plot_container.setObjectName("PlotMatrixArea")
        main_h_layout.addWidget(plot_container, 70)

        main_vbox.addWidget(content_hbox, 1)

        footer = self._create_footer_segment()
        footer.setObjectName("FooterSegment")
        main_vbox.addWidget(footer, 0)

    def _create_control_area(self):
        scroll_widget = QWidget()
        vbox = QVBoxLayout(scroll_widget)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        vbox.addWidget(QGroupBox("1. Pulse Shaping"))  # Placeholder for Pulse Shaping
        vbox.addWidget(QGroupBox("2. Constellation Bit Mapping"))  # Placeholder for Constellation
        vbox.addWidget(QGroupBox("3. IQ Modulator"))  # Placeholder for IQ Modulator
        vbox.addWidget(QGroupBox("4. Save Baseline Signal"))  # Placeholder for Save Config
        vbox.addWidget(QGroupBox("5. Selected Baseline Parameters"))  # Placeholder for Config Summary

        vbox.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        return scroll_area

    def _create_matrix_area(self):
        main_widget = QWidget()
        main_vbox = QVBoxLayout(main_widget)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(15)

        title_label = QLabel("Matrix Comparison View")
        title_label.setObjectName("MatrixTitle")
        title_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        main_vbox.addWidget(title_label)

        desc_label = QLabel(
            "The **Top slot** updates dynamically with the controls. "
            "The **Bottom slot** shows the configuration saved in the currently selected **Slot 1-4 (in control panel)**."
        )
        desc_label.setObjectName("MatrixDescription")
        main_vbox.addWidget(desc_label)

        plot_grid_widget = QWidget()
        grid = QGridLayout(plot_grid_widget)
        grid.setSpacing(15)

        grid.addWidget(MatrixPlotPlaceholder("Pulse Shape (Time)", "Pulse"), 0, 0)
        grid.addWidget(MatrixPlotPlaceholder("Constellation/EVM", "Constellation"), 0, 1)
        grid.addWidget(MatrixPlotPlaceholder("Baseband I/Q (Time)", "BasebandTime"), 1, 0)
        grid.addWidget(MatrixPlotPlaceholder("Baseband FFT (Frequency)", "BasebandFFT"), 1, 1)

        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        main_vbox.addWidget(plot_grid_widget, 3)
        main_vbox.addWidget(MediaPlayerPlaceholder(self), 1)

        return main_widget

    def _create_footer_segment(self):
        footer_widget = QWidget()
        footer_widget.setObjectName("AppFooter")

        h_layout = QHBoxLayout(footer_widget)
        h_layout.setContentsMargins(10, 5, 10, 5)
        h_layout.setSpacing(10)

        h_layout.addStretch(1)
        h_layout.addWidget(QPushButton("Restart Application"))
        h_layout.addWidget(QPushButton("Exit Application"))

        return footer_widget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SDRPlaygroundMatrix()
    window.show()
    sys.exit(app.exec())