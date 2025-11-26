from PySide6.QtCore import Qt, Signal,QRegularExpression, QPoint
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QSpinBox,
    QFormLayout,
    QListWidget,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QMenu

)
import numpy as np

from adtx_lab.src.ui.plot_widgets import PlotWidget

class Header(QWidget):

    def __init__(self, fs, sym_rate, parent=None):

        super().__init__(parent)

        layout = QGridLayout(self)

        self.label_fs = QLabel(f"FS : {fs} Hz ")
        layout.addWidget(self.label_fs)

        self.label_sym_rate = QLabel(f"Symbolrate : {sym_rate} Symbol/s")
        layout.addWidget(self.label_sym_rate)

        self.label_samples_per_symbol = QLabel(
            f"Samples/Symbol: {int(fs/sym_rate)} samples "
        )
        layout.addWidget(self.label_samples_per_symbol)


class PulseTab(QWidget):

    signal_create_Pulse = Signal()

    signal_tab_pulse_selected = Signal(str)

    def __init__(self, pulse_shape_map, parent=None):

        super().__init__(parent)

        self.reverse_map_pulse_shape = {v: k for k, v in pulse_shape_map.items()}

        # Outer layout 4 Columns
        outer_layout = QHBoxLayout(self)
        # Left Side 2 Rows in the first column
        left_vert_layout = QVBoxLayout()
        # First Column First Row is a FormLayout
        vertical_form_layout = QFormLayout()

        # add layouts to each other
        outer_layout.addLayout(left_vert_layout)
        left_vert_layout.addLayout(vertical_form_layout)

        # Pulse Shape
        self.combobox_pulse_shapes = QComboBox()
        self.combobox_pulse_shapes.addItems(pulse_shape_map.values())
        vertical_form_layout.addRow("Pulse Shape:", self.combobox_pulse_shapes)

        # Pulse Span
        self.spinbox_pulse_span = QSpinBox(self)
        self.spinbox_pulse_span.setRange(1, 5)
        self.spinbox_pulse_span.setSingleStep(1)
        self.spinbox_pulse_span.setValue(1)

        vertical_form_layout.addRow("Pulse Span:", self.spinbox_pulse_span)

        # region Buttons
        btn_create_pulse = QPushButton("Create Pulse")
        vertical_form_layout.addRow(btn_create_pulse)
        # endregion

        # region List of Pulses
        self.list_created_pulses = QListWidget()

        left_vert_layout.addWidget(self.list_created_pulses)

        # endregion

        # Plot

        self.plot_pulses_widget = PlotWidget("Pulse Preview")
        outer_layout.addWidget(self.plot_pulses_widget, stretch=3)

        # Btn Signal

        self.list_created_pulses.itemClicked.connect(self.on_item_clicked)

        btn_create_pulse.clicked.connect(self.signal_create_Pulse.emit)

    def get_values(self):

        sel_shape_text = self.combobox_pulse_shapes.currentText()

        return {
            "shape": self.reverse_map_pulse_shape.get(sel_shape_text),
            "span": self.spinbox_pulse_span.value(),
        }

    def update_list(self, pulse_signal_items):
        self.list_created_pulses.clear()
        self.list_created_pulses.addItems(pulse_signal_items)

    def on_item_clicked(self, item):
        self.signal_tab_pulse_selected.emit(item.text())


class BitMappingTab(QWidget):

    signal_create_sym_sequence = Signal(int)

    def __init__(self,parent= None):
        super().__init__(parent)

        outer_layout = QHBoxLayout(self)
        left_vert_layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Content Form Layout Left/Top Inside QVbox inside QHbox

        left_vert_layout.addLayout(form_layout)
        outer_layout.addLayout(left_vert_layout)

        self.entry_bitsequence = QLineEdit()
        form_layout.addRow("Enter Bit Sequence:", self.entry_bitsequence)

        regex = QRegularExpression("^[01]+$")
        bit_validator = QRegularExpressionValidator(regex, self)
        self.entry_bitsequence.setValidator(bit_validator)

        self.btn_create_bitseq = QPushButton("2-ASK")
        form_layout.addRow(self.btn_create_bitseq)

        self.btn_create_bitseq.clicked.connect(
            lambda: self.signal_create_sym_sequence.emit(1))
        # Qlist left/bottom inside QVBox inside QHbox

        self.list_bitseq = QListWidget()
        left_vert_layout.addWidget(self.list_bitseq)

        self.label_sel_symseq = QLabel("Nothing Selected")
        self.label_sel_symseq.setWordWrap(True)
        left_vert_layout.addWidget(self.label_sel_symseq)

        outer_layout.addStretch(1)

        self.list_bitseq.currentItemChanged.connect(
            self.update_label_selected_symseq
        )


    def get_bitseq(self):
        bitseq_text = self.entry_bitsequence.text()

        if not bitseq_text:
            # Return None to signal a critical error to the main logic
            return None

        # Convert the string of bits (e.g., "10110") to a list of integers [1, 0, 1, 1, 0]
        bitseq_array = np.fromiter(bitseq_text, dtype=int)

        return bitseq_array

    def update_list(self, dict_symbol_sequences):
        self.list_bitseq.clear()
        self.list_bitseq.addItems(dict_symbol_sequences.keys())

    def update_label_selected_symseq(self):
        sel_sequence = self.list_bitseq.currentItem()

        if sel_sequence:
            self.label_sel_symseq.setText(f"Selected Symbol Sequence:\n{sel_sequence.data.name}")


class BasebandTab(QWidget):

    signal_create_basebandsignal = Signal()

    signal_tab_baseband_selected = Signal(str)

    signal_context_menu_baseband = Signal(QPoint)

    def __init__(self, parent=None):

        super().__init__(parent)

        # Outer layout 4 Columns
        outer_layout = QHBoxLayout(self)
        # Left Side 2 Rows in the first column
        left_vert_layout = QVBoxLayout()
        # First Column First Row is a FormLayout
        vertical_form_layout = QFormLayout()

        outer_layout.addLayout(left_vert_layout)
        left_vert_layout.addLayout(vertical_form_layout)

        # Forms inside left/top QVBox inside outer QHBox
        self.combobox_pulse_signals = QComboBox()
        vertical_form_layout.addRow("Select a Pulse:", self.combobox_pulse_signals)

        self.combobox_symseq = QComboBox()
        vertical_form_layout.addRow("Select Symbol Sequence", self.combobox_symseq)

        btn_create_baseband_signal = QPushButton("Create Baseband Signal")
        vertical_form_layout.addRow(btn_create_baseband_signal)

        btn_create_baseband_signal.clicked.connect(
            self.signal_create_basebandsignal.emit
        )

        # List inside left/bottom QVbox inside outer QHbox

        self.list_baseband_signals = QListWidget()
        self.list_baseband_signals.setSelectionMode(QListWidget.SingleSelection)
        self.list_baseband_signals.itemClicked.connect(
            parent.on_baseband_selected
        )
        left_vert_layout.addWidget(self.list_baseband_signals)

        self.list_baseband_signals.itemClicked.connect(self.on_item_clicked)

        self.list_baseband_signals.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_baseband_signals.customContextMenuRequested.connect(
            self.emit_context_menu_signal
        )

        # Plot bb=baseband

        self.plot_bb_widget = PlotWidget("Baseband Signal Preview")
        outer_layout.addWidget(self.plot_bb_widget, stretch=3)

    def update_combox_pulse_signals(self, dict_pulse_signal_obj):
        self.combobox_pulse_signals.clear()
        for pulse_signal in dict_pulse_signal_obj.values():
            self.combobox_pulse_signals.addItem(pulse_signal.name, pulse_signal)

    def update_combox_symseq(self, dict_symseq_obj):

        self.combobox_symseq.clear()
        for symseq in dict_symseq_obj.values():
            self.combobox_symseq.addItem(symseq.name, symseq)

    def update_list_pulse(self, baseband_signal_items):
        self.list_baseband_signals.clear()
        self.list_baseband_signals.addItems(baseband_signal_items)


    def on_item_clicked(self, item):
        self.signal_tab_baseband_selected.emit(item.text())

    def emit_context_menu_signal(self, pos: QPoint):
        """Maps local position to global and emits the signal for MainGUILogic."""
        if self.list_baseband_signals.itemAt(pos):
            global_pos = self.list_baseband_signals.mapToGlobal(pos)
            self.signal_context_menu_baseband.emit(global_pos)

class ModulationTab(QWidget):

    signal_create_Modulation = Signal()

    def __init__(self, parent=None):

        super().__init__(parent)

        # +++ Main layout GRID +++
        outer_layout = QGridLayout(self)

        # Vertical Layout for Comboboxes
        form_layout = QVBoxLayout()

        # Baseband ComboBox
        label_baseband = QLabel("Select Baseband Signal:")
        form_layout.addWidget(label_baseband)
        self.combobox_baseband_signals = QComboBox()
        form_layout.addWidget(self.combobox_baseband_signals)

        # Modulate Button
        btn_create_modulation = QPushButton("Modulate")
        form_layout.addWidget(btn_create_modulation)

        # This pushes the info label to the bottom of the control column
        form_layout.addStretch()

        # Info Label for Selected Baseband
        self.label_sel_name_baseband = QLabel("No Baseband Signal Selected")
        self.label_sel_name_baseband.setWordWrap(True)
        form_layout.addWidget(self.label_sel_name_baseband)

        # 3. --- Create a placeholder for the PLOT ---
        # This will be your plot widget later
        self.plot_placeholder = QLabel("Future Plot Area")
        self.plot_placeholder.setStyleSheet(
            """
            background-color: #f0f0f0;
            border: 2px dashed #aaa;
            qproperty-alignment: 'AlignCenter';
            font-size: 16px;
            color: #888;
        """
        )
        self.plot_placeholder.setMinimumSize(400, 300) #


        # Add the controls layout to column 0.
        # It starts at row 0, col 0, and spans ALL rows (-1), and 1 column.

        outer_layout.addLayout(form_layout, 0, 0, -1, 1)

        # Add the plot placeholder to column 1.
        # It starts at row 0, col 1, spans ALL rows (-1), and 2 columns.

        outer_layout.addWidget(self.plot_placeholder, 0, 1, -1, 2)

        # --- Set Column Stretching ---

        # Make the control column (index 0) a fixed size
        outer_layout.setColumnStretch(0, 0)

        # Make the plot area (index 1) take up all the extra space
        outer_layout.setColumnStretch(1, 1)

        # +++ SIGNALS +++

        btn_create_modulation.clicked.connect(self.signal_create_Modulation.emit)

        self.combobox_baseband_signals.currentIndexChanged.connect(
            self.update_label_baseband_info
        )

    def get_values(self):
        sel_mod_scheme_text = self.combobox_mod_schemes.currentText()

        return {
            "mod_scheme": self.reverse_map_mod_schemes.get(sel_mod_scheme_text),
        }

    def update_baseband_signals(self, baseband_signal_obj):
        self.combobox_baseband_signals.clear()
        for name, signal_object in baseband_signal_obj.items():
            self.combobox_baseband_signals.addItem(name, signal_object)

    def update_label_baseband_info(self):

        sel_signal = self.combobox_baseband_signals.currentData()

        if sel_signal:

            info_text = (
                f"<b>Selected Baseband Signal:<b> <br>"
                f"{sel_signal.name}<br>"
                f"Pulse Used: {sel_signal.pulse_name}<br>"
                f"Bit Sequence: {sel_signal.bit_seq_name}<br>"
                f"Sampling Freq (fs): {sel_signal.fs} Hz<br>"
                f"Symbol Rate: {sel_signal.sym_rate} Symbol/s"
            )

            self.label_sel_name_baseband.setText(info_text)

        else:
            self.label_sel_name_baseband.setText("INFO: No Baseband Selected")


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
