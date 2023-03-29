# MainWindow.py
from functools import partial

import datetime
import json
from PySide6.QtWidgets import QWidget, QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QStatusBar, QDialog, QLabel, QListWidget, QCalendarWidget, \
    QGroupBox, QGridLayout, QCheckBox, \
    QComboBox
from PySide6.QtGui import QIcon
from DialogsWindow import LocationDialog, OperatorDialog, StatusDialog, CommentsDialog, CalendarDialog, \
    load_settings, ServiceOrderView, RescanOrdersDialog, AdminManagement, AdminLoginDialog
from ServiceOrderDB import ServiceOrderDB
from TableWidget import SCMRTable
from WindowsLayout import LayoutSettings
from utils import load_settings


# Define the main window class
class MainWin(QMainWindow):
    # Initialize the window
    def __init__(self):
        super().__init__()
        self.resize(1080, 720)

        # Load application settings
        self.settings = load_settings()

        # Create a status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Create the central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a QVBoxLayout for the main layout
        main_layout = QVBoxLayout(central_widget)

        # Initialize the ServiceOrderDB and create the users table
        self.db = ServiceOrderDB(status_bar=self.status_bar)
        self.db.create_table_users()

        # Create an icon button for displaying the calendar dialog
        calendar_icon = QIcon("calendar_icon.png")
        self.calendar_button = QPushButton(calendar_icon, "")

        # Create a rescan button
        self.rescan_button = QPushButton("Rescan")
        self.rescan_button.clicked.connect(self.show_rescan_orders_dialog)

        # Create the SCMRTable for displaying service orders
        self.table_widget = SCMRTable(self.db)
        main_layout.addWidget(self.table_widget)

        # Create a QHBoxLayout for the input box and delete button

        input_buttons_layout = QVBoxLayout()

        # Create a QHBoxLayout for input box
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_label = QLabel("SO#")
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_box)
        self.input_box.returnPressed.connect(self.handle_scanner_input)

        input_buttons_layout.addLayout(input_layout)

        # Create the admin button
        self.admin_button = QPushButton("Admin")
        # Connect the admin button to the show_admin_login_dialog method
        self.admin_button.clicked.connect(self.show_admin_login_dialog)

        # Create a QVBoxLayout for delete button

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected_entry)
        self.rescan_button.clicked.connect(self.rescan_orders)
        self.calendar_button.clicked.connect(self.show_calendar_dialog)

        # Create a QHBoxLayout for the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.rescan_button)
        buttons_layout.addWidget(self.calendar_button)  # Admin button

        input_buttons_layout.addLayout(buttons_layout)

        # Add the QVBoxLayout to the main layout
        main_layout.addLayout(input_buttons_layout)

    # Inside the MainWin class

    @staticmethod
    def show_admin_login_dialog():
        admin_login_dialog = AdminLoginDialog()
        if admin_login_dialog.exec_():
            admin_management_dialog = AdminManagement()
            admin_management_dialog.exec_()

    def load_data(self):
        self.table_widget.load_data()

    def show_rescan_orders_dialog(self):
        operator_dialog = OperatorDialog()
        if operator_dialog.exec_():
            operator = operator_dialog.get_operator()

            rescan_orders_dialog = RescanOrdersDialog(self.db, operator)
            rescan_orders_dialog.refresh_main_table_signal.connect(self.refresh_main_table)

            rescan_orders_dialog.exec_()

    def refresh_main_table(self):
        self.load_data()

    # Display the calendar dialog
    def show_calendar_dialog(self):
        # Load settings and create the calendar dialog
        all_operators = load_settings()
        calendar_dialog = CalendarDialog(all_operators, self.db)
        calendar_dialog.exec_()

    # Delete the selected service order from the table and database
    def delete_selected_entry(self):
        operator_dialog = OperatorDialog()
        if operator_dialog.exec_():
            deleted_by = operator_dialog.get_operator()
            # Get the selected row
            selected_row = self.table_widget.currentRow()

            # If no row is selected, display a warning message and return
            if selected_row == -1:
                QMessageBox.warning(self, "No Selection", "Please select an entry to delete.")
                return
            # Get the service order number from the selected row
            service_order = self.table_widget.item(selected_row, 0).text()

            # Delete the service order from the database
            self.db.delete_service_order(service_order, deleted_by)

            # Remove the row from the table
            self.table_widget.removeRow(selected_row)

            # Display a message in the status bar
            self.status_bar.showMessage("No entry selected for deletion")
            self.status_bar.showMessage(f"Service Order: {service_order} was deleted from database!")

    def rescan_orders(self):
        operator = OperatorDialog().get_operator()
        if operator:
            rescan_orders_dialog = RescanOrdersDialog(self.db, operator)
            rescan_orders_dialog.exec_()

    # Handle input from the scanner
    def handle_scanner_input(self):
        # Get the scanned input from the input box
        scanned_input = self.input_box.text()
        # Check if the service order is already in the database

        existing_service_order = self.db.select_unit(ServiceOrder=scanned_input)

        # If the service order is already in the database and is checked out, display information about the service order
        if len(existing_service_order) != 0:
            # Check if the service order is checked out
            checked_out = existing_service_order[0][-2]
            if existing_service_order and checked_out != 0:
                service_order_dialog = ServiceOrderView(existing_service_order[0])
                service_order_dialog.exec_()
                return
            else:
                operator_dialog = OperatorDialog()
                if operator_dialog.exec_():
                    check_out_by = operator_dialog.get_operator()
                    if check_out_by != 1:
                        # Update the CheckOut value, CheckOutDate, and CheckOutBy in the database
                        self.db.update_checkout_info(1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                     check_out_by, scanned_input, check_out_by)
                        # Update the table
                        self.table_widget.load_data()
                        # Clear the input box
                        self.input_box.clear()
                        self.status_bar.showMessage(f"Serves Order {scanned_input} was checked out!")
                        return
        # If the service order is not already in the database, prompt the user for information and add it to the database
        else:
            # Display the location dialog
            location_dialog = LocationDialog()
            if location_dialog.exec_():
                location = location_dialog.location_input.text().upper()

                # Display the operator dialog
                operator_dialog = OperatorDialog()
                if operator_dialog.exec_():
                    close_by = operator_dialog.get_operator()

                    # Display the status dialog
                    status_dialog = StatusDialog()
                    if status_dialog.exec_():
                        status = status_dialog.status

                        # Display the comments dialog
                        comments_dialog = CommentsDialog(status)
                        if comments_dialog.exec_():
                            comments = comments_dialog.comments_input.text()
                        else:
                            return

                        # Add the service order to the database
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

                        # Display a message in the status bar
                        self.status_bar.showMessage(f"Service Order {scanned_input} was added to database!")

        # Clear the input box
        self.input_box.clear()
