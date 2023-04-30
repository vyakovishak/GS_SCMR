# ---- Start for TableWidget.py ---- #

from PySide6 import QtWidgets
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QLabel, \
    QPushButton
from PySide6.QtWidgets import QItemDelegate, QDialog, QVBoxLayout

from Dialogs.OperatorDialog import OperatorDialog
from Database.ServiceOrderDB import ServiceOrderDB
import json
from PySide6.QtCore import Qt

from Dialogs.ServiceOrderEditorDialog import ServiceOrderEditorDialog
from Dialogs.ServiceOrderViewDialog import ServiceOrderView


class AlignCenterDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(AlignCenterDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        return None

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignHCenter | Qt.AlignVCenter
        super(AlignCenterDelegate, self).paint(painter, option, index)


class SCMRTable(QTableWidget):
    def __init__(self, db: ServiceOrderDB):
        super().__init__()
        self.db = db
        self.setColumnCount(8)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setItemDelegate(AlignCenterDelegate(self))
        self.resizeColumnsToContents()
        self.setHorizontalHeaderLabels(
            ["Service Order", "Location", "Completion Date", "Closed By", "Status", "Comments", "Last Updated",
             "Updated By"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.load_data()

        # Connect the cellDoubleClicked signal to the custom function
        self.cellDoubleClicked.connect(self.show_full_comments)

    def on_cell_changed(self, row, column):
        if column == 5:
            check_out_dialog = OperatorDialog().get_operator()
            new_value = self.item(row, column).text()
            service_order = self.item(row, 0).text()
            self.db.update_comments(new_value, service_order, check_out_dialog)

    def load_data(self):
        self.setRowCount(0)
        data = self.db.select_all_unchecked_out()
        if data is not None:
            for row_number, row_data in enumerate(data):
                self.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def update_data(self):
        service_orders = self.db.select_all_unchecked_out()
        self.setRowCount(len(service_orders))

        for i, row_data in enumerate(service_orders):
            for j, column_data in enumerate(row_data):
                self.setItem(i, j, QTableWidgetItem(str(column_data)))

    def show_full_comments(self, row, column):
        # Get service order data for the selected row
        # Display the operator dialog
        operator_dialog = OperatorDialog()
        if operator_dialog.exec_():
            editing_by = operator_dialog.get_operator()
            service_order_data = []
            for col in range(self.columnCount()):
                service_order_data.append(self.item(row, col).text())

            service_order_editor_dialog = ServiceOrderEditorDialog(service_order_data, self.db, editing_by)
            if service_order_editor_dialog.exec_():
                # Refresh the table
                self.load_data()
                self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Add this line


class ServiceOrderUpdatesLogTable(QTableWidget):
    def __init__(self, service_order, parent=None):
        super().__init__(parent)
        self.service_order = service_order
        self.init_table()

    def init_table(self):
        log_filename = "./Logs/update_log.json"
        with open(log_filename, "r") as log_file:
            data = json.load(log_file)

        service_order_key = str(self.service_order)
        updates = data.get(service_order_key, [])

        self.setColumnCount(10)  # Increase the column count to 12
        self.setRowCount(len(updates))
        self.setHorizontalHeaderLabels(
            ["Timestamp", "Operation", "Agent", "Location", "Completion Date", "Closed By", "Status",
             "Comments", "Updated By", "Res Codes"])  # Add "FOB", "FOP", and "Res Codes" to the header labels
        self.horizontalHeader().setStretchLastSection(True)

        for i, update in enumerate(sorted(updates, key=lambda x: x['timestamp'])):
            self.setItem(i, 0, QTableWidgetItem(update['timestamp']))
            self.setItem(i, 1, QTableWidgetItem(update['operation']))
            self.setItem(i, 2, QTableWidgetItem(update['operator']))
            for j, key in enumerate(
                    ['Location', 'CompletionDate', 'ClosedBy', 'Status', 'Comments', 'UpdatedBy', 'ResCodes'],
                    start=3):
                if key in update['changes']:
                    if key == 'ResCodes':
                        codes = ', '.join(update['changes'][key]['after']['Code'])
                        self.setItem(i, j, QTableWidgetItem(codes))
                    else:
                        before = str(update['changes'][key]['before']) if update['changes'][key]['before'] else ""
                        after = str(update['changes'][key]['after'])
                        self.setItem(i, j, QTableWidgetItem(f"{before} → {after}" if before else after))

        self.setItemDelegate(AlignCenterDelegate(self))
        self.resizeColumnsToContents()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch out all the columns
        self.setSortingEnabled(True)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item is not None:
            row = item.row()
            update = {}
            for j, key in enumerate(
                    ["Timestamp", "Operation", "Agent", "Location", "Completion Date", "Closed By", "Status",
                     "Comments", "Updated By", "Res Codes"]):
                table_item = self.item(row, j)
                update[key] = table_item.text() if table_item else ""
            self.show_update_viewer(update)

    def show_update_viewer(self, update):
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Viewer")
        dialog.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout(dialog)
        for key, value in update.items():
            label = QLabel(f"{key}: {value}")
            layout.addWidget(label)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)

        dialog.exec()


class CalendarTable(QTableWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setColumnCount(12)
        self.setHorizontalHeaderLabels([
            "Service Order", "Location", "Completion Date", "Closed By", "Status", "Comments",
            "Last Updated", "Updated By", "Check Out By", "Check Out Date", "Check out", "CFI"
        ])

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.update_table()

    def update_table(self):
        self.setRowCount(0)
        for row_data in self.db:
            row_number = self.rowCount()
            self.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                print(row_data)
                print(column_number)
                item.setTextAlignment(Qt.AlignCenter)  # Center the text in table cells
                self.setItem(row_number, column_number, item)
        self.resizeColumnsToContents()
        self.setSortingEnabled(True)

        self.cellDoubleClicked.connect(self.show_order_info)

    def show_order_info(self, row, column):
        service_order = self.item(row, 0).text()  # get the service order value from the clicked cell
        service_data = next((data for data in self.db if data[0] == service_order),
                            None)  # find the matching row in self.db
        if service_data is not None:
            view_dialog = ServiceOrderView(service_data)
            view_dialog.exec_()

# ---- End for TableWidget.py ---- #
