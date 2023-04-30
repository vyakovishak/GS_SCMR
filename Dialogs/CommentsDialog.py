# ---- Start for CommentsDialog.py ---- #
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QPushButton, QMessageBox

class CommentsDialog(QDialog):
    def __init__(self, status):
        super().__init__()
        self.resize(400, 200)
        self.setContentsMargins(5, 5, 5, 5)
        self.status = status
        self.setWindowTitle("Enter Comments")
        layout = QVBoxLayout()
        self.label = QLabel("Comments (minimum 10 characters):")

        # Add Payment Required checkbox
        self.payment_required_checkbox = QCheckBox("Payment Required")
        self.comments_input = QLineEdit()
        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.label)
        layout.addWidget(self.comments_input)
        layout.addWidget(self.payment_required_checkbox)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)
        self.submit_button.clicked.connect(self.validate_comments)

    def validate_comments(self):

        # Check if the status is Green and the Payment Required checkbox is checked
        if self.status == "GREEN" and self.payment_required_checkbox.isChecked():
            condition = len(self.comments_input.text()) >= 10

        elif self.status == "YELLOW":
            condition = self.status == "YELLOW" and len(self.comments_input.text()) >= 10
        else:
            condition = True

        if condition:
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Comments must be at provided! (at least 10 characters long)")


# ---- End for CommentsDialog.py ---- #