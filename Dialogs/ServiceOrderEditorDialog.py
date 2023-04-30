# ---- Start for ServiceOrderEditorDialog.py ---- #
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QDialog, QMessageBox, QPushButton, QLabel, QGroupBox, QLineEdit, QComboBox, QFormLayout, \
    QHBoxLayout, QVBoxLayout

from Database.ServiceOrderDB import ServiceOrderDB
from Dialogs.DialogHelper import LocationWarningDialog
from Dialogs.ResCodeManagementDialog import ResCodeManagementDialog

from Utilities.utils import get_res_code, load_agents


class ServiceOrderEditorDialog(QDialog):
    def __init__(self, service_order_data, db: ServiceOrderDB, editing_by):
        super().__init__()
        self.editing_by = editing_by
        self.setContentsMargins(5, 5, 5, 5)

        self.db = db
        self.all_operators = load_agents(agent_names_only=True)
        self.setWindowTitle("Edit Service Order")
        self.service_order_data = service_order_data
        self.resize(1444, 720)
        self.res_code_data = get_res_code()
        layout = QVBoxLayout()

        # Create QHBoxLayout to hold General Information and Res Code Information side by side
        main_horizontal_layout = QHBoxLayout()

        # General Information layout
        general_info_groupbox = QGroupBox("General Information")
        general_info_layout = QFormLayout()

        # Service Order Number (unchangeable)
        so_number_label = QLabel("Service Order:")
        so_number_value = QLabel(str(self.service_order_data[0]))
        general_info_layout.addRow(so_number_label, so_number_value)

        # Location
        location_label = QLabel("Location:")
        self.location_input = QLineEdit(self.service_order_data[1])
        general_info_layout.addRow(location_label, self.location_input)

        # Closed By (dropdown)
        closed_by_label = QLabel("Closed By:")
        self.closed_by_input = QComboBox()
        self.closed_by_input.addItems(self.all_operators)
        self.closed_by_input.setCurrentText(self.service_order_data[3])
        general_info_layout.addRow(closed_by_label, self.closed_by_input)

        # Status (dropdown)
        status_label = QLabel("Status:")
        self.status_input = QComboBox()
        self.status_input.addItem("GREEN")
        self.status_input.addItem("YELLOW")
        self.status_input.setCurrentText(self.service_order_data[4])
        general_info_layout.addRow(status_label, self.status_input)

        # Comments
        comments_label = QLabel("Comments:")
        self.comments_input = QLineEdit(self.service_order_data[5])
        general_info_layout.addRow(comments_label, self.comments_input)

        general_info_groupbox.setLayout(general_info_layout)
        main_horizontal_layout.addWidget(general_info_groupbox)  # fixed variable name

        # Create a QGroupBox for the Res Code related input fields
        res_code_info_groupbox = QGroupBox("Res Code Information")
        res_code_input_layout = QFormLayout()

        # Res Code
        res_code_label = QLabel("Res Code:")
        self.res_code_value = QLabel(str(self.service_order_data[1]))
        res_code_input_layout.addRow(res_code_label, self.res_code_value)

        # BOP Time
        bop_time_label = QLabel("BOP Time:")
        self.bop_time_value = QLabel(str(self.service_order_data[1]))
        res_code_input_layout.addRow(bop_time_label, self.bop_time_value)

        # FOP
        fop_label = QLabel("FOP Time:")
        self.fop_value = QLabel(str(self.service_order_data[1]))
        res_code_input_layout.addRow(fop_label, self.fop_value)

        # Total Time for BOP and FOP
        total_time_label = QLabel("Total Time:")
        self.total_time_value = QLabel(str(self.service_order_data[1]))
        res_code_input_layout.addRow(total_time_label, self.total_time_value)

        # Add Res Codes button
        self.add_res_codes_button = QPushButton("Add Res Codes")
        self.add_res_codes_button.clicked.connect(self.update_res_codes)
        res_code_input_layout.addRow(self.add_res_codes_button)

        res_code_info_groupbox.setLayout(res_code_input_layout)

        main_horizontal_layout.addWidget(res_code_info_groupbox)
        main_horizontal_layout.addSpacing(300)
        layout.addLayout(main_horizontal_layout)

        # Submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_changes)
        layout.addWidget(submit_button, alignment=Qt.AlignCenter)

        from Widgets.TableWidget import ServiceOrderUpdatesLogTable
        log_table = ServiceOrderUpdatesLogTable(service_order_data[0], self)
        self.location_input.setFixedSize(200, 25)
        self.closed_by_input.setFixedSize(200, 25)
        self.status_input.setFixedSize(200, 25)
        self.comments_input.setFixedSize(200, 25)
        layout.addWidget(log_table)
        self.load_res_codes_from_log()
        self.setLayout(layout)

    def load_res_codes_from_log(self):
        service_order_data = self.db.select_service_order(self.service_order_data[0])
        res_codes = "None" if service_order_data[0][13] is None else eval(service_order_data[0][13])
        res_codes_str = ", ".join(res_codes) if res_codes is not None else "None"

        bop_time = service_order_data[0][14]
        fop_time = service_order_data[0][15]
        total_time = service_order_data[0][16]

        self.res_code_value.setText(res_codes_str)
        self.bop_time_value.setText(str(bop_time))
        self.fop_value.setText(str(fop_time))
        self.total_time_value.setText(str(total_time))

    def submit_changes(self):
        # Retrieve the updated data
        location = self.location_input.text()
        closed_by = self.closed_by_input.currentText()
        status = self.status_input.currentText()
        comments = self.comments_input.text()
        service_order = self.service_order_data[0]

        # Create a dictionary to store the changed values
        before = {}
        after = {}

        # Compare the initial values with the updated values and store the changes
        if location != self.service_order_data[1]:
            before["Location"] = self.service_order_data[1]
            after["Location"] = location
        if closed_by != self.service_order_data[3]:
            before["ClosedBy"] = self.service_order_data[3]
            after["ClosedBy"] = closed_by
        if status != self.service_order_data[4]:
            before["Status"] = self.service_order_data[4]
            after["Status"] = status
        if comments != self.service_order_data[5]:
            before["Comments"] = self.service_order_data[5]
            after["Comments"] = comments

        location_exists = self.db.check_location_exists(location)

        if location_exists and "Location" in after:
            location_warning_dialog = LocationWarningDialog(location)
            if location_warning_dialog.exec_():
                pass
            else:
                return
        if after:
            self.db.update_service_order(service_order, self.editing_by, before=before, after=after)
        self.accept()

    def show_res_code_management_dialog(self):

        # Instantiate the ResCodeManagementDialog with the res code data
        res_code_management_dialog = ResCodeManagementDialog(self.res_code_data)
        result = res_code_management_dialog.exec_()

        if result == QDialog.Accepted:
            selected_res_codes = res_code_management_dialog.get_selected_res_codes()
            self.update_res_codes()

    def update_res_codes(self):
        if self.editing_by != self.closed_by_input.currentText():
            QMessageBox.warning(self, "Permission Denied",
                                "Only the agent who closed the service order can add res codes.")
            return
        res_code_dialog = ResCodeManagementDialog(self.res_code_data)
        result = res_code_dialog.exec()

        if result == QDialog.Accepted:
            selected_res_codes = res_code_dialog.get_selected_res_codes()
            selected_res_codes_str = ', '.join(selected_res_codes)

            self.res_code_value.setText(selected_res_codes_str)

            # Calculate the total BOP and FOP times
            total_bop_time = 0
            total_fop_time = 0
            for res_code in selected_res_codes:
                selected_category = None
                for category, res_codes in self.res_code_data.items():
                    if res_code in res_codes:
                        selected_category = category
                        break
                res_code_data = self.res_code_data[selected_category][res_code]
                total_bop_time += int(res_code_data["bop"])
                total_fop_time += int(res_code_data["fop"])

            # Update BOP Time, FOP Time, and Total Time
            self.bop_time_value.setText(str(total_bop_time))
            self.fop_value.setText(str(total_fop_time))
            self.total_time_value.setText(str(total_bop_time + total_fop_time))
            after = {
                "ResCodes": {"Code": selected_res_codes,
                             "BOB_time": total_bop_time,
                             "FOP_time": total_fop_time,
                             "Total_time": total_bop_time + total_fop_time}

            }
            self.db.update_res_codes(res_code_data=after, so=self.service_order_data[0], operator=self.editing_by)
# ---- End for ServiceOrderEditorDialog.py ---- #