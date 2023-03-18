import datetime
import json

from PySide6.QtWidgets import QWidget, QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QStatusBar

from DialogsWindow import LocationDialog, CloseByDialog, StatusDialog, CommentsDialog
from ServiceOrderDB import ServiceOrderDB  # Assuming your ServiceOrderDB class is in a file named service_order_db.py

from TableWidget import SCMRTable
from WindowsLayout import LayoutSettings


class MainWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1080, 720)
        self.settings = self.load_settings()
        # Create a status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a QVBoxLayout
        main_layout = QVBoxLayout(central_widget)

        # Create a QHBoxLayout for input box and delete button
        input_delete_layout = QHBoxLayout()

        # Initialize the ServiceOrderDB
        self.db = ServiceOrderDB(status_bar=self.status_bar)
        self.db.create_table_users()

        # Create the SCMRTable
        self.table_widget = SCMRTable(self.db, )
        main_layout.addWidget(self.table_widget)

        input_delete_layout = QHBoxLayout()

        # Create a QVBoxLayout for input box
        input_layout = QVBoxLayout()
        self.input_box = QLineEdit()
        input_layout.addWidget(self.input_box)
        self.input_box.returnPressed.connect(self.handle_scanner_input)
        input_delete_layout.addLayout(input_layout)

        # Create a QVBoxLayout for delete button
        delete_layout = QVBoxLayout()
        self.delete_button = QPushButton("Delete")
        delete_layout.addWidget(self.delete_button)
        self.delete_button.clicked.connect(self.delete_selected_entry)
        input_delete_layout.addLayout(delete_layout)

        # Add the QHBoxLayout to the QVBoxLayout
        main_layout.addLayout(input_delete_layout)

    @staticmethod
    def load_settings():
        with open("Settings.json", "r") as settings_file:
            return json.load(settings_file)

    def delete_selected_entry(self):
        selected_row = self.table_widget.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select an entry to delete.")
            return

        service_order = self.table_widget.item(selected_row, 0).text()
        service_order_db = ServiceOrderDB()
        service_order_db.delete_user(service_order,
                                     operator="Some Operator")  # Replace "Some Operator" with the actual operator
        self.table_widget.removeRow(selected_row)
        self.status_bar.showMessage("No entry selected for deletion")
        self.status_bar.showMessage(f"Deleted entry: {service_order}")

    def handle_scanner_input(self):
        # Get the scanned input from the input box
        scanned_input = self.input_box.text()

        # Process the scanned input
        print(f"Scanned input: {scanned_input}")

        # Location Dialog
        location_dialog = LocationDialog()
        if location_dialog.exec_():
            location = location_dialog.location_input.text().upper()

            # Close By Dialog
            close_by_list = self.settings["Operators"]["ARA"]
            close_by_dialog = CloseByDialog(close_by_list)
            if close_by_dialog.exec_():
                close_by = close_by_list[close_by_dialog.button_group.checkedId()]

                # Status Dialog
                status_dialog = StatusDialog()
                if status_dialog.exec_():
                    status = status_dialog.status

                    comments_dialog = CommentsDialog(status)
                    if comments_dialog.exec_():
                        comments = comments_dialog.comments_input.text()
                        print(comments)
                    else:
                        return

                    # Add the data to the database
                    self.db.add_user(
                        ServiceOrder=int(scanned_input),
                        Location=location,
                        CompletionDate=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ClosedBy=close_by,
                        Status=status,
                        Comments=comments,
                    )

                    # Update the table
                    self.table_widget.update_data()

        # Clear the input box
        self.input_box.clear()
        self.status_bar.showMessage(f"Added entry: {scanned_input}")
