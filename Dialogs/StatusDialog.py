# ---- Start for StatusDialog.py ---- #
from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton

class StatusDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(100, 70)
        self.setWindowTitle("Status")
        self.setContentsMargins(5, 5, 5, 5)

        layout = QHBoxLayout()

        self.green_button = QPushButton("GREEN")
        self.yellow_button = QPushButton("YELLOW")

        layout.addWidget(self.green_button)
        layout.addWidget(self.yellow_button)

        self.setLayout(layout)

        self.status = None

        self.green_button.clicked.connect(self.set_status_green)
        self.yellow_button.clicked.connect(self.set_status_yellow)

    def set_status_green(self):
        self.status = "GREEN"
        self.accept()

    def set_status_yellow(self):
        self.status = "YELLOW"
        self.accept()
# ---- End for StatusDialog.py ---- #