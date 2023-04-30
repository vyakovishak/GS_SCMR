# ---- Start for WelcomeScreen.py ---- #
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QDialog

from Dialogs.TutorialDialog import TutorialDialog
from Utilities.UI import override_ui_elements


@override_ui_elements
class WelcomeScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Welcome')

        self.setContentsMargins(5, 5, 5, 5)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        welcome_label = QLabel("Welcome to SCMR Management Beta V1\n")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(welcome_label)
        text = QLabel("This program will help you keep track of service orders.\n\n"
                      "PS. From V 599 with Love !")
        text.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(text)

        tutorial_button = QPushButton("Tutorial")
        tutorial_button.clicked.connect(self.show_tutorial)
        layout.addWidget(tutorial_button)

        skip_button = QPushButton("Skip")
        skip_button.clicked.connect(self.close)
        layout.addWidget(skip_button)

        self.setLayout(layout)

    def show_tutorial(self):
        tutorial_dialog = TutorialDialog(self)
        tutorial_dialog.exec_()
# ---- End for WelcomeScreen.py ---- #