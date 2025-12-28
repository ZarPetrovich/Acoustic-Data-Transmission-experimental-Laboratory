from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QDialog, QTextEdit,
    QPushButton, QLineEdit, QWidget, QStackedLayout, QFormLayout, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QTimer, QRegularExpression, QFileInfo
from PySide6.QtGui import QRegularExpressionValidator
from src.dataclasses.dataclass_models import BitstreamUpdateTask

class BitstreamWidget(QGroupBox):
    sig_changed = Signal(BitstreamUpdateTask)
    sig_clear_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("3. Bitstream", parent)

        # Debounce Timer restored from original logic
        self.bitstream_debounce_timer = QTimer(self)
        self.bitstream_debounce_timer.setSingleShot(True)
        self.bitstream_debounce_timer.setInterval(200)
        self.bitstream_debounce_timer.timeout.connect(self._emit_bitstream_from_entry)

        self.main_vbox = QVBoxLayout(self)
        self.stacked_layout = QStackedLayout()

        self._create_manual_entry_widget()
        self._create_imported_file_widget()

        self.main_vbox.addLayout(self.stacked_layout)

        self.btn_clear_plots = QPushButton("Clear All Signals & Data")
        self.main_vbox.addWidget(self.btn_clear_plots)
        self.btn_clear_plots.clicked.connect(self.sig_clear_requested.emit)

        self.stacked_layout.setCurrentIndex(0)
        self._current_bit_sequence = "" # Internal state for viewing

    def _create_manual_entry_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.lbl_manual_source = QLabel("Source: Manual Entry (Active)")
        self.lbl_manual_source.setStyleSheet("font-weight: bold; color: green;")
        layout.addWidget(self.lbl_manual_source)

        layout.addWidget(QLabel("Add Bitstream manually ( 1 | 0 ): "))
        self.entry_bitstream = QLineEdit()
        regex = QRegularExpression("^[01]+$")
        self.entry_bitstream.setValidator(QRegularExpressionValidator(regex, self))
        layout.addWidget(self.entry_bitstream)

        import_h = QHBoxLayout()
        import_h.addWidget(QLabel("Or Import File"))
        self.btn_import_data = QPushButton("Import Bitstream (.bin)")
        import_h.addWidget(self.btn_import_data)
        layout.addLayout(import_h)

        self.stacked_layout.addWidget(widget)

        self.entry_bitstream.textChanged.connect(self._on_text_changed)
        self.btn_import_data.clicked.connect(self._open_import_dialog)

    def _create_imported_file_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.lbl_file_info = QLabel("Source: File")
        self.lbl_file_info.setStyleSheet("font-weight: bold; color: darkorange;")
        layout.addWidget(self.lbl_file_info)

        form_layout = QFormLayout()
        self.lbl_filename = QLabel("N/A")
        self.lbl_bit_length = QLabel("N/A")
        form_layout.addRow("Filename:", self.lbl_filename)
        form_layout.addRow("Length:", self.lbl_bit_length)
        layout.addLayout(form_layout)

        h_buttons = QHBoxLayout()
        self.btn_view_data = QPushButton("View Full Data") # Restored
        self.btn_revert_manual = QPushButton("Revert to Manual Entry")
        h_buttons.addWidget(self.btn_view_data)
        h_buttons.addWidget(self.btn_revert_manual)
        layout.addLayout(h_buttons)

        self.stacked_layout.addWidget(widget)

        # Connections for file view
        self.btn_view_data.clicked.connect(self._on_view_data_clicked)
        self.btn_revert_manual.clicked.connect(self._on_revert_to_manual)

    def _on_view_data_clicked(self):
        """Displays the internal bit sequence in a dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Imported Bitstream")
        vbox = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(self._current_bit_sequence)
        vbox.addWidget(text)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        vbox.addWidget(btn_close)
        dialog.resize(400, 300)
        dialog.exec()

    def _on_text_changed(self):
        self._current_bit_sequence = self.entry_bitstream.text() # Sync state
        self.bitstream_debounce_timer.stop()
        self.bitstream_debounce_timer.start()

    def _emit_bitstream_from_entry(self):
        self.sig_changed.emit(BitstreamUpdateTask(bit_stream=self._current_bit_sequence))

    def _open_import_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Baseline Data", "", "Binary Files (*.bin)")
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                raw_data = f.read()

            clean_bits = "".join(raw_data.split())
            self._current_bit_sequence = clean_bits # Store for the viewer

            self.lbl_filename.setText(QFileInfo(file_path).fileName())
            self.lbl_bit_length.setText(f"{len(clean_bits)} bits")
            self.stacked_layout.setCurrentIndex(1)

            self.sig_changed.emit(BitstreamUpdateTask(bit_stream=clean_bits))
        except Exception as e:
            print(f"Import Error: {e}")

    def _on_revert_to_manual(self):
        self._current_bit_sequence = ""
        self.entry_bitstream.clear()
        self.stacked_layout.setCurrentIndex(0)
        self._emit_bitstream_from_entry()