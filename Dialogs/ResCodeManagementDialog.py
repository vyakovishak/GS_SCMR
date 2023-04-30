# ---- Start for RescanOrdersDialog.py ---- #
from PySide6.QtWidgets import QMessageBox, QPushButton, QLabel, QLineEdit, QVBoxLayout, QDialog, QGridLayout, QGroupBox

from Dialogs.ServiceOrderViewDialog import CategoriesGroupBox


class ResCodesGroupBox(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.res_code_layout = QGridLayout()
        self.setLayout(self.res_code_layout)
        self.res_code_buttons = {}

    def show_res_codes(self, category, res_codes):
        self.clear_res_code_layout()
        self.setTitle(category)

        row = 0
        col = 0
        for code, data in res_codes.items():
            button = QPushButton(code)
            button.clicked.connect(self.parent().select_res_code)
            self.res_code_layout.addWidget(button, row, col)
            self.res_code_buttons[code] = button
            col += 1
            if col == 3:
                col = 0
                row += 1
        self.res_code_layout.setRowStretch(row, 1)

    def clear_res_code_layout(self):
        for i in reversed(range(self.res_code_layout.count())):
            self.res_code_layout.itemAt(i).widget().hide()


class ResCodeManagementDialog(QDialog):
    def __init__(self, res_code_data):
        super().__init__()
        self.setWindowTitle("Res Code Management")
        self.res_code_data = res_code_data
        self.resize(320, 240)
        layout = QVBoxLayout()
        self.selected_res_codes_count = 0
        self.categories_group_box = CategoriesGroupBox(["Apple", "Samsung", "GeekSquad"], self.show_res_codes)
        layout.addWidget(self.categories_group_box)

        self.res_codes_group_box = ResCodesGroupBox(self)
        layout.addWidget(self.res_codes_group_box)

        self.selected_res_codes_input = QLineEdit()
        self.selected_res_codes_input.setReadOnly(True)
        layout.addWidget(self.selected_res_codes_input)

        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.accept)
        layout.addWidget(self.done_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_selected_res_codes)
        layout.addWidget(self.clear_button)

        self.fop_time_label = QLabel("FOP Time: 0")
        layout.addWidget(self.fop_time_label)

        self.bop_time_label = QLabel("BOP Time: 0")
        layout.addWidget(self.bop_time_label)

        self.total_time_label = QLabel("Total Time: 0")
        layout.addWidget(self.total_time_label)

        self.setLayout(layout)

    def clear_selected_res_codes(self):
        self.selected_res_codes_input.clear()
        self.selected_res_codes_count = 0
        for button in self.res_codes_group_box.res_code_buttons.values():
            button.setDisabled(False)
            button.setStyleSheet("")

        # Enable category buttons
        for button in self.categories_group_box.category_buttons.values():
            button.setDisabled(False)

        self.fop_time_label.setText("FOP Time: 0")
        self.bop_time_label.setText("BOP Time: 0")
        self.total_time_label.setText("Total Time: 0")

    def enable_categories(self, enable):
        for button in self.categories_group_box.category_buttons.values():
            button.setEnabled(enable)

    def show_res_codes(self):
        sender = self.sender()
        category = sender.text()
        res_codes = self.res_code_data[category]
        self.res_codes_group_box.show_res_codes(category, res_codes)
        self.enable_categories(False)

    def get_selected_res_codes(self):
        return self.selected_res_codes_input.text().split(', ')

    def select_res_code(self):
        sender = self.sender()
        res_code = sender.text()

        if self.selected_res_codes_count >= 4:
            QMessageBox.warning(self, "Warning", "Maximum res codes reached.")
            return

        if self.selected_res_codes_input.text():
            current_res_codes = self.selected_res_codes_input.text().split(', ')

        sender.setDisabled(True)
        self.update_selected_res_codes_input(res_code)
        self.selected_res_codes_count += 1

        self.calculate_total_time()

        # Update button colors based on compatibility
        selected_res_code_data = None
        for category, res_codes in self.res_code_data.items():
            if res_code in res_codes:
                selected_res_code_data = res_codes[res_code]
                break
        compatible_res_codes = selected_res_code_data["compatible"]

        for code, button in self.res_codes_group_box.res_code_buttons.items():
            if code == res_code:
                continue
            if compatible_res_codes == "NONE":
                button.setStyleSheet("background-color: red")
                button.setDisabled(True)
            elif code in compatible_res_codes or compatible_res_codes == "Any":
                button.setStyleSheet("background-color: green")
            else:
                button.setStyleSheet("background-color: red")
                button.setDisabled(True)

    def enable_res_code_buttons(self, enable):
        for button in self.res_codes_group_box.res_code_buttons.values():
            button.setEnabled(enable)

    def update_selected_res_codes_input(self, res_code):
        current_text = self.selected_res_codes_input.text()

        if not current_text:
            self.selected_res_codes_input.setText(res_code)
        else:
            self.selected_res_codes_input.setText(f"{current_text}, {res_code}")

    def calculate_total_time(self):

        selected_res_codes = self.selected_res_codes_input.text().split(", ")

        total_fop_time = 0
        total_bop_time = 0
        for res_code in selected_res_codes:
            for category, res_codes in self.res_code_data.items():
                if res_code in res_codes:
                    total_fop_time += int(res_codes[res_code]["fop"])
                    total_bop_time += int(res_codes[res_code]["bop"])
                    break

        self.fop_time_label.setText(f"FOP Time: {total_fop_time}")
        self.bop_time_label.setText(f"BOP Time: {total_bop_time}")
        self.total_time_label.setText(f"Total Time: {total_fop_time + total_bop_time}")
# ---- End for RescanOrdersDialog.py ---- #