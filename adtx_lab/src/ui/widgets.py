from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QPushButton
)

from PySide6.QtCore import Qt, QTimer



class MatrixWidget(QWidget):
    """
    Placeholder for plots in the comparison matrix, now supporting two stacked sub-plots:
    1. Live Signal (Top) - Dynamically updated by controls.
    2. Saved Signal (Bottom) - Statically set (for future use).
    """
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setMinimumSize(250, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Main layout for the slot
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

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


class FooterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        footer_widget = QWidget(self)
        footer_widget.setObjectName("AppFooter")

        h_layout = QHBoxLayout(footer_widget)
        h_layout.setContentsMargins(10, 5, 10, 5)
        h_layout.setSpacing(10)

        h_layout.addStretch(1)

        restart_button = QPushButton("Restart Application", self)
        restart_button.setObjectName("RestartButton")
        restart_button.clicked.connect(self.restart_application)
        h_layout.addWidget(restart_button)

        close_button = QPushButton("Exit Application", self)
        close_button.setObjectName("ExitButton")
        close_button.clicked.connect(self.close)
        h_layout.addWidget(close_button)

    def restart_application(self):
        """Placeholder for restart functionality."""
        print("Restarting application...")

    def close(self):
        """Placeholder for close functionality."""
        print("Closing application...")