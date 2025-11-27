import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QScrollArea, QGroupBox, QLabel, QSlider, QComboBox, QAbstractButton,
    QPushButton, QRadioButton, QButtonGroup, QSizePolicy, QFrame, QFormLayout,
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, Slot, QTimer, Signal
import json

# --- Custom Plot Placeholder Widget (No Changes) ---
class MatrixPlotPlaceholder(QWidget):
    """
    Placeholder for plots in the comparison matrix, now supporting two stacked sub-plots:
    1. Live Signal (Top) - Dynamically updated by controls.
    2. Saved Signal (Bottom) - Statically set (for future use).
    """
    def __init__(self, title, role, parent=None):
        super().__init__(parent)
        self.role = role # e.g., 'Pulse', 'Constellation', 'Baseband', 'Spectrum'
        self.setObjectName(f"MatrixPlotPlaceholder_{role}")

        self.setMinimumSize(250, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Main layout for the slot
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("PlotTitleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # --- Slot A: Live Signal (Top Half) ---
        self.plot_live_widget = QWidget()
        self.plot_live_widget.setObjectName("LivePlot")
        vbox_A = QVBoxLayout(self.plot_live_widget)
        vbox_A.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_label_live = QLabel('LIVE: Configuring...')
        self.content_label_live.setObjectName("LiveContentLabel")
        vbox_A.addWidget(self.content_label_live)
        layout.addWidget(self.plot_live_widget, 1) # Stretch factor 1

        # --- Slot B: Saved Signal (Bottom Half) ---
        self.plot_saved_widget = QWidget()
        self.plot_saved_widget.setObjectName("SavedPlot")
        vbox_B = QVBoxLayout(self.plot_saved_widget)
        vbox_B.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_label_saved = QLabel('SAVED: Baseline not set')
        self.content_label_saved.setObjectName("SavedContentLabel")
        vbox_B.addWidget(self.content_label_saved)
        layout.addWidget(self.plot_saved_widget, 1) # Stretch factor 1

        self.current_signal_live_name = None

    def update_live_content(self, name, signal_path):
        """Updates the Live (Top) slot. Called whenever a parameter changes."""
        self.current_signal_live_name = name
        self.content_label_live.setText(f'LIVE: {name}')

        # Simulate update flash using a temporary object property for QSS targeting
        self.plot_live_widget.setProperty("isUpdating", "true")
        self.plot_live_widget.style().polish(self.plot_live_widget)
        # Use QTimer.singleShot for a thread-safe, non-blocking delay
        QTimer.singleShot(300, lambda: self._clear_update_property(self.plot_live_widget))

    def update_saved_content(self, name):
        """
        Updates the Saved (Bottom) slot based on the content of the currently selected save slot
        from the control panel.
        """
        self.content_label_saved.setText(name)
        # Simulate update flash only if a specific configuration was passed
        if "Baseline not set" not in name:
            self.plot_saved_widget.setProperty("isUpdating", "true")
            self.plot_saved_widget.style().polish(self.plot_saved_widget)
            QTimer.singleShot(300, lambda: self._clear_update_property(self.plot_saved_widget))

    def _clear_update_property(self, widget):
        """Helper to clear the QSS update property."""
        widget.setProperty("isUpdating", "false")
        widget.style().polish(widget)


# --- Media Player Placeholder Widget (Simplified) ---
class MediaPlayerPlaceholder(QGroupBox):
    """
    Placeholder for the media player which displays the configuration
    of the currently selected saved slot for playback.
    """
    def __init__(self, parent=None):
        super().__init__("6. Signal Playback", parent)
        self.setObjectName("MediaPlayerGroup")

        # Internal state for which slot the player is targeting (0-3)
        self.selected_playback_slot = 0

        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(10, 20, 10, 10)

        # 1. Slot Selection for Playback (Independent)
        slot_select_group = QGroupBox("Select Slot for Playback")
        slot_select_group.setObjectName("PlaybackSlotGroup")
        slot_buttons_layout = QHBoxLayout(slot_select_group)
        slot_buttons_layout.setContentsMargins(5, 5, 5, 5)

        self.playback_slot_group = QButtonGroup(self)
        self.playback_slot_group.setExclusive(True)

        for i in range(1, 5):
            radio = QRadioButton(f"Slot {i}")
            radio.setObjectName(f"PlaybackRadio_{i}")
            self.playback_slot_group.addButton(radio, i - 1)
            slot_buttons_layout.addWidget(radio)

        self.playback_slot_group.buttons()[0].setChecked(True) # Default Slot 1 selected
        self.playback_slot_group.buttonClicked.connect(self._handle_playback_slot_selection)

        main_vbox.addWidget(slot_select_group)

        # 2. Current Selected Signal Info
        self.info_label = QLabel("Select a slot (1-4) above to view its saved configuration here.")
        self.info_label.setObjectName("MediaPlayerInfoLabel")
        self.info_label.setWordWrap(True)
        main_vbox.addWidget(self.info_label)

        # 3. Control Buttons (Placeholder for Play/Stop/Loop)
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

    @Slot(QAbstractButton)
    def _handle_playback_slot_selection(self, button: QAbstractButton):
        """Updates the internal playback slot index and refreshes the display."""
        self.selected_playback_slot = self.playback_slot_group.id(button)
        # The parent (SDRPlaygroundMatrix) holds the saved_configs list.
        self.update_player_display(self.parent().saved_configs)

    @Slot(list)
    def update_player_display(self, saved_configs: list | None):
        """
        Updates the display based on the internally selected slot and the full list of saved configs.
        """
        config = saved_configs[self.selected_playback_slot] if saved_configs and len(saved_configs) > self.selected_playback_slot else None
        slot_number = self.selected_playback_slot + 1

        if config is None:
            self.info_label.setText(
                f"**Slot {slot_number}** is currently EMPTY. "
                f"Store an active signal configuration in Slot {slot_number} above to enable playback."
            )
            self.play_button.setDisabled(True)
            self.stop_button.setDisabled(True)
        else:
            name = (
                f"**Loaded Signal from Slot {slot_number}:** {config['mod_scheme']} + {config['pulse_type']}(α={config['roll_off']:.2f}). "
                f"Mapping: {config['bit_mapping']} | Carrier: {config['carrier_freq']} Unit, Phase: {config['phase_offset']}°"
            )
            self.info_label.setText(name)
            self.play_button.setDisabled(False)
            self.stop_button.setDisabled(False)

        # Simulate update flash on the group box
        self.setProperty("isUpdating", "true")
        self.style().polish(self)
        QTimer.singleShot(300, lambda: self._clear_update_property(self))

    def _clear_update_property(self, widget):
        widget.setProperty("isUpdating", "false")
        widget.style().polish(widget)


# --- Config Summary Widget (Now displays the SELECTED BASELINE config) ---
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

        # Setup labels for dynamic update
        self.mod_scheme_label = QLabel("N/A")
        self.pulse_type_label = QLabel("N/A")
        self.roll_off_label = QLabel("N/A")
        self.bit_mapping_label = QLabel("N/A")
        self.carrier_freq_label = QLabel("N/A")
        self.phase_offset_label = QLabel("N/A")


        self.mod_scheme_label.setObjectName("MetadataValue")
        self.pulse_type_label.setObjectName("MetadataValue")
        self.roll_off_label.setObjectName("MetadataValue")
        self.bit_mapping_label.setObjectName("MetadataValue")
        self.carrier_freq_label.setObjectName("MetadataValue")
        self.phase_offset_label.setObjectName("MetadataValue")


        self.form_layout.addRow("Modulation Scheme:", self.mod_scheme_label)
        self.form_layout.addRow("Pulse Type:", self.pulse_type_label)
        self.form_layout.addRow("Roll-off Factor (α):", self.roll_off_label)
        self.form_layout.addRow("Bit Mapping:", self.bit_mapping_label)
        self.form_layout.addRow("Carrier Frequency (fc):", self.carrier_freq_label)
        self.form_layout.addRow("Phase Offset:", self.phase_offset_label)

        main_vbox.addLayout(self.form_layout)

        self.update_metadata(None) # Initialize display

    @Slot(dict)
    def update_metadata(self, config: dict | None):
        """Updates the metadata fields based on the provided SAVED configuration dictionary."""
        if config is None:
            text = "<i style='color:#888;'>No signal saved in this slot.</i>"
            self.mod_scheme_label.setText(text)
            self.pulse_type_label.setText(text)
            self.roll_off_label.setText(text)
            self.bit_mapping_label.setText(text)
            self.carrier_freq_label.setText(text)
            self.phase_offset_label.setText(text)

        else:
            self.mod_scheme_label.setText(config.get('mod_scheme', 'N/A'))
            self.pulse_type_label.setText(config.get('pulse_type', 'N/A'))

            roll_off = config.get('roll_off')
            if roll_off is not None:
                self.roll_off_label.setText(f"{roll_off:.2f}")
            else:
                self.roll_off_label.setText("N/A")

            self.bit_mapping_label.setText(config.get('bit_mapping', 'N/A'))

            carrier_freq = config.get('carrier_freq')
            if carrier_freq is not None:
                self.carrier_freq_label.setText(f"{carrier_freq} Unit")
            else:
                self.carrier_freq_label.setText("N/A")

            phase_offset = config.get('phase_offset')
            if phase_offset is not None:
                self.phase_offset_label.setText(f"{phase_offset}°")
            else:
                self.phase_offset_label.setText("N/A")

        # Simulate update flash
        self.setProperty("isUpdating", "true")
        self.style().polish(self)
        QTimer.singleShot(300, lambda: self._clear_update_property(self))

    def _clear_update_property(self, widget):
        widget.setProperty("isUpdating", "false")
        widget.style().polish(widget)


# --- Main Application Window ---
class SDRPlaygroundMatrix(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDR Playground: Dynamic Matrix View (Pulse/Constellation)")
        self.resize(1200, 800)

        # Live Configuration (constantly changing)
        self.current_live_config = {
            "pulse_type": "RRC",
            "roll_off": 0.50,
            "mod_scheme": "QPSK",
            "bit_mapping": "Gray",
            # New IQ Modulator Parameters
            "carrier_freq": 550, # Scaled frequency for demo
            "phase_offset": 0.0,
        }

        # Saved Configurations (list of 4 slots, initialized to None)
        self.saved_configs = [None] * 4
        # Index of the currently selected slot in the CONTROL PANEL (0, 1, 2, or 3)
        self.selected_save_slot = 0

        # Store reference to the media player and config summary
        self.media_player_placeholder = None
        self.config_summary = None # Renamed reference

        self._setup_ui()
        self._update_live_config_text()
        self._update_saved_display() # Initialize saved display

    # --- Core Application Logic ---
    @Slot()
    def restart_application(self):
        """Simulates restarting the application by simply printing a message."""
        print("--- RESTART APPLICATION TRIGGERED ---")
        self.statusBar().showMessage("Application Restart Simulated.", 3000)

    def _setup_ui(self):
        # Use a central QWidget to hold the main VBox layout
        central_container = QWidget()
        self.setCentralWidget(central_container)

        # Main vertical layout for the whole window (Controls + Matrix + Footer)
        main_vbox = QVBoxLayout(central_container)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)

        # Content area (Controls and Matrix)
        content_hbox = QWidget()
        content_hbox.setObjectName("ContentArea")
        main_h_layout = QHBoxLayout(content_hbox)
        main_h_layout.setContentsMargins(10, 10, 10, 10)

        # LEFT COLUMN (Controls)
        control_panel = self._create_control_area()
        control_panel.setObjectName("ControlPanel")
        main_h_layout.addWidget(control_panel, 30)

        # RIGHT COLUMN (Matrix Comparison Plot + Media Player)
        plot_container = self._create_matrix_area()
        plot_container.setObjectName("PlotMatrixArea")
        main_h_layout.addWidget(plot_container, 70)

        # Add content area to the main vertical layout (with stretch to fill space)
        main_vbox.addWidget(content_hbox, 1)

        # FOOTER Segment (Non-stretching)
        footer = self._create_footer_segment()
        footer.setObjectName("FooterSegment")
        main_vbox.addWidget(footer, 0)

        # Link all plot widgets for global updates
        self.plot_widgets = [
            self.plot1_pulse,
            self.plot2_constellation_placeholder,
            self.plot3_baseband_time_placeholder,
            self.plot4_baseband_fft_placeholder
        ]


    # --- Control Panel Widgets (Updated numbering and ConfigSummary placement) ---

    def _create_control_area(self):
        """Creates the scrollable left control panel."""
        scroll_widget = QWidget()
        vbox = QVBoxLayout(scroll_widget)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. PULSE SHAPING CONFIGURATION SECTION
        vbox.addWidget(self._create_pulse_config_group())

        # 2. CONSTELLATION/BIT MAPPING CONFIGURATION SECTION
        vbox.addWidget(self._create_constellation_config_group())

        # 3. IQ MODULATOR CONFIGURATION SECTION
        vbox.addWidget(self._create_iq_modulator_group())

        # 4. SAVE BASELINE SIGNAL SECTION
        vbox.addWidget(self._create_save_config_group())

        # 5. SELECTED BASELINE CONFIGURATION SUMMARY (Now displays the saved config)
        summary_group = QGroupBox("5. Selected Baseline Parameters")
        summary_layout = QVBoxLayout(summary_group)
        self.config_summary = ConfigSummary() # Reroute to display saved config
        summary_layout.addWidget(self.config_summary)
        summary_group.setObjectName("ConfigSummaryGroup")
        vbox.addWidget(summary_group)


        # 6. LIVE STATUS LABEL (Informal summary, still tracking live configuration)
        # Note: This label is kept to still show a *live* summary of the controls for immediate feedback
        self.live_status_label = QLabel("Current Live Signal: N/A")
        self.live_status_label.setObjectName("LiveStatusLabel")
        vbox.addWidget(self.live_status_label)

        vbox.addStretch()

        # Wrap in QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        return scroll_area

    def _create_pulse_config_group(self):
        """Group for setting pulse shaping parameters."""
        group = QGroupBox("1. Pulse Shaping")
        group.setObjectName("PulseConfigGroup")
        layout = QVBoxLayout(group)

        # Pulse Type
        layout.addWidget(QLabel("Pulse Type:"))
        self.pulse_combo = QComboBox()
        self.pulse_combo.setObjectName("PulseTypeCombo")
        self.pulse_combo.addItems(["RRC", "Rectangular", "Gaussian"])
        layout.addWidget(self.pulse_combo)

        # Roll-off Slider
        layout.addWidget(QLabel("Roll-off Factor (α):"))
        h_roll_off = QHBoxLayout()
        self.slider_roll_off = QSlider(Qt.Orientation.Horizontal)
        self.slider_roll_off.setObjectName("RollOffSlider")
        self.slider_roll_off.setRange(0, 100)
        self.slider_roll_off.setValue(50)
        self.label_roll_off = QLabel("0.50")
        h_roll_off.addWidget(self.slider_roll_off)
        h_roll_off.addWidget(self.label_roll_off)
        layout.addLayout(h_roll_off)

        # Connect signals
        self.slider_roll_off.valueChanged.connect(self._handle_pulse_change)
        self.pulse_combo.currentTextChanged.connect(self._handle_pulse_change)

        return group

    def _create_constellation_config_group(self):
        """Group for setting modulation and bit mapping parameters."""
        group = QGroupBox("2. Constellation Bit Mapping")
        group.setObjectName("ConstellationConfigGroup")
        layout = QVBoxLayout(group)

        # Modulation Type (Radio Buttons)
        layout.addWidget(QLabel("Modulation Scheme:"))
        mod_group_widget = QWidget()
        mod_layout = QHBoxLayout(mod_group_widget)
        self.mod_group = QButtonGroup()

        for text in ["QPSK", "16-QAM", "BPSK"]:
            radio = QRadioButton(text)
            radio.setObjectName(f"ModRadio_{text}")
            self.mod_group.addButton(radio)
            mod_layout.addWidget(radio)
        self.mod_group.buttons()[0].setChecked(True) # Default QPSK
        layout.addWidget(mod_group_widget)

        # Bit Mapping Type (Combo Box)
        layout.addWidget(QLabel("Bit Mapping Type:"))
        self.bit_mapping_combo = QComboBox()
        self.bit_mapping_combo.setObjectName("BitMappingCombo")
        # Options that generally apply to QPSK/16-QAM
        self.bit_mapping_combo.addItems(["Gray", "Binary", "Differential"])
        layout.addWidget(self.bit_mapping_combo)

        # Connect signals
        self.mod_group.buttonClicked.connect(self._handle_constellation_change)
        self.bit_mapping_combo.currentTextChanged.connect(self._handle_constellation_change)

        return group

    def _create_iq_modulator_group(self):
        """Group for setting IQ Modulator parameters (Carrier Frequency and Phase Offset)."""
        group = QGroupBox("3. IQ Modulator")
        group.setObjectName("IQModulatorGroup")
        layout = QVBoxLayout(group)

        # Carrier Frequency Slider
        layout.addWidget(QLabel("Carrier Frequency (fc, Scaled):"))
        h_freq = QHBoxLayout()
        self.slider_carrier_freq = QSlider(Qt.Orientation.Horizontal)
        self.slider_carrier_freq.setObjectName("CarrierFreqSlider")
        self.slider_carrier_freq.setRange(100, 1000) # 100 to 1000 units (e.g., Hz/kHz/MHz)
        self.slider_carrier_freq.setValue(self.current_live_config["carrier_freq"])
        self.label_carrier_freq = QLabel(f"{self.current_live_config['carrier_freq']} Unit")
        h_freq.addWidget(self.slider_carrier_freq)
        h_freq.addWidget(self.label_carrier_freq)
        layout.addLayout(h_freq)

        # Phase Offset Slider
        layout.addWidget(QLabel("Phase Offset (degrees):"))
        h_phase = QHBoxLayout()
        self.slider_phase_offset = QSlider(Qt.Orientation.Horizontal)
        self.slider_phase_offset.setObjectName("PhaseOffsetSlider")
        self.slider_phase_offset.setRange(0, 360)
        self.slider_phase_offset.setValue(0)
        self.label_phase_offset = QLabel("0°")
        h_phase.addWidget(self.slider_phase_offset)
        h_phase.addWidget(self.label_phase_offset)
        layout.addLayout(h_phase)

        # Connect signals
        self.slider_carrier_freq.valueChanged.connect(self._handle_iq_modulator_change)
        self.slider_phase_offset.valueChanged.connect(self._handle_iq_modulator_change)

        return group


    def _create_save_config_group(self):
        """Group for saving the current configuration to a slot."""
        group = QGroupBox("4. Save Baseline Signal")
        group.setObjectName("SaveConfigGroup")
        layout = QVBoxLayout(group)

        # Slot Selection Radio Buttons (For saving/viewing plots' saved state)
        self.slot_group = QButtonGroup(self)
        self.slot_group.setExclusive(True)

        slot_buttons_widget = QWidget()
        slot_buttons_layout = QHBoxLayout(slot_buttons_widget)

        for i in range(1, 5):
            radio = QRadioButton(f"Slot {i}")
            radio.setObjectName(f"SlotRadio_{i}")
            self.slot_group.addButton(radio, i - 1) # i-1 is the list index (0-3)
            slot_buttons_layout.addWidget(radio)

        self.slot_group.buttons()[0].setChecked(True) # Default Slot 1 selected

        # Connect signal: changes the currently selected slot index for plots/saving
        self.slot_group.buttonClicked.connect(self._handle_slot_selection)

        layout.addWidget(slot_buttons_widget)

        # Store Button
        self.store_button = QPushButton("Store Active Signal")
        self.store_button.setObjectName("StoreButton")
        self.store_button.clicked.connect(self._save_active_config)
        layout.addWidget(self.store_button)

        return group

    # --- Handlers for Dynamic Updates and Saving ---

    @Slot()
    def _handle_pulse_change(self):
        """Updates internal state based on Pulse Group changes."""
        alpha = self.slider_roll_off.value() / 100.0
        self.current_live_config["roll_off"] = alpha
        self.current_live_config["pulse_type"] = self.pulse_combo.currentText()
        self.label_roll_off.setText(f"{alpha:.2f}")
        self._update_live_config_text()

    @Slot()
    def _handle_constellation_change(self):
        """Updates internal state based on Constellation Group changes."""
        checked_button = self.mod_group.checkedButton()
        if checked_button:
            self.current_live_config["mod_scheme"] = checked_button.text()
            self.current_live_config["bit_mapping"] = self.bit_mapping_combo.currentText()
            self._update_live_config_text()

    @Slot()
    def _handle_iq_modulator_change(self):
        """Updates internal state based on IQ Modulator Group changes."""
        carrier_freq = self.slider_carrier_freq.value()
        phase_offset = self.slider_phase_offset.value()

        self.current_live_config["carrier_freq"] = carrier_freq
        self.current_live_config["phase_offset"] = phase_offset

        self.label_carrier_freq.setText(f"{carrier_freq} Unit")
        self.label_phase_offset.setText(f"{phase_offset}°")

        self._update_live_config_text()


    @Slot(QAbstractButton)
    def _handle_slot_selection(self, button: QAbstractButton):
        """
        Updates the index of the currently selected save slot for plots/saving
        and refreshes the plots' saved display AND the Baseline Metadata Summary.
        """
        self.selected_save_slot = self.slot_group.id(button)
        self._update_plots_saved_view()
        self._update_baseline_metadata() # <-- NEW: Update Metadata box

    @Slot()
    def _save_active_config(self):
        """Saves the current live configuration into the selected slot."""
        config_copy = self.current_live_config.copy()
        self.saved_configs[self.selected_save_slot] = config_copy

        slot_id = self.selected_save_slot + 1
        print(f"Signal saved to Slot {slot_id}: {config_copy}")

        self.statusBar().showMessage(f"Active signal saved to Slot {slot_id}.", 3000)

        # 1. Update the plots' saved view (since the content of the selected slot changed)
        self._update_plots_saved_view()

        # 2. Update the Baseline Metadata (since the selected slot now has new data)
        self._update_baseline_metadata()

        # 3. Notify the independent media player that the global list has new content
        if self.media_player_placeholder:
            self.media_player_placeholder.update_player_display(self.saved_configs)


    def _get_config_name(self, config):
        """Helper to generate a readable name for a config dictionary."""
        if config is None:
            return 'SAVED: Baseline not set'

        mod_details = (
            f"Mod: {config['mod_scheme']} + {config['pulse_type']}(α={config['roll_off']:.2f}) "
            f"[Map: {config['bit_mapping']}]"
        )
        iq_details = (
            f" | IQ: fc={config['carrier_freq']} Unit, φ={config['phase_offset']}°"
        )

        return f"SAVED: {mod_details}{iq_details}"

    def _update_live_config_text(self):
        """Updates the Live (Top) pane of all relevant matrix plots and the Live Status Label."""
        config = self.current_live_config
        live_name = self._get_config_name(config).replace('SAVED: ', 'LIVE: ')
        live_path = f"Mod: {config['mod_scheme']}, Pulse: {config['pulse_type']}, Map: {config['bit_mapping']}"

        # 1. Update the informal status label (Group 6) with the live configuration
        self.live_status_label.setText(f"Current Live Signal: {live_name}")

        # 2. Global Update: Update the 'Live' part of the custom MatrixPlotPlaceholder widgets
        for plot in self.plot_widgets:
            if isinstance(plot, MatrixPlotPlaceholder):
                plot.update_live_content(live_name, live_path)

    def _update_plots_saved_view(self):
        """
        Updates the Saved (Bottom) pane of all plots based ONLY on the
        currently selected control panel save slot.
        """
        current_saved_config = self.saved_configs[self.selected_save_slot]
        saved_name = self._get_config_name(current_saved_config)

        # Global Update for Plots (Bottom Half)
        for plot in self.plot_widgets:
            if isinstance(plot, MatrixPlotPlaceholder):
                plot.update_saved_content(saved_name)

    @Slot()
    def _update_baseline_metadata(self):
        """
        Updates the dedicated Metadata panel (Group 5) with the configuration
        of the signal currently selected for comparison (the selected slot).
        """
        current_saved_config = self.saved_configs[self.selected_save_slot]
        if self.config_summary:
            self.config_summary.update_metadata(current_saved_config)


    def _update_saved_display(self):
        """
        Initializes the saved view for plots, the media player, and the baseline metadata.
        Called once on startup.
        """
        # 1. Update Plots' Saved View (tied to the default selected_save_slot=0)
        self._update_plots_saved_view()

        # 2. Update Baseline Metadata (tied to the default selected_save_slot=0)
        self._update_baseline_metadata()

        # 3. Initialize Media Player Display (It will select Slot 1 by default)
        if self.media_player_placeholder:
            self.media_player_placeholder.update_player_display(self.saved_configs)


    # --- Plot Matrix and Media Player Container (No Changes) ---

    def _create_matrix_area(self):
        """
        Creates the right-hand container holding the 2x2 grid and the media player below it.
        """
        main_widget = QWidget()
        main_vbox = QVBoxLayout(main_widget)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(15) # Spacing between the grid and the player

        # --- Top Half: Matrix Comparison View Title ---
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

        # --- Middle Section: 2x2 Plot Grid ---
        plot_grid_widget = QWidget()
        plot_grid_widget.setObjectName("PlotGridContainer")
        grid = QGridLayout(plot_grid_widget)
        grid.setSpacing(15)

        # Slot 1: Pulse
        self.plot1_pulse = MatrixPlotPlaceholder("Pulse Shape (Time)", "Pulse")
        grid.addWidget(self.plot1_pulse, 0, 0)

        # Slot 2: Constellation
        self.plot2_constellation_placeholder = MatrixPlotPlaceholder("Constellation/EVM", "Constellation")
        grid.addWidget(self.plot2_constellation_placeholder, 0, 1)

        # Slot 3: Baseband Time
        self.plot3_baseband_time_placeholder = MatrixPlotPlaceholder("Baseband I/Q (Time)", "BasebandTime")
        grid.addWidget(self.plot3_baseband_time_placeholder, 1, 0)

        # Slot 4: Baseband FFT
        self.plot4_baseband_fft_placeholder = MatrixPlotPlaceholder("Baseband FFT (Frequency)", "BasebandFFT")
        grid.addWidget(self.plot4_baseband_fft_placeholder, 1, 1)

        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        main_vbox.addWidget(plot_grid_widget, 3)

        # --- Bottom Section: Media Player (Full Width) ---
        self.media_player_placeholder = MediaPlayerPlaceholder(self)
        main_vbox.addWidget(self.media_player_placeholder, 1)

        return main_widget

    def _create_footer_segment(self):
        """Creates the bottom widget containing the Restart and Exit buttons."""
        footer_widget = QWidget()
        footer_widget.setObjectName("AppFooter")

        h_layout = QHBoxLayout(footer_widget)
        h_layout.setContentsMargins(10, 5, 10, 5)
        h_layout.setSpacing(10)

        h_layout.addStretch(1)

        restart_button = QPushButton("Restart Application")
        restart_button.setObjectName("RestartButton")
        restart_button.clicked.connect(self.restart_application)
        h_layout.addWidget(restart_button)

        close_button = QPushButton("Exit Application")
        close_button.setObjectName("ExitButton")
        close_button.clicked.connect(self.close)
        h_layout.addWidget(close_button)

        return footer_widget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SDRPlaygroundMatrix()
    window.show()
    sys.exit(app.exec())