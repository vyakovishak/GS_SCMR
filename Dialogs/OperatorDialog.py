# ---- Start for OperatorDialog.py ---- #
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QGridLayout, QButtonGroup, QPushButton, QMessageBox

from Utilities.utils import load_agents


class OperatorDialog(QDialog):
    def __init__(self, location=None, payment=None):
        super().__init__()
        self.agents = load_agents(agent_names_only=True)

        self.setContentsMargins(5, 5, 5, 5)

        self.setWindowTitle("Select Agent")
        layout = QVBoxLayout()

        # Add location label when location is not None
        if location is not None:
            location_label = QLabel(f"Current Location: {location}")
            location_label.text
            layout.addWidget(location_label)

        grid_layout = QGridLayout()
        self.button_group = QButtonGroup()
        self.buttons = []
        for index, operator in enumerate(self.agents):
            button = QPushButton(operator)
            self.buttons.append(button)

            self.button_group.addButton(button, index)
            grid_layout.addWidget(button, index // 2, index % 2)

        layout.addLayout(grid_layout)
        self.setLayout(layout)
        self.button_group.buttonClicked.connect(self.on_button_clicked)
        self.selected_operator = None

    def on_button_clicked(self, button):
        button_id = self.button_group.id(button)
        self.selected_operator = self.agents[button_id]

        confirmation_message = QMessageBox(self)
        confirmation_message.setIcon(QMessageBox.Question)
        confirmation_message.setWindowTitle("Confirm Agent")
        confirmation_message.setText(f"Is '{self.selected_operator}' the correct Agent?")
        yes_button = confirmation_message.addButton(QMessageBox.Yes)
        no_button = confirmation_message.addButton(QMessageBox.No)
        confirmation_message.exec_()

        if confirmation_message.clickedButton() == yes_button:
            self.accept()
        else:
            self.selected_operator = None

    def get_operator(self):
        return self.selected_operator


# ---- End for OperatorDialog.py ---- #