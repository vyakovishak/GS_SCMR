# DialogsWindow.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QButtonGroup, \
    QMessageBox, QHBoxLayout, QTableWidget, QCalendarWidget, QCheckBox, QComboBox
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QCalendarWidget, QLabel, QPushButton, QCheckBox, QComboBox, \
    QHBoxLayout, QDialogButtonBox, QTableWidgetItem, QFormLayout, QHeaderView
from ServiceOrderDB import ServiceOrderDB

import json

from PySide6 import QtWidgets


class RescanOrdersDialog(QDialog):
    def __init__(self, db: ServiceOrderDB):
        super().__init__()

        self.setWindowTitle("Rescan Orders")
        self.db = db

        layout = QVBoxLayout(self)

        counter_layout = QHBoxLayout()
        self.scanned_orders_counter = QLabel("Scanned Orders: 0")
        self.remaining_orders_counter = QLabel("Remaining Orders: 0")
        counter_layout.addWidget(self.scanned_orders_counter)
        counter_layout.addWidget(self.remaining_orders_counter)
        layout.addLayout(counter_layout)

        self.table_widget = QTableWidget()
        self.load_data()
        layout.addWidget(self.table_widget)

        input_layout = QHBoxLayout()
        self.scanner_input = QLineEdit()
        self.scanner_input.setPlaceholderText("Scan service order")
        input_layout.addWidget(self.scanner_input)
        self.scanner_input.returnPressed.connect(self.handle_scanner_input)

        self.operator_selector = QComboBox()
        self.load_operators()
        input_layout.addWidget(self.operator_selector)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        input_layout.addWidget(self.close_button)

        layout.addLayout(input_layout)

    def load_data(self):
        # Load data from the database
        orders = self.db.select_not_checked_out_orders()

        # Set the table size and headers
        self.table_widget.setRowCount(len(orders))
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["SO#", "Location", "Completion Date", "Closed By", "Status", "Comments", "Check Out"])

        # Fill the table with data
        for row, order in enumerate(orders):
            for col, value in enumerate(order):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(row, col, item)

        self.table_widget.resizeColumnsToContents()

    def load_operators(self):
        operators = self.db.get_all_operators()
        for operator in operators:
            self.operator_selector.addItem(operator)

    def handle_scanner_input(self):
        scanned_input = self.scanner_input.text()
        existing_service_order = self.db.select_unit(ServiceOrder=scanned_input)

        if not existing_service_order:
            QMessageBox.warning(self, "Not Found", f"Service Order {scanned_input} not found in the database.")
            return

        location_dialog = LocationDialog()
        if location_dialog.exec_():
            new_location = location_dialog.location_input.text().upper()
            updated_by = self.operator_selector.currentText()
            last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.db.update_location(new_location, scanned_input, updated_by)
            self.db.update_updated_by(updated_by, scanned_input, updated_by)
            self.db.update_last_updated(last_updated, scanned_input, updated_by)

            self.load_data()
            self.update_counters()
            self.scanner_input.clear()

    def update_counters(self):
        scanned_orders = self.db.get_scanned_orders_count()
        remaining_orders = self.db.get_remaining_orders_count()

        self.scanned_orders_counter.setText(f"Scanned Orders: {scanned_orders}")
        self.remaining_orders_counter.setText(f"Remaining Orders: {remaining_orders}")

class ServiceOrderView(QtWidgets.QDialog):
    def __init__(self, service_order_info):
        super().__init__()
        self.service_order_info = service_order_info
        self.setup_ui()
        self.resize(400, 350)

    def setup_ui(self):
        self.setWindowTitle("Service Order Details")
        layout = QtWidgets.QFormLayout()

        # Add a label and input field for the service order number
        service_order_label = QtWidgets.QLabel("Service Order:")
        service_order_input = QtWidgets.QLineEdit(str(self.service_order_info[0]))
        service_order_input.setReadOnly(True)
        layout.addRow(service_order_label, service_order_input)

        # Add a label and input field for the location
        location_label = QtWidgets.QLabel("Location:")
        location_input = QtWidgets.QLineEdit(self.service_order_info[1])
        location_input.setReadOnly(True)
        layout.addRow(location_label, location_input)

        # Add a label and input field for the completion date
        completion_date_label = QtWidgets.QLabel("Completion Date:")
        completion_date_input = QtWidgets.QLineEdit(str(self.service_order_info[2]))
        completion_date_input.setReadOnly(True)
        layout.addRow(completion_date_label, completion_date_input)

        # Add a label and input field for the operator who closed the service order
        closed_by_label = QtWidgets.QLabel("Closed By:")
        closed_by_input = QtWidgets.QLineEdit(self.service_order_info[3])
        closed_by_input.setReadOnly(True)
        layout.addRow(closed_by_label, closed_by_input)

        # Add a label and input field for the status of the service order
        status_label = QtWidgets.QLabel("Status:")
        status_input = QtWidgets.QLineEdit(self.service_order_info[4])
        status_input.setReadOnly(True)
        layout.addRow(status_label, status_input)

        # Add a label and input field for the comments
        comments_label = QtWidgets.QLabel("Comments:")
        comments_input = QtWidgets.QLineEdit(self.service_order_info[5])
        comments_input.setReadOnly(True)
        layout.addRow(comments_label, comments_input)

        # Add a label and input field for the last updated date
        last_updated_label = QtWidgets.QLabel("Last Updated:")
        last_updated_input = QtWidgets.QLineEdit(str(self.service_order_info[6]))
        last_updated_input.setReadOnly(True)
        layout.addRow(last_updated_label, last_updated_input)

        # Add a label and input field for the operator who updated the service order
        updated_by_label = QtWidgets.QLabel("Updated By:")
        updated_by_input = QtWidgets.QLineEdit(self.service_order_info[7])
        updated_by_input.setReadOnly(True)
        layout.addRow(updated_by_label, updated_by_input)

        # Add a label and input field for the operator who checked out the service order
        check_out_by_label = QtWidgets.QLabel("Check Out By:")
        check_out_by_input = QtWidgets.QLineEdit(self.service_order_info[8])
        check_out_by_input.setReadOnly(True)
        layout.addRow(check_out_by_label, check_out_by_input)

        # Add a label and input field for the check out date
        check_out_date_label = QtWidgets.QLabel("Check Out Date:")
        check_out_date_input = QtWidgets.QLineEdit(str(self.service_order_info[9]))
        check_out_date_input.setReadOnly(True)
        layout.addRow(check_out_date_label, check_out_date_input)

        # Add a label and input field for whether the service order was checked out or not
        checked_out_label = QtWidgets.QLabel("Checked Out:")
        checked_out_input = QtWidgets.QLineEdit(str(bool(self.service_order_info[10])))

        # Display "True" or "False" instead of "1" or "0"
        checked_out_input.setText("True" if bool(self.service_order_info[10]) else "False")

        checked_out_input.setReadOnly(True)
        layout.addRow(checked_out_label, checked_out_input)

        # Add some spacing at the bottom of the layout
        layout.addItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.setLayout(layout)


class ServiceOrderEditorDialog(QDialog):
    def __init__(self, service_order_data, db: ServiceOrderDB):
        super().__init__()
        self.db = db
        self.all_operators = load_settings()['ALL']
        self.setWindowTitle("Edit Service Order")
        self.service_order_data = service_order_data

        layout = QVBoxLayout()

        # Service Order Number (unchangeable)
        so_number_layout = QHBoxLayout()
        so_number_label = QLabel("Service Order:")
        so_number_value = QLabel(str(self.service_order_data[0]))
        so_number_layout.addWidget(so_number_label)
        so_number_layout.addWidget(so_number_value)
        layout.addLayout(so_number_layout)

        # Location
        location_layout = QHBoxLayout()
        location_label = QLabel("Location:")
        self.location_input = QLineEdit(self.service_order_data[1])
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_input)
        layout.addLayout(location_layout)

        # Closed By (dropdown)
        closed_by_layout = QHBoxLayout()
        closed_by_label = QLabel("Closed By:")
        self.closed_by_input = QComboBox()
        self.closed_by_input.addItems(self.all_operators)
        self.closed_by_input.setCurrentText(self.service_order_data[3])
        closed_by_layout.addWidget(closed_by_label)
        closed_by_layout.addWidget(self.closed_by_input)
        layout.addLayout(closed_by_layout)

        # Status (dropdown)
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        self.status_input = QComboBox()
        self.status_input.addItem("GREEN")
        self.status_input.addItem("YELLOW")
        self.status_input.setCurrentText(self.service_order_data[4])
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_input)
        layout.addLayout(status_layout)

        # Comments
        comments_layout = QHBoxLayout()
        comments_label = QLabel("Comments:")
        self.comments_input = QLineEdit(self.service_order_data[5])
        comments_layout.addWidget(comments_label)
        comments_layout.addWidget(self.comments_input)
        layout.addLayout(comments_layout)

        # Submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_changes)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def submit_changes(self):
        # Retrieve the updated data
        location = self.location_input.text()
        closed_by = self.closed_by_input.currentText()
        status = self.status_input.currentText()
        comments = self.comments_input.text()
        service_order = int(self.service_order_data[0])
        operator = OperatorDialog().get_operator()
        # Update the database
        self.db.update_service_order(service_order, operator, Location=location, ClosedBy=closed_by, Status=status,
                                     Comments=comments)

        self.accept()


class CalendarDialog(QDialog):
    def __init__(self, operators, db):
        super().__init__()
        self.setWindowTitle("Select Date Range")
        self.resize(600, 400)
        self.start_date = None
        self.end_date = None
        self.db = db

        layout = QVBoxLayout()

        # Create calendar widget
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)

        # Label to display selected date range
        self.range_label = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.range_label.setFont(font)
        self.range_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.range_label)

        # Checkboxes and dropdowns for filtering service orders
        filters_layout = QHBoxLayout()

        # Filter by closed date checkbox
        self.close_date_checkbox = QCheckBox("By closed date")
        filters_layout.addWidget(self.close_date_checkbox)

        # Filter by updated date checkbox
        self.update_date_checkbox = QCheckBox("By updated date")
        filters_layout.addWidget(self.update_date_checkbox)

        self.checkout_checkbox = QCheckBox("Check Out")
        filters_layout.addWidget(self.checkout_checkbox)

        self.closed_by_label = QLabel("Closed By")
        filters_layout.addWidget(self.closed_by_label)

        self.closed_by = QComboBox()
        self.closed_by.addItems(operators['ARA'])
        filters_layout.addWidget(self.closed_by)

        self.checkout_by_label = QLabel("Check Out By")
        filters_layout.addWidget(self.checkout_by_label)

        self.checkout_by = QComboBox()
        self.checkout_by.addItems(operators['ALL'])
        filters_layout.addWidget(self.checkout_by)

        self.closed_by_label = QLabel("Status")
        filters_layout.addWidget(self.closed_by_label)
        self.status = QComboBox()
        self.status.addItems(['', 'GREEN', "YELLOW"])
        filters_layout.addWidget(self.status)

        layout.addLayout(filters_layout)

        # Apply and cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_button_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        self.calendar.clicked.connect(self.update_date_range)

    def update_date_range(self, clicked_date):
        if not self.start_date:
            self.start_date = clicked_date
            self.end_date = None
        elif not self.end_date:
            if clicked_date < self.start_date:
                self.start_date, self.end_date = clicked_date, self.start_date
            else:
                self.end_date = clicked_date
        else:
            self.start_date = clicked_date
            self.end_date = None

        # Update label with selected date range
        if self.start_date and not self.end_date:
            self.range_label.setText(self.start_date.toString("yyyy-MM-dd"))
        elif self.start_date and self.end_date:
            self.range_label.setText(
                f"{self.start_date.toString('yyyy-MM-dd')} - {self.end_date.toString('yyyy-MM-dd')}")

        # Update filter results
        self.calendar_clicked()

    def calendar_clicked(self):
        if not self.start_date:
            self.start_date = self.calendar.selectedDate()
        elif self.end_date is not None:
            self.end_date = self.calendar.selectedDate()
            self.range_label.setText(f"Selected range: {self.start_date.toString()} - {self.end_date.toString()}")
        else:
            self.start_date = self.calendar.selectedDate()
            self.range_label.setText(f"Date {self.start_date.toString()} selected")

    def apply_button_clicked(self):
        if self.start_date is None and self.end_date is None:
            QMessageBox.warning(self, "Warning", "Please select a date.")
            return
        # Get filter values
        closedDate = self.close_date_checkbox.isChecked()
        updateDate = self.update_date_checkbox.isChecked()
        checkout = self.checkout_checkbox.isChecked()
        closed_by = self.closed_by.currentText()
        checkout_by = self.checkout_by.currentText()
        status = self.status.currentText()
        start_date, end_date = self.start_date.toString(
            'yyyy-MM-dd'), self.end_date if self.end_date is None else self.end_date.toString('yyyy-MM-dd')

        # Create a query with filters
        query = "SELECT * FROM ServiceOrders WHERE 1 "

        if updateDate:
            if end_date is None:
                query += f" AND DATE(LastUpdated)='{start_date}'"
            else:
                query += f" AND DATE(LastUpdated) BETWEEN '{start_date}' AND '{end_date}'"

        if closedDate:
            if end_date is None:
                query += f" AND DATE(CompletionDate)='{start_date}'"
            else:
                query += f" AND DATE(CompletionDate) BETWEEN '{start_date}' AND '{end_date}'"

        if checkout:
            if end_date is None:
                query += f" AND DATE(CheckOutDate)='{start_date}'"
            else:
                query += f" AND DATE(CheckOutDate) BETWEEN '{start_date}' AND '{end_date}'"

        if checkout:
            query += f" AND CheckedOut=1"

        if closed_by:
            query += f" AND ClosedBy='{closed_by}'"

        if checkout_by:
            query += f" AND CheckOutBy='{checkout_by}'"

        if status:
            query += f" AND Status='{status}'"
        # Fetch data from the database
        results = self.db.execute(query, fetchall=True)

        # Create a QDialog to display the results
        result_dialog = QDialog(self)
        result_dialog.setWindowTitle("Filtered Results")
        result_dialog.resize(1800, 700)

        layout = QVBoxLayout(result_dialog)

        label = QLabel("Filtered Service Orders:")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Service Order", "Location", "Completion Date", "Closed By", "Status", "Comments",
            "Last Updated", "Updated By", "Check Out By", "Check Out Date"
        ])

        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table.cellDoubleClicked.connect(lambda row, : self.show_service_order(row))

        for row_data in results:
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table.setItem(row_number, column_number, item)

        layout.addWidget(self.table)

        # Add a close button to the dialog
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(result_dialog.reject)
        layout.addWidget(button_box)

        # Show the result dialog
        result_dialog.exec_()

    def get_selected_date_range(self):
        return self.start_date, self.end_date

    def show_service_order(self, row):
        service_order = self.table.item(row, 0).text()
        service_order_info = self.db.select_unit(ServiceOrder=service_order)
        ServiceOrderView(service_order_info[0]).exec()

# Define a QDialog for entering a location
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

# Define a QDialog for selecting who closed the service order
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

# Define a QDialog for selecting an operator
class OperatorDialog(QDialog):
    def __init__(self, operator_type="ALL"):
        super().__init__()
        self.operators = load_settings()[operator_type][1:]
        self.setWindowTitle("Select Operator")
        layout = QGridLayout()
        self.button_group = QButtonGroup()
        self.buttons = []
        for index, operator in enumerate(self.operators):
            button = QPushButton(operator)
            self.buttons.append(button)
            self.button_group.addButton(button, index)
            layout.addWidget(button, index // 2, index % 2)
        self.setLayout(layout)
        self.button_group.buttonClicked.connect(self.on_button_clicked)
        self.selected_operator = None

    def on_button_clicked(self, button):
        button_id = self.button_group.id(button)
        self.selected_operator = self.operators[button_id]
        self.accept()

    def get_operator(self):
        return self.selected_operator

# Define a QDialog for selecting a service order status
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

# Define a QDialog for entering comments
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


def load_settings():
    with open("Settings.json", "r") as settings_file:
        operators = json.load(settings_file)
        all_operators = {'ARA': operators["Operators"]["ARA"], 'CA': operators["Operators"]["CA"], 'ALL': []}
        for operator in all_operators['ARA'] + all_operators['CA']:
            if operator not in all_operators['ALL']:
                all_operators['ALL'].append(operator)
        return all_operators
