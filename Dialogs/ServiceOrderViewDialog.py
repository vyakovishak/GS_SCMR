# ---- Start for ServiceOrderView.py ---- #
import json
from PySide6 import QtWidgets
from PySide6.QtWidgets import QTableWidgetItem, QGroupBox, QHBoxLayout, QPushButton, QTableWidget

from Dialogs.DialogHelper import AlignCenterDelegate


class ServiceOrderView(QtWidgets.QDialog):
    def __init__(self, service_order_info):
        super().__init__()
        self.setContentsMargins(5, 5, 5, 5)

        self.service_order_info = service_order_info
        self.setup_ui()
        self.resize(1444, 880)

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

        # Add a label and input field for the check-out date
        check_out_date_label = QtWidgets.QLabel("Check Out Date:")
        check_out_date_input = QtWidgets.QLineEdit(str(self.service_order_info[9]))
        check_out_date_input.setReadOnly(True)
        layout.addRow(check_out_date_label, check_out_date_input)

        # Add a label and input field for whether the service order was checked out or not
        checked_out_label = QtWidgets.QLabel("Checked Out:")
        checked_out_input = QtWidgets.QLineEdit(self.service_order_info[10])
        checked_out_input.setReadOnly(True)
        layout.addRow(checked_out_label, checked_out_input)

        delete_label = QtWidgets.QLabel("Deleted:")
        delete_label_input = QtWidgets.QLineEdit(self.service_order_info[11])
        delete_label_input.setReadOnly(True)
        layout.addRow(delete_label, delete_label_input)

        # Add some spacing at the bottom of the layout
        layout.addItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # Add a QLabel for the service order updates
        updates_label = QtWidgets.QLabel("Updates:")
        layout.addRow(updates_label)

        # Call the show_service_order_updates method to display the updates table
        self.show_service_order_updates(self.service_order_info[0], layout)

        # Add some spacing at the bottom of the layout
        layout.addItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.setLayout(layout)

    def show_service_order_updates(self, service_order, layout):
        log_filename = "../Logs/update_log.json"
        with open(log_filename, "r") as log_file:
            data = json.load(log_file)

        service_order_key = str(service_order)
        updates = data.get(service_order_key, [])

        table = QTableWidget(self)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setItemDelegate(AlignCenterDelegate(self))
        table.resizeColumnsToContents()
        table.setColumnCount(9)  # Update the column count to 9
        table.setRowCount(len(updates))
        table.setHorizontalHeaderLabels(
            ["Timestamp", "Operation", "Agent", "Location", "Completion Date", "Closed By", "Status", "Comments",
             "Updated By", "Checked Out"
                           "CFI"])  # Update the header labels
        table.horizontalHeader().setStretchLastSection(True)

        for i, update in enumerate(sorted(updates, key=lambda x: x['timestamp'])):
            table.setItem(i, 0, QTableWidgetItem(update['timestamp']))
            table.setItem(i, 1, QTableWidgetItem(update['operation']))
            table.setItem(i, 2, QTableWidgetItem(update['operator']))  # Add operator to the table
            for j, key in enumerate(
                    ['Location', 'CompletionDate', 'ClosedBy', 'Status', 'Comments', 'CFI', "Updated By",
                     "Checked Out"], start=3):
                if key in update['changes']:
                    before = update['changes'][key]['before']
                    after = update['changes'][key]['after']

                    # Check if the values are lists and extract the first element if necessary
                    if isinstance(before, list) and len(before) == 1:
                        before = before[0]
                    if isinstance(after, list) and len(after) == 1:
                        after = after[0]

                    # Convert the value to a scalar if it's a single-element list
                    before = before[0] if isinstance(before, list) and len(before) == 1 else before
                    after = after[0] if isinstance(after, list) and len(after) == 1 else after

                    before_str = str(before) if before else ""
                    after_str = str(after)

                    table.setItem(i, j, QTableWidgetItem(f"{before_str} → {after_str}" if before_str else after_str))

        table.resizeColumnsToContents()
        table.setSortingEnabled(True)

        layout.addRow(table)


class CategoriesGroupBox(QGroupBox):
    def __init__(self, categories, show_res_codes_callback, parent=None):
        super().__init__("Categories", parent)
        categories_layout = QHBoxLayout()
        self.category_buttons = {}

        for category in categories:
            button = QPushButton(category)
            button.clicked.connect(show_res_codes_callback)
            categories_layout.addWidget(button)
            self.category_buttons[category] = button

        self.setLayout(categories_layout)
# ---- End for ServiceOrderView.py ---- #