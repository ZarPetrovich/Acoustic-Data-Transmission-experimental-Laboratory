from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit
)
from PySide6.QtCore import Signal

class MediaPlayerWidget(QGroupBox):
    # Signals for the Mediator (main_model.py)
    sig_play = Signal()
    sig_stop = Signal()
    sig_export_wav = Signal(str)

    def __init__(self, parent=None):
        super().__init__("6. Media Player", parent)

        # Consistent styling from original widgets.py
        font = self.font()
        font.setPointSize(16)
        font.setBold(True)
        self.setFont(font)

        layout = QVBoxLayout(self)

        # Main horizontal box split into Playback and Export sections
        mediaply_box = QHBoxLayout()

        # ---- 1/3: Playback Section ----
        player_vbox = QVBoxLayout()
        self.info_lbl = QLabel("Playback Status: Idle")
        player_vbox.addWidget(self.info_lbl)

        self.btn_play = QPushButton("Play")
        player_vbox.addWidget(self.btn_play)

        self.btn_stop = QPushButton("Stop")
        player_vbox.addWidget(self.btn_stop)
        player_vbox.addStretch(1)

        # ---- 2/3: Spacer ----
        mediaply_box.addLayout(player_vbox, 1)
        mediaply_box.addStretch(1)

        # ---- 3/3: Export Section ----
        export_vbox = QVBoxLayout()
        export_vbox.addWidget(QLabel("Export Bandpass Signal to .wav File"))

        file_path_hbox = QHBoxLayout()
        self.line_edit_wav_path = QLineEdit()
        self.line_edit_wav_path.setPlaceholderText("No path selected...")
        self.btn_browse_path = QPushButton("Browse")

        file_path_hbox.addWidget(self.line_edit_wav_path)
        file_path_hbox.addWidget(self.btn_browse_path)
        export_vbox.addLayout(file_path_hbox)

        self.btn_export = QPushButton("Export WAV File")
        export_vbox.addWidget(self.btn_export)
        export_vbox.addStretch(1)

        mediaply_box.addLayout(export_vbox, 1)
        layout.addLayout(mediaply_box)

        # --- Internal Connections ---
        self.btn_play.clicked.connect(self.sig_play.emit)
        self.btn_stop.clicked.connect(self.sig_stop.emit)
        self.btn_browse_path.clicked.connect(self._open_export_wav_dialog)
        self.btn_export.clicked.connect(self._on_export_clicked)

    def _open_export_wav_dialog(self):
        """Internal UI logic to pick a save location."""
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Bandpass Signal", "", "WAV Files (*.wav)"
        )
        if file_path:
            self.line_edit_wav_path.setText(file_path)

    def _on_export_clicked(self):
        """Validates the path before sending it to the Mediator."""
        path = self.line_edit_wav_path.text().strip()
        if path:
            self.sig_export_wav.emit(path)

    def update_status(self, text: str):
        """Allows the Controller to update the status label (e.g., 'Playing...')."""
        self.info_lbl.setText(f"Playback Status: {text}")