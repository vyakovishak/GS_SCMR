import datetime
import json

from PySide6.QtWidgets import QWidget, QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QStatusBar, QDialog, QLabel, QListWidget, QCalendarWidget, QGroupBox, QGridLayout, QCheckBox, \
    QComboBox

from PySide6.QtGui import QIcon

from DialogsWindow import LocationDialog, OperatorDialog, StatusDialog, CommentsDialog, CalenderTable

from ServiceOrderDB import ServiceOrderDB

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

        # Initialize the ServiceOrderDB
        self.db = ServiceOrderDB(status_bar=self.status_bar)
        self.db.create_table_users()

        #Create Icon button
        calendar_icon = QIcon("calendar_icon.png")
        calendar_button = QPushButton(calendar_icon, "")
        calendar_button.clicked.connect(self.show_filter_dialog)

        # Create the SCMRTable
        self.table_widget = SCMRTable(self.db, )
        main_layout.addWidget(self.table_widget)

        input_delete_layout = QHBoxLayout()

        # Create a QVBoxLayout for input box
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_label = QLabel("SO#")
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_box)
        self.input_box.returnPressed.connect(self.handle_scanner_input)
        input_delete_layout.addLayout(input_layout)

        # Create a QVBoxLayout for delete button
        delete_layout = QVBoxLayout()
        self.delete_button = QPushButton("Delete")
        delete_layout.addWidget(calendar_button)
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
        service_order_db.delete_service_order(service_order, operator="Some Operator")
        self.table_widget.removeRow(selected_row)
        self.status_bar.showMessage("No entry selected for deletion")
        self.status_bar.showMessage(f"Deleted entry: {service_order}")

    def handle_scanner_input(self):
        # Get the scanned input from the input box
        scanned_input = self.input_box.text()

        existing_service_order = self.db.select_unit(ServiceOrder=scanned_input)
        print(existing_service_order)
        if existing_service_order:
            # Show the "Checking Out" dialog
            check_out_list = self.settings["Operators"]["CA"]
            check_out_dialog = OperatorDialog(check_out_list)
            if check_out_dialog.exec_():
                check_out_by = check_out_list[check_out_dialog.button_group.checkedId()]

                # Update the CheckOut value, CheckOutDate, and CheckOutBy in the database
                self.db.update_checked_out(True, scanned_input, check_out_by)
                self.db.update_check_out_date(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), scanned_input,
                                              check_out_by)
                self.db.update_check_out_by(check_out_by, scanned_input, check_out_by)

                # Update the table
                self.table_widget.load_data()

                # Clear the input box
                self.input_box.clear()
                self.status_bar.showMessage(f"Checked out entry: {scanned_input}")
                return

        # Location Dialog
        location_dialog = LocationDialog()
        if location_dialog.exec_():
            location = location_dialog.location_input.text().upper()

            # Close By Dialog
            close_by_list = self.settings["Operators"]["ARA"]
            close_by_dialog = OperatorDialog(close_by_list)
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
                    self.db.add_service_order(
                        ServiceOrder=int(scanned_input),
                        Location=location,
                        CompletionDate=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ClosedBy=close_by,
                        Status=status,
                        Comments=comments
                    )

                    # Update the table
                    self.table_widget.load_data()

        # Clear the input box
        self.input_box.clear()
        self.status_bar.showMessage(f"Added entry: {scanned_input}")

    def show_filter_dialog(self):
        filter_dialog = QDialog(self)
        filter_dialog.setWindowTitle("Filter Service Orders")
        filter_dialog.resize(400, 300)

        layout = QVBoxLayout()

        # Create the calendar widget
        calendar = QCalendarWidget()
        layout.addWidget(calendar)

        # Create the filter options
        filter_options = QGroupBox("Filter Options")
        filter_layout = QGridLayout()

        completion_date_checkbox = QCheckBox("Completion Date")
        last_updated_checkbox = QCheckBox("Last Updated")
        check_out_date_checkbox = QCheckBox("Check Out Date")

        filter_layout.addWidget(completion_date_checkbox, 0, 0)
        filter_layout.addWidget(last_updated_checkbox, 1, 0)
        filter_layout.addWidget(check_out_date_checkbox, 2, 0)

        checkout_checkbox = QCheckBox("Checkout")
        closed_by_combobox = QComboBox()
        closed_by_combobox.addItem()
        checked_out_by_combobox = QComboBox()
        checked_out_by_combobox.addItem("CA Operator 1")
        checked_out_by_combobox.addItem("CA Operator 2")

        status_combobox = QComboBox()
        status_combobox.addItem("Yellow")
        status_combobox.addItem("Green")

        filter_layout.addWidget(checkout_checkbox, 0, 1)
        filter_layout.addWidget(QLabel("Closed By:"), 1, 1)
        filter_layout.addWidget(closed_by_combobox, 1, 2)
        filter_layout.addWidget(QLabel("Checked Out By:"), 2, 1)
        filter_layout.addWidget(checked_out_by_combobox, 2, 2)
        filter_layout.addWidget(QLabel("Status:"), 3, 1)
        filter_layout.addWidget(status_combobox, 3, 2)

        filter_options.setLayout(filter_layout)

        layout.addWidget(filter_options)

        # Create apply and cancel buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Connect apply and cancel buttons
        apply_button.clicked.connect(filter_dialog.accept)
        cancel_button.clicked.connect(filter_dialog.reject)

        filter_dialog.setLayout(layout)

        result = filter_dialog.exec_()

        if result == QDialog.Accepted:
            # Retrieve filter values and apply the filter
            calendar_table = CalenderTable()


