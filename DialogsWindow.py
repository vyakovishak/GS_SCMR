from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QButtonGroup, \
    QMessageBox, QHBoxLayout, QTableWidget


class LocationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Location")
        layout = QVBoxLayout()

        # Create a QHBoxLayout for the label and input box
        hbox = QHBoxLayout()

        self.label = QLabel("Location:")
        self.location_input = QLineEdit()

        # Add the label and input box to the QHBoxLayout
        hbox.addWidget(self.label)
        hbox.addWidget(self.location_input)

        # Add the QHBoxLayout to the main QVBoxLayout
        layout.addLayout(hbox)
        self.location_input.returnPressed.connect(self.accept)
        self.setLayout(layout)


class CloseByDialog(QDialog):
    def __init__(self, close_by_list):
        super().__init__()
        self.resize(200, 150)
        self.setWindowTitle("Select Close By")
        layout = QGridLayout()
        self.button_group = QButtonGroup()
        for index, close_by in enumerate(close_by_list):
            button = QPushButton(close_by)
            self.button_group.addButton(button, index)
            layout.addWidget(button, index // 2, index % 2)
        self.setLayout(layout)
        self.button_group.buttonClicked.connect(self.accept)


class OperatorDialog(QDialog):
    def __init__(self, close_by_list):
        super().__init__()
        self.resize(200, 150)
        self.setWindowTitle("Select Close By")
        layout = QGridLayout()
        self.button_group = QButtonGroup()
        for index, close_by in enumerate(close_by_list):
            button = QPushButton(close_by)
            self.button_group.addButton(button, index)
            layout.addWidget(button, index // 2, index % 2)
        self.setLayout(layout)
        self.button_group.buttonClicked.connect(self.accept)


class CalenderTable(QTableWidget):
    def __int__(self, table_data=None):
        super().__int__()
        self.resize(1080, 720)
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels(
            ["Service Order", "Location", "Completion Date", "Closed By", "Status", "Comments", "Last Updated",
             "Updated By", ""])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        if table_data is not None:
            for row_number, row_data in enumerate(table_data):
                self.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        else:
            print("The database is empty.")


class StatusDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(100, 70)
        self.setWindowTitle("Status")
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


class CommentsDialog(QDialog):
    def __init__(self, status):
        super().__init__()
        self.resize(400, 200)
        self.setWindowTitle("Enter Comments")
        layout = QVBoxLayout()
        self.label = QLabel("Comments (minimum 10 characters):")
        self.comments_input = QLineEdit()
        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.label)
        layout.addWidget(self.comments_input)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)
        if status == "YELLOW":
            self.submit_button.clicked.connect(self.validate_comments)
        else:
            self.submit_button.clicked.connect(self.accept)

    def validate_comments(self):
        if len(self.comments_input.text()) >= 10:
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Comments must be at least 10 characters long.")
