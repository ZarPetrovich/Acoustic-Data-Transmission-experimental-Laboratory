from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
    QPushButton, QGroupBox, QSlider, QComboBox, QRadioButton,
    QButtonGroup, QGridLayout, QFormLayout, QScrollArea, QFrame, QAbstractButton,
    QPushButton, QLineEdit,QFileDialog, QStackedLayout
)

from PySide6.QtCore import Qt, QTimer, Signal, Slot, QRegularExpression, QFileInfo
from PySide6.QtGui import QFont, QRegularExpressionValidator
from src.ui.plot_widgets import PlotWidget, SpectrumContainerWidget, PulseContainerWidget
from src.constants import PulseShape
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton


# ===========================================================
#   Main Widget Classes
#       1. Control Widget: Holds Elements to Control
#           the Application (Left Side) @@@control Widget
#       2. Matrix Widgget: Displays Plot
#       3. MetaData Widget: Shows Current Config
#       4. Media Player Widget: Play/Stop Signals
#       5. Footer Widget
# ===========================================================


#------------------------------------------------------------
# +++++ Control Widget +++++
#------------------------------------------------------------
class ControlWidget(QWidget):

    # SIGNALS
    sig_pulse_changed = Signal(dict)        # Emits {pulse_type, span, roll_off}
    sig_mod_changed = Signal(dict)          # Emits {mod_scheme, mapping}
    sig_bit_stream_changed = Signal(dict)      # Emits {bit_sequence}
    sig_carrier_freq_changed = Signal(dict) # Emits {carrie_freq}
    sig_clear_plots = Signal()              # Emits when clear button is pressed

    sig_save_requested = Signal(int)        # Emits slot_index (0-3) to save to
    sig_slot_selection_changed = Signal(int) # Emits slot_index (0-3) selected for viewing

    # Media Player
    sig_play_button_pressed = Signal()
    sig_stop_button_pressed = Signal()
    sig_export_path = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Debounce timer for bitstream text entry
        self.bitstream_debounce_timer = QTimer(self)
        self.bitstream_debounce_timer.setSingleShot(True)
        self.bitstream_debounce_timer.setInterval(200)  # 200ms delay
        self.bitstream_debounce_timer.timeout.connect(self._emit_bitstream_from_entry)

        # Debounce timer for pulse shape sliders
        self.pulse_debounce_timer = QTimer(self)
        self.pulse_debounce_timer.setSingleShot(True)
        self.pulse_debounce_timer.setInterval(150)  # 150ms delay
        self.pulse_debounce_timer.timeout.connect(self._emit_pulse)

        # Scroll Area setup
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content_widget = QWidget()
        self.vbox = QVBoxLayout(content_widget)

        # 1. Pulse Shaping
        self._init_pulse_group()
        # 2. Constellation
        self._init_constellation_group()
        # 4. Save Controls
        self._init_enter_bitstream()
        # 3. IQ Modulator
        self._init_iq_group()

        self._init_media_player()

        self.vbox.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _init_pulse_group(self):
        group = QGroupBox("1. Pulse Shaping")

        # ---- Set Font Size ----
        self._style_groupbox_title(group)
        layout = QVBoxLayout(group)

        # Pulse Type
        pulse_type_layout = QHBoxLayout()
        pulse_type_layout.addWidget(QLabel("Pulse Type:"))
        self.pulse_combo = QComboBox()
        pulse_type_layout.addWidget(self.pulse_combo)
        layout.addLayout(pulse_type_layout)
        self.set_pulse_shape_map()
        # Span and Roll-off
        sliders_layout = QVBoxLayout()

        # Span
        span_layout = QHBoxLayout()
        span_layout.addWidget(QLabel("Span:"))
        self.slider_span = QSlider(Qt.Orientation.Horizontal)
        self.slider_span.setRange(1, 20)
        self.slider_span.setValue(2)
        self.lbl_span = QLabel(f"{2}")
        span_layout.addWidget(self.slider_span)
        span_layout.addWidget(self.lbl_span)
        sliders_layout.addLayout(span_layout)

        # Roll-off
        rolloff_layout = QHBoxLayout()
        rolloff_layout.addWidget(QLabel("Roll-off (α):"))
        self.slider_roll = QSlider(Qt.Orientation.Horizontal)
        self.slider_roll.setRange(1, 100)
        self.slider_roll.setValue(50)
        self.lbl_roll = QLabel("0.50")
        rolloff_layout.addWidget(self.slider_roll)
        rolloff_layout.addWidget(self.lbl_roll)
        sliders_layout.addLayout(rolloff_layout)

        layout.addLayout(sliders_layout)
        self.vbox.addWidget(group)

        # TODO Deactivate Roll OFF for specific Pulses

        # Internal Connections
        self.pulse_combo.currentTextChanged.connect(self._emit_pulse)  # ComboBox: immediate
        self.slider_span.valueChanged.connect(self._on_pulse_slider_changed)
        self.slider_roll.valueChanged.connect(self._on_pulse_slider_changed)

        self.vbox.addWidget(group)

    def _init_constellation_group(self):
        group = QGroupBox("2. Constellation")
        # ---- Set Font Size ----
        self._style_groupbox_title(group)
        layout = QVBoxLayout(group)

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

        self.vbox.addWidget(group)

    def _init_enter_bitstream(self):
        self.group_bitstream = QGroupBox("3. Bitstream")
        self._style_groupbox_title(self.group_bitstream)

        # *** 1. Use QStackedLayout for state management ***
        self.main_vbox = QVBoxLayout(self.group_bitstream)
        self.stacked_widget = QWidget() # A QWidget to hold the stack
        self.stacked_layout = QStackedLayout(self.stacked_widget)

        # Create the two state widgets
        self._create_manual_entry_widget()
        self._create_imported_file_widget()

        # Add the stacked widget to the group box's main layout
        self.main_vbox.addWidget(self.stacked_widget)

        # Add the global 'Clear All Signals' button below the stack
        self.btn_clear_plots = QPushButton("Clear All Signals & Data")
        self.main_vbox.addWidget(self.btn_clear_plots)

        # Initial state is Manual Entry (index 0)
        self.stacked_layout.setCurrentIndex(0)

        # Connect the global button
        self.btn_clear_plots.clicked.connect(self.sig_clear_plots.emit) # Keep this one

        self.vbox.addWidget(self.group_bitstream)

    def _create_manual_entry_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Status Label (Always shows 'Manual' in this view)
        self.lbl_manual_source = QLabel("Source: Manual Entry (Active)")
        self.lbl_manual_source.setStyleSheet("font-weight: bold; color: green;")
        layout.addWidget(self.lbl_manual_source)

        # Manual Entry Line Edit
        layout.addWidget(QLabel("Add Bitstream manually ( 1 | 0 ): "))
        self.entry_bitstream = QLineEdit()
        regex = QRegularExpression("^[01]+$")
        bit_validator = QRegularExpressionValidator(regex, self)
        self.entry_bitstream.setValidator(bit_validator)
        layout.addWidget(self.entry_bitstream)

        # Import Button
        import_h = QHBoxLayout()
        import_h.addWidget(QLabel("Or Import File"))
        self.btn_import_data = QPushButton("Import Bitstream (.bin)")
        import_h.addWidget(self.btn_import_data)
        layout.addLayout(import_h)

        # Add to stack
        self.stacked_layout.addWidget(widget)

        # Connections for this view
        self.entry_bitstream.textChanged.connect(self._on_bitstream_text_changed)
        self.btn_import_data.clicked.connect(self._open_import_dialog)

    def _create_imported_file_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # File Info Label
        self.lbl_file_info = QLabel("Source: File") # Will be updated dynamically
        self.lbl_file_info.setStyleSheet("font-weight: bold; color: darkorange;")
        layout.addWidget(self.lbl_file_info)

        # Value labels
        form_layout = QFormLayout()
        self.lbl_filename = QLabel("N/A")
        self.lbl_bit_length = QLabel("N/A")
        form_layout.addRow("Filename:", self.lbl_filename)
        form_layout.addRow("Length:", self.lbl_bit_length)
        layout.addLayout(form_layout)

        # Action Buttons
        h_buttons = QHBoxLayout()
        self.btn_view_data = QPushButton("View Full Data")
        self.btn_revert_manual = QPushButton("Revert to Manual Entry")
        h_buttons.addWidget(self.btn_view_data)
        h_buttons.addWidget(self.btn_revert_manual)
        layout.addLayout(h_buttons)

        # Add to stack
        self.stacked_layout.addWidget(widget)

        # Connections for this view
        self.btn_view_data.clicked.connect(self._on_view_data_clicked)
        self.btn_revert_manual.clicked.connect(self._on_revert_to_manual)

        # Store bit sequence internally for viewing
        self._current_bit_sequence = ""

    def _init_iq_group(self):
        group = QGroupBox("4. IQ Modulator")
        # ---- Set Font Size ----
        self._style_groupbox_title(group)

        layout = QVBoxLayout(group)
        layout.addWidget(QLabel("Carrier Frequency:"))

        # Radio Buttons
        self.freq_bg = QButtonGroup(self)
        h_rad = QHBoxLayout()
        for txt in ["440 Hz", "4400 Hz", "8800 Hz"]:
            rb = QRadioButton(txt)
            self.freq_bg.addButton(rb)
            h_rad.addWidget(rb)
        self.freq_bg.buttons()[0].setChecked(True)
        layout.addLayout(h_rad)

        self.btn_modulate = QPushButton("Modulate")
        layout.addWidget(self.btn_modulate)

        self.vbox.addWidget(group)

        # Internal Connections

        self.btn_modulate.clicked.connect(self._emit_carrier_freq)

    def _init_media_player(self):
        group = QGroupBox("6. Media Player")

        self._style_groupbox_title(group)

        layout = QVBoxLayout(group)

        mediaply_box = QHBoxLayout(group) # MAIN H BOX 1/3 PLAY STOP 2/3 Space 3/3 Export

        # ---- PLAY/STOP BUTTON ----
        player_vbox = QVBoxLayout()

        self.info_lbl = QLabel("Playback Status: Idle")
        player_vbox.addWidget(self.info_lbl)

        self.btn_play = QPushButton("Play")
        player_vbox.addWidget(self.btn_play)

        self.btn_stop = QPushButton("Stop")
        player_vbox.addWidget(self.btn_stop)

        player_vbox.addStretch(1)


        # ---- EXPORT VBOX  ----
        export_vbox = QVBoxLayout()
        file_path_hbox = QHBoxLayout()
        export_vbox.addWidget(QLabel("Export Bandpass Signal to .wav File"))
        self.path_line_edit =QLineEdit()
        self.btn_browse_path = QPushButton("Browse")

        file_path_hbox.addWidget(self.path_line_edit)
        file_path_hbox.addWidget(self.btn_browse_path)

        export_vbox.addLayout(file_path_hbox)


        self.btn_export = QPushButton("Export WAV File")
        export_vbox.addWidget(self.btn_export)
        # export_vbox.addWidget(self.btn_browse_path)

        export_vbox.addStretch(1)

        mediaply_box.addLayout(player_vbox, 1)
        mediaply_box.addStretch(1)
        mediaply_box.addLayout(export_vbox, 1)

        layout.addLayout(mediaply_box)

    # --- Internal Emitters  ---

        self.btn_play.clicked.connect(self.sig_play_button_pressed.emit)
        self.btn_stop.clicked.connect(self.sig_stop_button_pressed.emit)
        self.btn_browse_path.clicked.connect(self._open_export_dialog)
        self.btn_export.clicked.connect(self._emit_export_path)

        self.vbox.addWidget(group)


    def _on_pulse_slider_changed(self):
        """Update labels immediately but debounce the signal emission."""
        # Update labels for instant visual feedback
        val_roll_off = self.slider_roll.value() / 100
        val_span = self.slider_span.value()
        self.lbl_span.setText(f"{val_span}")
        self.lbl_roll.setText(f"{val_roll_off:.2f}")

        # Restart debounce timer
        self.pulse_debounce_timer.stop()
        self.pulse_debounce_timer.start()

    def _emit_pulse(self):
        """Emit pulse signal after debounce delay."""
        val_roll_off = self.slider_roll.value() / 100
        val_span = self.slider_span.value()
        self.sig_pulse_changed.emit({
            "pulse_type": PulseShape[self.pulse_combo.currentText()],  # Emit enum value
            "span": val_span,
            "roll_off": val_roll_off,
        })

    def _emit_mod(self):
        self.sig_mod_changed.emit({
            "mod_scheme": self.modulation_bg.checkedButton().text(),
            "bit_mapping": self.map_combo.currentText()
        })

    def _on_bitstream_text_changed(self):
        """Restart the debounce timer on each text change."""
        self.bitstream_debounce_timer.stop()
        self.bitstream_debounce_timer.start()

    def _emit_bitstream_from_entry(self):
        """Emit the bitstream signal after debounce delay."""
        self.sig_bit_stream_changed.emit({
            "bit_seq": self.entry_bitstream.text()
        })

    def _emit_carrier_freq(self):

        carrier_freq = self.freq_bg.checkedButton().text()
        carrier_freq = carrier_freq.split(" ")[0]  # Get numeric part
        self.sig_carrier_freq_changed.emit({
            "carrier_freq": carrier_freq
        })

    def set_pulse_shape_map(self):
        self.pulse_combo.clear()
        self.pulse_combo.addItems([shape.name for shape in PulseShape])  # Use enum names

    def _show_imported_bitstream_dialog(self, bit_sequence: str):
        """Show info and a dialog to display the imported bitstream."""

        class BitstreamDialog(QDialog):
            def __init__(self, bit_sequence, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Imported Bitstream")
                vbox = QVBoxLayout(self)
                text = QTextEdit()
                text.setReadOnly(True)
                text.setText(bit_sequence)
                vbox.addWidget(text)
                btn_close = QPushButton("Close")
                btn_close.clicked.connect(self.accept)
                vbox.addWidget(btn_close)
                self.resize(400, 300)

        dialog = BitstreamDialog(bit_sequence, self)
        dialog.exec()

        # Optionally: self.layout_bitstream.addLayout(hbox) if you want to show this in the UI

    def _open_import_dialog(self):
        # 1. Re-add File Dialog and Reading Logic
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Baseline Data", "", "Binary Files (*.bin)")

        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                raw_data = f.read()

            clean_bit_sequence = "".join(raw_data.split()) # TODO Create FileService Seperation of Concern

            regex = QRegularExpression("^[01]+$")
            bit_validator = QRegularExpressionValidator(regex, self)
            if not regex.match(clean_bit_sequence).hasMatch():
                 # Handle invalid characters gracefully, e.g., show an error dialog
                 print("Imported file contains invalid characters after cleaning. Only '0' and '1' are allowed.")
                 return

            # 2. Update internal state and emit signal (Your existing logic)
            self._current_bit_sequence = clean_bit_sequence
            self.sig_bit_stream_changed.emit({"bit_seq": clean_bit_sequence})

            # 3. Update the File Imported View (Your existing logic)
            file_name = QFileInfo(file_path).fileName()
            self.lbl_file_info.setText("Source: File Imported")
            self.lbl_filename.setText(file_name)
            self.lbl_bit_length.setText(f"{len(clean_bit_sequence)} bits")

            # 4. Switch the UI View (Your existing logic)
            self.stacked_layout.setCurrentIndex(1) # Switch to File Imported View

        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"Could not read or process file: {e}")

    def _on_revert_to_manual(self):
        """Action to switch back to manual entry mode."""
        # 1. Clear internal state and the line edit
        self._current_bit_sequence = ""
        self.entry_bitstream.clear() # Clears the data

        # 2. Emit an empty signal (or the new content of the entry box)
        self._emit_bitstream_from_entry() # Emits the new (empty) sequence

        # 3. Switch the UI View
        self.stacked_layout.setCurrentIndex(0) # Switch to Manual Entry View

    def _on_view_data_clicked(self):
        """Triggers the dialog using the internally stored sequence."""
        self._show_imported_bitstream_dialog(self._current_bit_sequence)

    def clear_bitstream_entry(self):
        self.entry_bitstream.clear()
        self.entry_bitstream.show()
        self.entry_bitstream.setEnabled(True)

    def _open_export_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Bandpass Signal", "", "WAV Files (*.wav)")

        if file_path:
            self.path_line_edit.setText(file_path)

    def _emit_export_path(self):
        path = self.path_line_edit.text()
        if path:
            self.sig_export_path.emit(path)

#------------------------------------------------------------
# +++++ Font Size Group Box Widget +++++
#------------------------------------------------------------

    def _style_groupbox_title(self, group: QGroupBox, font_size: int = 16):
        """Apply consistent title font styling to a QGroupBox."""
        font = group.font()
        font.setPointSize(font_size)
        font.setBold(True)
        font.setFamily("Segoe UI")
        group.setFont(font)


#------------------------------------------------------------
# +++++ Matrix Widget +++++
#------------------------------------------------------------
class MatrixWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Grid Layout
        layout = QGridLayout(self)

        # +++ Pulse Plot Widget +++
        # self.plot_pulse = PlotWidget(title="Pulse Shape (Time)")
        self.plot_pulse = PulseContainerWidget(title_prefix = "Pulse Shape")

        # 2. Constellation Plot (Scatter)
        self.plot_const = PlotWidget(title="Constellation (I/Q)")
        self.plot_const.plot_widget.setAspectLocked(True) # Important for Constellations
        self.plot_const.plot_widget.showGrid(x=True, y=True)


        # 3. Baseband (Placeholder for now as requested)
        self.plot_baseband = PlotWidget(title="Baseband (Time) - Pending")

        # 4. Baseband FFT (Placeholder)
        #self.plot_bb_fft = PlotWidget(title="Spectrum - Pending")
        self.bb_spectrum_container = SpectrumContainerWidget(title_prefix="Baseband Spectrum")
        # 5. Bandpass
        self.plot_bandpass  = PlotWidget(title="Bandpass (Time) - Pending")

        # 6. Bandpass FFT
        #self.plot_bp_fft = PlotWidget(title ="Bandpass Spectrum")
        self.bp_spectrum_container = SpectrumContainerWidget(title_prefix="Bandpass Spectrum")

        layout.addWidget(self.plot_pulse, 0, 0)
        layout.addWidget(self.plot_const, 0, 1)
        layout.addWidget(self.plot_baseband, 1, 0)
        #layout.addWidget(self.plot_bb_fft, 1, 1)
        layout.addWidget(self.bb_spectrum_container,1,1)
        layout.addWidget(self.plot_bandpass,2,0)
        #layout.addWidget(self.plot_bp_fft,2,1)
        layout.addWidget(self.bp_spectrum_container,2,1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(0, 26) #
        layout.setRowStretch(1, 32) #
        layout.setRowStretch(2, 32) #

#------------------------------------------------------------
# +++++ Meta Data Widget +++++
#------------------------------------------------------------
class MetaDataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.group = QGroupBox("5. Selected Baseline Parameters")
        # ---- Set Font Size ----
        font = self.group.font()
        font.setPointSize(16)
        self.group.setFont(font)

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

# #------------------------------------------------------------
# # +++++ Media Player +++++
# #------------------------------------------------------------
# class MediaPlayerWidget(QWidget):

#     # ---- Signals for main Gui Controller ----
#     sig_play_button_pressed = Signal()
#     sig_stop_button_pressed = Signal()
#     sig_export_path = Signal(str)

#     def __init__(self, parent=None):

#         super().__init__(parent)
#         layout = QVBoxLayout(self)
#         group = QGroupBox("6. Media Player")

#         # ---- Set Font Size ----
#         font = group.font()
#         font.setPointSize(16)
#         group.setFont(font)

#         layout.addWidget(group)

#         mediaply_box = QHBoxLayout(group) # MAIN H BOX 1/3 PLAY STOP 2/3 Space 3/3 Export


#         # ---- PLAY/STOP BUTTON ----
#         player_vbox = QVBoxLayout()

#         self.info_lbl = QLabel("Playback Status: Idle")
#         player_vbox.addWidget(self.info_lbl)

#         self.btn_play = QPushButton("Play")
#         player_vbox.addWidget(self.btn_play)

#         self.btn_stop = QPushButton("Stop")
#         player_vbox.addWidget(self.btn_stop)

#         player_vbox.addStretch(1)


#         # ---- EXPORT VBOX  ----
#         export_vbox = QVBoxLayout()
#         file_path_hbox = QHBoxLayout()
#         export_vbox.addWidget(QLabel("Export Bandpass Signal to .wav File"))
#         self.path_line_edit =QLineEdit()
#         self.btn_browse_path = QPushButton("Browse")

#         file_path_hbox.addWidget(self.path_line_edit)
#         file_path_hbox.addWidget(self.btn_browse_path)

#         export_vbox.addLayout(file_path_hbox)


#         self.btn_export = QPushButton("Export WAV File")
#         export_vbox.addWidget(self.btn_export)
#         # export_vbox.addWidget(self.btn_browse_path)

#         export_vbox.addStretch(1)

#         mediaply_box.addLayout(player_vbox, 1)
#         mediaply_box.addStretch(1)
#         mediaply_box.addLayout(export_vbox, 1)



#         # ---- Internal Emitters ----

#         self.btn_play.clicked.connect(self.sig_play_button_pressed.emit)
#         self.btn_stop.clicked.connect(self.sig_stop_button_pressed.emit)
#         self.btn_browse_path.clicked.connect(self._open_export_dialog)
#         self.btn_export.clicked.connect(self._emit_export_path)

#     def _open_export_dialog(self):
#         file_path, _ = QFileDialog.getSaveFileName(self, "Export Bandpass Signal", "", "WAV Files (*.wav)")

#         if file_path:
#             self.path_line_edit.setText(file_path)

#     def _emit_export_path(self):
#         path = self.path_line_edit.text()
#         if path:
#             self.sig_export_path.emit(path)



#------------------------------------------------------------
# +++++ Footer Widget +++++
#------------------------------------------------------------
class FooterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.status_bar = parent.statusBar()

        # Assuming simple footer for layout purposes
        layout = QHBoxLayout(self)
        layout.addStretch()
        self.btn_restart = QPushButton("Restart Application")
        layout.addWidget(self.btn_restart)