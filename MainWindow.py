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
    ServiceOrderEditorDialog, load_settings, ServiceOrderView, RescanOrdersDialog
from ServiceOrderDB import ServiceOrderDB
from TableWidget import SCMRTable
from WindowsLayout import LayoutSettings


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
        self.rescan_button = QPushButton("RESCAN")
        self.rescan_button.clicked.connect(self.show_rescan_orders_dialog)

        # Create the SCMRTable for displaying service orders
        self.table_widget = SCMRTable(self.db)
        main_layout.addWidget(self.table_widget)

        # Create a QHBoxLayout for the input box and delete button
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
        delete_layout.addWidget(self.calendar_button)
        delete_layout.addWidget(self.delete_button)
        delete_layout.addWidget(self.rescan_button)
        self.delete_button.clicked.connect(self.delete_selected_entry)
        self.rescan_button.clicked.connect(self.rescan_orders)
        input_delete_layout.addLayout(delete_layout)
        self.calendar_button.clicked.connect(self.show_calendar_dialog)

        # Add the QHBoxLayout to the QVBoxLayout
        main_layout.addLayout(input_delete_layout)

    def show_rescan_orders_dialog(self):

        rescan_orders_dialog = RescanOrdersDialog(self.db)

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
        # Get the selected row
        selected_row = self.table_widget.currentRow()

        # If no row is selected, display a warning message and return
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select an entry to delete.")
            return
        # Get the service order number from the selected row
        service_order = self.table_widget.item(selected_row, 0).text()

        # Delete the service order from the database
        service_order_db = ServiceOrderDB()
        service_order_db.delete_service_order(service_order, operator="Some Operator")

        # Remove the row from the table
        self.table_widget.removeRow(selected_row)

        # Display a message in the status bar
        self.status_bar.showMessage("No entry selected for deletion")
        self.status_bar.showMessage(f"Service Order: {service_order} was deleted from database!")

    def rescan_orders(self):
        operator = OperatorDialog("ALL").get_operator()
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
        if existing_service_order:
            # Check if the service order is checked out
            checked_out = existing_service_order[0][-1]

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
                        self.db.update_checked_out(True, scanned_input, check_out_by)
                        self.db.update_check_out_date(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                      scanned_input,
                                                      check_out_by)
                        self.db.update_check_out_by(check_out_by, scanned_input, check_out_by)

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
