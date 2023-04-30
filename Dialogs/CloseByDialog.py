# ---- Start for CloseByDialog.py ---- #
from PySide6.QtWidgets import QButtonGroup, QGridLayout, QDialog, QPushButton


class CloseByDialog(QDialog):
    def __init__(self, close_by_list):
        super().__init__()
        self.resize(200, 150)
        self.setContentsMargins(5, 5, 5, 5)

        self.setWindowTitle("Select Close By")
        layout = QGridLayout()
        self.button_group = QButtonGroup()
        for index, close_by in enumerate(close_by_list):
            button = QPushButton(close_by)
            self.button_group.addButton(button, index)
            layout.addWidget(button, index // 2, index % 2)
        self.setLayout(layout)
        self.button_group.buttonClicked.connect(self.accept)

# ---- End for CloseByDialog.py ---- #