# TableWidget.py

from PySide6 import QtWidgets
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView, QDialog, QVBoxLayout, QLabel, \
    QItemDelegate
from PySide6.QtWidgets import QItemDelegate, QComboBox, QDialog, QVBoxLayout, QListWidget
from DialogsWindow import OperatorDialog, ServiceOrderEditorDialog, load_settings
from ServiceOrderDB import ServiceOrderDB
import json


class SCMRTable(QTableWidget):
    def __init__(self, db: ServiceOrderDB):
        super().__init__()
        self.db = db
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(
            ["Service Order", "Location", "Completion Date", "Closed By", "Status", "Comments", "Last Updated",
             "Updated By"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.load_data()

        # Connect the cellDoubleClicked signal to the custom function
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.cellDoubleClicked.connect(self.show_full_comments)

    @staticmethod
    def load_settings():
        with open("Settings.json", "r") as settings_file:
            operators = json.load(settings_file)
            all_operators = {'ARA': operators["Operators"]["ARA"], 'CA': operators["Operators"]["CA"], 'ALL': []}
            for operator in all_operators['ARA'] + all_operators['CA']:
                if operator not in all_operators['ALL']:
                    all_operators['ALL'].append(operator)
            return all_operators

    def on_cell_changed(self, row, column):
        if column == 5:
            check_out_dialog = OperatorDialog().get_operator()
            new_value = self.item(row, column).text()
            service_order = self.item(row, 0).text()
            self.db.update_comments(new_value, service_order, check_out_dialog)

    def load_data(self):
        self.setRowCount(0)
        data = self.db.select_all_unchecked_out()
        print(data)
        if data is not None:
            for row_number, row_data in enumerate(data):
                self.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        else:
            print("The database is empty.")

    def update_data(self):
        service_orders = self.db.select_all_service_orders()
        self.setRowCount(len(service_orders))

        for i, row_data in enumerate(service_orders):
            for j, column_data in enumerate(row_data):
                self.setItem(i, j, QTableWidgetItem(str(column_data)))

    def show_full_comments(self, row, column):
        # Get service order data for the selected row
        service_order_data = []
        for col in range(self.columnCount()):
            service_order_data.append(self.item(row, col).text())
        service_order_editor_dialog = ServiceOrderEditorDialog(service_order_data, self.db)
        if service_order_editor_dialog.exec_():
            # Refresh the table
            self.load_data()
