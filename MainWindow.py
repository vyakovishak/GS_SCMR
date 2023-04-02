# MainWindow.py
from functools import partial
import re
import datetime
import json
from PySide6.QtWidgets import QWidget, QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QStatusBar, QDialog, QLabel, QListWidget, QCalendarWidget, \
    QGroupBox, QGridLayout, QCheckBox, \
    QComboBox, QDialogButtonBox, QMenu
from PySide6.QtGui import QAction
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QTimer, Signal
from DialogsWindow import LocationDialog, OperatorDialog, StatusDialog, CommentsDialog, CalendarDialog, \
    load_settings, ServiceOrderView, RescanOrdersDialog, AdminManagement, AdminLoginDialog, AboutDialog, TutorialDialog, \
    QRCodeGeneratorDialog, LocationWarningDialog
from ServiceOrderDB import ServiceOrderDB
from TableWidget import SCMRTable
from utils import load_settings


# Define the main window class
class MainWin(QMainWindow):
    # Initialize the window
    location_warning = Signal(str)

    def __init__(self):
        super(MainWin, self).__init__()
        self.resize(1444, 720)
        self.setWindowTitle("SCMR Management")

        self.setContentsMargins(0, 0, 0, 0)
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
        self.location_dialog = LocationDialog(self.db)
        self.location_dialog.location_warning.connect(self.show_location_warning)

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

        # Add menu bar and actions
        menubar = self.menuBar()

        admin_action = QAction("Admin", self)
        admin_action.triggered.connect(self.show_admin_login_dialog)
        menubar.addAction(admin_action)

        tutorial_action = QAction("Tutorial", self)
        tutorial_action.triggered.connect(self.show_tutorial)
        menubar.addAction(tutorial_action)

        qr_code_generator_action = QAction("QR Code Generator", self)
        qr_code_generator_action.triggered.connect(self.open_qr_code_generator)
        menubar.addAction(qr_code_generator_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        menubar.addAction(about_action)

        # Create a QVBoxLayout for delete button

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected_entry)
        self.rescan_button.clicked.connect(self.rescan_orders)
        self.calendar_button.clicked.connect(self.show_calendar_dialog)

        # Create a QHBoxLayout for the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.rescan_button)
        buttons_layout.addWidget(self.calendar_button)  # Admin button

        input_buttons_layout.addLayout(buttons_layout)
        # Add logo to the table

        # Add the QVBoxLayout to the main layout
        main_layout.addLayout(input_buttons_layout)


    def open_qr_code_generator(self):
        qr_code_generator_dialog = QRCodeGeneratorDialog()
        qr_code_generator_dialog.exec_()

    def add_logo_to_table(self):
        # Create a QLabel to hold the logo
        self.logo_label = QLabel(self.table_widget)

        # Set the logo as a QPixmap
        pixmap = QPixmap("gs_logo.png")

        # Scale the pixmap to a desired size
        pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio)  # Increase the size here

        # Set the pixmap to the QLabel
        self.logo_label.setPixmap(pixmap)

        # Align the logo to the center
        self.logo_label.setAlignment(Qt.AlignCenter)

    def show_tutorial(self):
        tutorial_dialog = TutorialDialog(self)
        tutorial_dialog.exec_()

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

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
            remaining_orders = len(self.db.select_all_unchecked_out())
            if remaining_orders > 0:
                rescan_orders_dialog = RescanOrdersDialog(self.db, operator)
                rescan_orders_dialog.refresh_main_table_signal.connect(self.refresh_main_table)

                rescan_orders_dialog.exec_()
            else:
                QMessageBox.information(None, "Information",
                                        "There are no more service orders that need to be scanned.")

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
            self.db.delete_service_order("YES", service_order, deleted_by)

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

        # Check if the input is a service order number
        if not re.match(r'^\d{14}$', scanned_input):
            # Check if the input is the last 4 digits of a service order number
            if re.match(r'^\d{4}$', scanned_input):
                service_orders = self.db.get_service_orders_by_last_digits(scanned_input)
                if service_orders:
                    # Create a list widget to display the matching service orders
                    list_widget = QListWidget()
                    for service_order in service_orders:
                        list_widget.addItem(service_order[0])

                    # Create a QDialog to display the matching service orders
                    match_dialog = QDialog(self)
                    match_dialog.setWindowTitle("Select Service Order")
                    match_dialog.resize(300, 200)

                    layout = QVBoxLayout(match_dialog)
                    layout.addWidget(QLabel("Select the service order:"))
                    layout.addWidget(list_widget)

                    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                    button_box.accepted.connect(match_dialog.accept)
                    button_box.rejected.connect(match_dialog.reject)
                    layout.addWidget(button_box)

                    # Show the match dialog and get the selected service order
                    if match_dialog.exec_():
                        selected_item = list_widget.currentItem()
                        if selected_item:
                            scanned_input = selected_item.text()
                        else:
                            QMessageBox.warning(self, "No Selection", "Please select a service order.")
                            return
                else:
                    QMessageBox.warning(self, "Invalid Input", "No service order found with the given last 4 digits.")
                    return
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid service order number.")
                return

        # Check if the service order is already in the database
        existing_service_order = self.db.select_unit(ServiceOrder=scanned_input)
        if len(existing_service_order) != 0:
            # Check if the service order is checked out
            checked_out = existing_service_order[0][-3]
            deleted = existing_service_order[0][-2]
            if existing_service_order and checked_out != "NO" or deleted != "NO":
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
                                                     check_out_by, scanned_input)
                        # Update the table
                        self.table_widget.load_data()
                        # Clear the input box
                        self.input_box.clear()
                        self.status_bar.showMessage(f"Serves Order {scanned_input} was checked out!")
                        return
        else:
            if self.location_dialog.exec_():
                location = self.location_dialog.location_input.text().upper()

                # Check if the location already exists
                if self.db.check_location_exists(location):
                    location_warning_dialog = LocationWarningDialog(location)
                    result = location_warning_dialog.exec_()
                    if result == QMessageBox.No:
                        return
                operator_dialog = OperatorDialog()
                if operator_dialog.exec_():
                    close_by = operator_dialog.get_operator()

                    # Display the status dialog
                    status_dialog = StatusDialog()
                    if status_dialog.exec_():
                        status = status_dialog.status
                        comments_dialog = CommentsDialog(status)
                        if comments_dialog.exec_():
                            comments = comments_dialog.comments_input.text()
                        else:
                            return

                        self.db.add_service_order(
                            ServiceOrder=scanned_input,
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

    def show_location_warning(self, location):
        msg_box = QMessageBox.warning(self, "Location already exists",
                                      f"The location '{location}' already exists. "
                                      "Do you want to add the unit to the current location or choose a different location?",
                                      QMessageBox.Yes | QMessageBox.No)

        if msg_box == QMessageBox.Yes:
            self.handle_scanner_input()
        else:
            return
