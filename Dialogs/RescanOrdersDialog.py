# ---- Start for RescanOrdersDialog.py ---- #
import datetime
import re

from PySide6 import QtWidgets
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QLineEdit, QPushButton, QMessageBox, QTableWidgetItem, QHeaderView, QHBoxLayout, QLabel, \
    QVBoxLayout, QTableWidget, QDialog
from PySide6.QtCore import Signal
from Dialogs.DialogHelper import LocationWarningDialog, AlignCenterDelegate
from Dialogs.LocationDialog import LocationDialog
from Database.ServiceOrderDB import ServiceOrderDB


class RescanOrdersDialog(QDialog):
    refresh_main_table_signal = Signal()

    def __init__(self, db: ServiceOrderDB, operator: str):
        super().__init__()
        self.setContentsMargins(5, 5, 5, 5)

        self.db = db
        self.scanned_orders = 0
        self.setWindowTitle("Rescan Orders")
        self.operator = operator
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_widget.setItemDelegate(AlignCenterDelegate(self))
        self.table_widget.resizeColumnsToContents()

        self.remaining_orders = len(self.db.select_all_unchecked_out())  # Initialize remaining_orders

        if self.remaining_orders > 0:
            self.init_dialog()
        else:
            self.close_and_refresh()

    def init_dialog(self):

        self.setWindowTitle("Rescan Orders")

        layout = QVBoxLayout(self)

        counter_layout = QHBoxLayout()
        self.scanned_orders_counter = QLabel(f"Scanned Orders: {self.scanned_orders}")
        self.remaining_orders = len(self.db.select_all_unchecked_out())  # Initialize remaining_orders
        self.remaining_orders_counter = QLabel(f"Remaining Orders: {self.remaining_orders}")
        counter_layout.addWidget(self.scanned_orders_counter)
        counter_layout.addWidget(self.remaining_orders_counter)
        layout.addLayout(counter_layout)

        self.load_data()
        self.resize(1080, 720)
        layout.addWidget(self.table_widget)

        input_layout = QHBoxLayout()
        self.scanner_input = ScannerInput()
        self.scanner_input.setPlaceholderText("Scan service order")
        input_layout.addWidget(self.scanner_input)
        self.scanner_input.returnPressed.connect(self.handle_scanner_input)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_and_refresh)
        input_layout.addWidget(self.close_button)

        self.table_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        layout.addLayout(input_layout)

    def close_and_refresh(self):
        self.refresh_main_table_signal.emit()
        self.accept()

    def load_data(self):
        # Load data from the database
        orders = self.db.select_all_scanned_out()

        if len(orders) != 0:

            # Set the table size and headers
            self.table_widget.setRowCount(len(orders))
            self.table_widget.setColumnCount(8)  # Change to 8 to accommodate the CFI button
            self.table_widget.setHorizontalHeaderLabels(
                ["SO#", "Location", "Completion Date", "Closed By", "Status", "Comments", "Check Out", "CFI"])
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

            # Fill the table with data
            for row, service_order in enumerate(orders):
                for col, data in enumerate(service_order):
                    item = QTableWidgetItem(str(data))
                    self.table_widget.setItem(row, col, item)
                cfi_button = CFIButton("CFI", service_order)
                cfi_button.clicked.connect(self.handle_cfi_button)
                self.table_widget.setCellWidget(row, 7, cfi_button)  # Set CFI button in the 8th column
        else:
            self.check_and_reset_scanned_status()

        self.table_widget.setRowCount(len(orders))

    def check_and_reset_scanned_status(self):
        unscanned_orders = self.db.select_all_scanned_out()
        if not unscanned_orders:
            reply = QMessageBox.information(self, "Information", "There are no more service orders that need to be "
                                                                 "scanned. (Press okay to close)")
            if reply == QMessageBox.Ok:
                scanned_orders = self.db.select_all_unchecked_out()  # Create this method in ServiceOrderDB
                for order in scanned_orders:
                    self.db.update_service_order(ServiceOrder=order[0], operator=self.operator,
                                                 before={"Scanned": True},
                                                 after={"Scanned": False},
                                                 log=False)
                # Emit the signal to refresh the main table
                self.refresh_main_table_signal.emit()

                # Close the RescanOrdersDialog
                self.close_and_refresh()

    def handle_cfi_button(self):
        clicked_button = self.sender()
        service_order = clicked_button.service_order

        reply = QMessageBox.warning(self, "Warning", "Are you sure you want to delete this service order?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_service_order(status='YES', so=service_order[0], operator=self.operator)
            self.load_data()

    def update_counters(self):
        self.scanned_orders_counter.setText(f"Scanned Orders: {self.scanned_orders}")
        self.remaining_orders_counter.setText(f"Remaining Orders: {self.remaining_orders}")

    def handle_scanner_input(self):
        scanned_input = self.scanner_input.text()
        # Check if the input is a valid service order number
        if re.match(r'^\d{14}$', scanned_input):
            # Check if the service order is already in the database
            existing_service_order = self.db.select_unit(ServiceOrder=scanned_input)
            print("Here is order:" + str(existing_service_order))

            # If the service order is in the database and not checked out
            if existing_service_order:
                print(existing_service_order[0][-7])
                if existing_service_order[0][-7] == "NO":
                    # Display the location dialog
                    location_dialog = LocationDialog(self.db, existing_service_order[0][1])
                    if location_dialog.exec_():

                        location = location_dialog.location_input.text().upper()
                        if self.db.check_location_exists(location):
                            location_warning_dialog = LocationWarningDialog(location)
                            result = location_warning_dialog.exec_()
                            if result == QMessageBox.No:
                                return
                        last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Update the location, updated_by, scanned_status, and last_updated in the database
                        self.db.rescan_service_order_update(location, self.operator, 1, last_updated, scanned_input,
                                                            self.operator)
                        self.load_data()

                        # Update the counters
                        self.scanned_orders += 1
                        self.remaining_orders -= 1
                        self.update_counters()

                        # Clear the input box
                        self.scanner_input.clear()

                        # Emit the signal to refresh the main table
                        self.refresh_main_table_signal.emit()

                else:
                    QMessageBox.information(self, "Information", "Service Order was updated already!")
            else:
                QMessageBox.information(self, "Information", "Service order not found.")
        else:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid service order number.")
            self.scanner_input.clear()
            return
        # Clear the input box
        self.scanner_input.clear()
        # self.load_data()

        # Emit the signal to refresh the main table
        self.refresh_main_table_signal.emit()


class ScannerInput(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.returnPressed.emit()
            event.accept()
        else:
            super().keyPressEvent(event)


class CFIButton(QPushButton):
    def __init__(self, text, service_order, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.service_order = service_order
# ---- End for RescanOrdersDialog.py ---- #