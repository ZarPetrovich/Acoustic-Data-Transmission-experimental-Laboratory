from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import(
    QDialog,
    QWidget,
    QVBoxLayout,
    QLabel,
    QDialogButtonBox,
    QSpinBox,
    QFormLayout, # Used for the input fields
    QComboBox)


class IntroDialog(QDialog):


    def __init__(self, parent=None):
        super().__init__(parent)

        GLOBAL_LIST_OF_FS =["44100" , "48000"]

        self.setWindowTitle("Welcome to ADTx Lab")
        self.setGeometry(100, 100, 900, 600)
        self.setModal(True)

        # 1. Use a QVBoxLayout as the main layout for stacking content
        main_layout = QVBoxLayout(self)

        # --- Header and Intro Text ---
        header_label = QLabel("ADTx Laboratory 🧪")
        header_label.setStyleSheet("font-size: 30pt; font-weight: bold; padding: 10px 0;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)

        # Intro Text
        intro_text = (
            "This application is designed to help you explore and visualize the "
            "fundamentals of **digital baseband signal transmission** and **pulse shaping**. "
            "Start by defining the core system timing below."
        )
        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True)
        intro_label.setTextFormat(Qt.TextFormat.RichText)
        main_layout.addWidget(intro_label)

        # --- 2. Input Form (QFormLayout nested inside a container) ---

        # Container widget for the form inputs
        form_container = QWidget()
        form_layout = QFormLayout(form_container) # This is the QFormLayout instance
        form_layout.setContentsMargins(0, 15, 0, 15)

        # FS ComboBox
        self.combobox_fs = QComboBox()
        self.combobox_fs.addItems(GLOBAL_LIST_OF_FS)
        # Use QFormLayout.addRow(label, widget)
        form_layout.addRow("FS (Hz):", self.combobox_fs)

        # Symbols per Second SpinBox
        self.spinbox_sym_rate = QSpinBox()
        self.spinbox_sym_rate.setRange(1, 600)
        self.spinbox_sym_rate.setSingleStep(1)
        self.spinbox_sym_rate.setValue(100) # Set a sensible default
        form_layout.addRow("Symbols/s (Rs):", self.spinbox_sym_rate)

        # Add the form container to the main vertical stack
        main_layout.addWidget(form_container)

        # --- 3. Button Box ---

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box) # Add the button box to the main vertical stack


    def get_values(self):
        """Returns the selected sampling frequency and symbol rate."""
        fs = int(self.combobox_fs.currentText())
        sym_rate = int(self.spinbox_sym_rate.value())

        return {
            "fs": fs,
            "sym_rate": sym_rate
        }