# ---- Start for AboutDialog.py ---- #
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

from Utilities.UI import override_ui_elements


@override_ui_elements
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About')
        self.setContentsMargins(5, 5, 5, 5)
        self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create a header QLabel with larger font size
        header_label = QLabel("SCMR Management V1")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Create a description QLabel with normal font size
        description_label = QLabel(
            "The SCMR Management V1 application is a user-friendly desktop tool designed to streamline the process of managing service orders."
            "Developed using Python and the PySide6 library, this cross-platform application offers an intuitive interface that enables users to view, search, add, and modify service orders with ease. ")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignCenter)
        copyright_label = QLabel("© 2023 Vasyl Yakovishak. All rights reserved.")
        copyright_label.setStyleSheet("font-size: 10px; font-weight: bold;")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(description_label)
        layout.addWidget(copyright_label)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

# ---- End for AboutDialog.py ---- #