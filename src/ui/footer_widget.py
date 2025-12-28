from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton
)

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
