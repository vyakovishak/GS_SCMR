from PySide6 import QtWidgets
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView, QDialog, QVBoxLayout, QLabel, QItemDelegate
from PySide6.QtWidgets import QItemDelegate, QComboBox, QDialog, QVBoxLayout, QListWidget
from DialogsWindow import OperatorDialog
from ServiceOrderDB import ServiceOrderDB
import MainWIndow

class StatusDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(StatusDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItem("Yellow")
        editor.addItem("Green")
        editor.currentIndexChanged.connect(self.show_operator_dialog)
        return editor

    def setEditorData(self, editor, index):
        value = index.data()
        editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def show_operator_dialog(self):
        operators = MainWIndow.MainWin.load_settings()
        all_operators = operators["Operators"]["ARA"] + operators["Operators"]["CA"]

        check_out_dialog = OperatorDialog([*set(all_operators)])
        if check_out_dialog.exec_():
            check_out_by = all_operators[check_out_dialog.button_group.checkedId()]
            list_widget = QListWidget()
            list_widget.addItems(check_out_by)
            # Connect the itemClicked signal to a custom slot
            list_widget.itemClicked.connect(self.on_operator_selected(check_out_by))

            check_out_dialog.exec_()

    def on_operator_selected(self, item):
        selected_operator = item
        print(selected_operator)
        # Save the new status and selected operator to the database and log the changes
        # You will need to modify this part to access the service order number and the new status value
        service_order = ...
        new_status = ...

        self.db.update_status(new_status, service_order, selected_operator)
        self.db.log_update("Updated Status", so=service_order, operator=selected_operator, status=new_status)

        self.parent().refresh_table()
        self.parent().parent().close()


class SCMRTable(QTableWidget):
    def __init__(self, db: ServiceOrderDB):
        super().__init__()
        self.db = db
        self.setItemDelegateForColumn(4, StatusDelegate(self))
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(
            ["Service Order", "Location", "Completion Date", "Closed By", "Status", "Comments", "Last Updated",
             "Updated By"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.load_data()

        # Connect the cellDoubleClicked signal to the custom function
        self.cellChanged.connect(self.on_cell_changed)
        self.cellDoubleClicked.connect(self.show_full_comments)

    def on_cell_changed(self, row, column):
        new_value = self.item(row, column).text()
        service_order = self.item(row, 0).text()

        # Update the database with the new value
        # Replace the 'if' conditions with the corresponding column numbers
        if column == 1:
            self.db.update_location(new_value, service_order, list_widget.itemClicked)
        elif column == 2:
            self.db.update_completion_date(new_value, service_order, list_widget.itemClicked)
        elif column == 3:
            self.db.update_closed_by(new_value, service_order, list_widget.itemClicked)
        elif column == 4:
            self.db.update_status(new_value, service_order, list_widget.itemClicked)
        elif column == 5:
            self.db.update_comments(new_value, service_order, "test")
        # Add other columns if needed

        # Refresh the table to show the updated data
        # self.load_data()

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
        # Check if the double-clicked cell is in the "Comments" column
        if column == 5:
            comments = self.item(row, column).text()

            # Create a new QDialog to show the full comments
            comments_dialog = QDialog(self)
            comments_dialog.setWindowTitle("Full Comments")
            comments_dialog.resize(150, 50)
            layout = QVBoxLayout()
            label = QLabel(comments)
            layout.addWidget(label)
            comments_dialog.setLayout(layout)

            # Show the QDialog
            comments_dialog.exec_()
