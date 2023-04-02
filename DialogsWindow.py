# DialogsWindow.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout, QButtonGroup, \
    QMessageBox, QHBoxLayout, QTableWidget, QCalendarWidget, QCheckBox, QComboBox
from PySide6.QtCore import QDate, Qt, QPoint, QDir
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtGui import QFont, QPixmap, QImage, QPainter, QPen
from PySide6.QtWidgets import QDialog, QVBoxLayout, QCalendarWidget, QLabel, QPushButton, QCheckBox, QComboBox, \
    QHBoxLayout, QDialogButtonBox, QTableWidgetItem, QFormLayout, QHeaderView, QGroupBox, QListWidget, QListWidgetItem, \
    QSplitter, QListView, QItemDelegate, QSpinBox, QFileDialog, QScrollArea, QWidget
import qrcode
from PIL.ImageQt import ImageQt
from PIL import Image, ImageDraw, ImageFont
from math import ceil, sqrt
from ServiceOrderDB import ServiceOrderDB
from PySide6.QtCore import Signal
import json
import datetime
from PySide6 import QtWidgets
from utils import load_settings
import re


class AlignCenterDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(AlignCenterDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        return None

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignHCenter | Qt.AlignVCenter
        super(AlignCenterDelegate, self).paint(painter, option, index)



class QRCodeGeneratorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Code Generator")
        self.resize(1080, 720)
        self.qr_codes_per_row = 3

        self.generated_qr_codes = []

        layout = QVBoxLayout()

        self.qr_code_container = QWidget()
        self.qr_code_layout = QGridLayout()
        self.qr_code_container.setLayout(self.qr_code_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.qr_code_container)
        layout.addWidget(scroll_area, stretch=1)

        input_layout = QHBoxLayout()
        input_label = QLabel("QR Code Text:")
        self.input_box = QLineEdit()
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_box)
        layout.addLayout(input_layout)

        size_layout = QHBoxLayout()
        width_label = QLabel("Width:")
        self.width_box = QLineEdit()
        self.width_box.setText("100")
        height_label = QLabel("Height:")
        self.height_box = QLineEdit()
        self.height_box.setText("100")
        font_size = QLabel("Font Size:")
        self.font_size = QComboBox()
        self.font_size.addItems(["2", "4", "6", "8", "10", "12", "14", "16", "18", "20"])
        size_layout.addWidget(width_label)
        size_layout.addWidget(self.width_box)
        size_layout.addWidget(height_label)
        size_layout.addWidget(self.height_box)
        size_layout.addWidget(font_size)
        size_layout.addWidget(self.font_size)
        layout.addLayout(size_layout)

        button_layout = QHBoxLayout()
        create_button = QPushButton("Create")
        create_button.clicked.connect(self.create_qr_code)
        button_layout.addWidget(create_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_qr_code)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_qr_code(self):
        input_text = self.input_box.text()
        texts = input_text.split(',')

        width = int(self.width_box.text())
        height = int(self.height_box.text())
        font_size = int(self.font_size.currentText())

        for text in texts:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((width, height), Image.ANTIALIAS)

            img_w, img_h = img.size
            background = Image.new('RGBA', (img_w, img_h + 20), (255, 255, 255, 255))
            background.paste(img, (0, 0))

            draw = ImageDraw.Draw(background)
            font = ImageFont.truetype("arial.ttf", font_size)
            text_w, text_h = draw.textsize(text, font=font)
            draw.text(((img_w - text_w) // 2, img_h), text, font=font, fill="black")

            self.display_qr_code(background, text)

    def display_qr_code(self, img, label_text):
        pixmap = QPixmap.fromImage(ImageQt(img))

        current_index = len(self.generated_qr_codes)
        row = current_index // self.qr_codes_per_row
        col = current_index % self.qr_codes_per_row

        qr_code_label = QLabel()
        qr_code_label.setPixmap(pixmap)
        self.qr_code_layout.addWidget(qr_code_label, row, col)

        # Save the pixmap without text in generated_qr_codes list
        self.generated_qr_codes.append({'pixmap': pixmap, 'label': label_text})

    def save_qr_code(self):
        save_options = QMessageBox(self)
        save_options.setIcon(QMessageBox.Information)
        save_options.setWindowTitle("Save QR Code")
        save_options.setText("Choose a save option:")
        save_all_as_single_image_button = save_options.addButton("Save All As Single Image", QMessageBox.ActionRole)
        save_as_pdf_button = save_options.addButton("Save As PDF", QMessageBox.ActionRole)
        save_separately_button = save_options.addButton("Save Separately", QMessageBox.ActionRole)
        save_options.addButton("Cancel", QMessageBox.RejectRole)

        save_options.exec_()

        clicked_button = save_options.clickedButton()

        if clicked_button == save_all_as_single_image_button:
            self.save_all_as_single_image()
        elif clicked_button == save_as_pdf_button:
            self.save_as_pdf()
        elif clicked_button == save_separately_button:
            self.save_separately()

    def save_all_as_single_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        selected_filter, _ = QFileDialog.getSaveFileName(self, "Save All QR Codes as Single Image", "",
                                                         "Images (*.png *.xpm *.jpg);;PDF (*.pdf)", options=options)
        if not selected_filter:
            return

        if not selected_filter.lower().endswith(('.png', '.xpm', '.jpg')):
            selected_filter += '.png'

        num_qr_codes = len(self.generated_qr_codes)
        grid_size = ceil(sqrt(num_qr_codes))

        max_width = max([item['pixmap'].width() for item in self.generated_qr_codes])
        max_height = max([item['pixmap'].height() for item in self.generated_qr_codes])

        result = Image.new('RGB', (max_width * grid_size, max_height * grid_size), (255, 255, 255))

        row, col = 0, 0
        for item in self.generated_qr_codes:
            img = Image.fromqpixmap(item['pixmap'])
            result.paste(img, (col * max_width, row * max_height))

            col += 1
            if col >= grid_size:
                col = 0
                row += 1

        result.save(selected_filter)

    def save_as_pdf(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        selected_filter, _ = QFileDialog.getSaveFileName(self, "Save All QR Codes As PDF", "", "PDF (*.pdf);;",
                                                         options=options)
        if not selected_filter:
            return

        if not selected_filter.lower().endswith('.pdf'):
            selected_filter += '.pdf'

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setPaperSize(QPrinter.A4)
        printer.setOutputFileName(selected_filter)

        painter = QPainter()
        painter.begin(printer)

        margin = 30
        spacing = 10

        x, y = margin, margin
        max_width = printer.pageRect().width() - margin * 2
        max_height = printer.pageRect().height() - margin * 2

        for i, item in enumerate(self.generated_qr_codes):
            pixmap = item['pixmap']

            if x + pixmap.width() > max_width:
                x = margin
                y += pixmap.height() + spacing

            if y + pixmap.height() > max_height:
                printer.newPage()
                y = margin

            painter.drawPixmap(x, y, pixmap)
            x += pixmap.width() + spacing

        painter.end()

    def save_separately(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly

        selected_directory = QFileDialog.getExistingDirectory(self, "Save QR Codes Separately", "", options=options)
        if not selected_directory:
            return

        for item in self.generated_qr_codes:
            label = item['label']
            file_name = f"{label}.png"
            full_path = QDir(selected_directory).filePath(file_name)
            item['pixmap'].save(full_path)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About')
        self.setContentsMargins(5, 5, 5, 5)
        self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create a header QLabel with larger font size
        header_label = QLabel("SCMR Management V1")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Create a description QLabel with normal font size
        description_label = QLabel(
            "The SCMR Management V1 application is a user-friendly desktop tool designed to streamline the process of managing service orders."
            "Developed using Python and the PySide6 library, this cross-platform application offers an intuitive interface that enables users to view, search, add, and modify service orders with ease. ")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignCenter)
        copyright_label = QLabel("© 2023 Vasyl Yakovishak. All rights reserved.")
        copyright_label.setStyleSheet("font-size: 10px; font-weight: bold;")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(description_label)
        layout.addWidget(copyright_label)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class WelcomeScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Welcome')

        self.setContentsMargins(5, 5, 5, 5)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        welcome_label = QLabel("Welcome to SCMR Management Beta V1\n")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(welcome_label)
        text = QLabel("This program will help you keep track of service orders.\n\n"
                      "PS. From V 599 with Love !")
        text.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(text)

        tutorial_button = QPushButton("Tutorial")
        tutorial_button.clicked.connect(self.show_tutorial)
        layout.addWidget(tutorial_button)

        skip_button = QPushButton("Skip")
        skip_button.clicked.connect(self.close)
        layout.addWidget(skip_button)

        self.setLayout(layout)

    def show_tutorial(self):
        tutorial_dialog = TutorialDialog(self)
        tutorial_dialog.exec_()


class TutorialDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Tutorial")
        self.resize(720, 480)
        self.setContentsMargins(5, 5, 5, 5)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        splitter = QSplitter()

        video_list = QListView()
        splitter.addWidget(video_list)

        video_player = QVideoWidget()
        splitter.addWidget(video_player)

        layout.addWidget(splitter)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class AdminLoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Login")
        self.setContentsMargins(5, 5, 5, 5)

        layout = QVBoxLayout(self)

        username_layout = QHBoxLayout()
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.verify_credentials)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def verify_credentials(self):
        # Replace 'admin' and 'password' with the correct admin credentials
        if self.username_input.text() == "admin" and self.password_input.text() == "password":
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Invalid username or password.")


class AdminManagement(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Admin Management")
        self.operators = load_settings()
        self.resize(200, 300)
        self.setContentsMargins(5, 5, 5, 5)

        layout = QVBoxLayout(self)

        # Create a QTableWidget for displaying operators and delete buttons
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(self.operators))
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Agent", "Delete"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add operators and delete buttons to the table
        for row, operator in enumerate(self.operators):
            # Add operator name
            operator_item = QTableWidgetItem(operator)
            self.table_widget.setItem(row, 0, operator_item)

            # Add delete button
            delete_button = QPushButton("X")
            delete_button.clicked.connect(lambda *_, r=row: self.delete_operator(r))
            self.table_widget.setCellWidget(row, 1, delete_button)

        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table_widget)

        # Add operator input and button
        add_operator_layout = QHBoxLayout()
        self.operator_input = QLineEdit()
        self.add_operator_button = QPushButton("Add Agent")
        self.add_operator_button.clicked.connect(self.add_operator)
        add_operator_layout.addWidget(self.operator_input)
        add_operator_layout.addWidget(self.add_operator_button)
        layout.addLayout(add_operator_layout)

    def delete_operator(self, row):
        operator_to_delete = self.operators[row]
        if operator_to_delete:
            self.operators.remove(operator_to_delete)
            self.update_settings()
            self.table_widget.removeRow(row)

            # Update delete button connections for the remaining rows
            for r in range(row, self.table_widget.rowCount()):
                delete_button = self.table_widget.cellWidget(r, 1)
                delete_button.clicked.disconnect()
                delete_button.clicked.connect(lambda *_, r=r: self.delete_operator(r))

    def add_operator(self):
        new_operator = self.operator_input.text().strip()
        if new_operator and new_operator not in self.operators:
            self.operators.append(new_operator)
            self.update_settings()

            # Add the new operator to the table
            row = self.table_widget.rowCount()
            self.table_widget.setRowCount(row + 1)
            operator_item = QTableWidgetItem(new_operator)
            self.table_widget.setItem(row, 0, operator_item)

            delete_button = QPushButton("X")
            delete_button.clicked.connect(lambda *_, r=row: self.delete_operator(r))
            self.table_widget.setCellWidget(row, 1, delete_button)

            self.operator_input.clear()

    def update_settings(self):
        with open("Settings.json", "r") as f:
            settings = json.load(f)
        settings["Operators"]["ALL"] = self.operators
        with open("Settings.json", "w") as f:
            json.dump(settings, f, indent=2)


class CustomQDialog(QDialog):
    def __init__(self, should_display: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.should_display = should_display

    def exec_(self):
        if self.should_display:
            return super().exec_()
        return QDialog.Rejected


class RescanOrdersDialog(QDialog):
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
            self.db.delete_service_order(status=1, so=service_order[0], operator=self.operator)
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
                if existing_service_order[0][-2] == "NO":
                    # Display the location dialog
                    location_dialog = LocationDialog()
                    if location_dialog.exec_():
                        location = location_dialog.location_input.text().upper()

                        # Update the location and updated_by in the database
                        self.db.update_location(location, scanned_input, self.operator)
                        self.db.update_updated_by(self.operator, scanned_input, self.operator)
                        self.db.update_scanned_status(1, scanned_input, self.operator)
                        self.db.update_last_updated(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                    scanned_input,
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
        log_filename = "update_log.json"
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
             "CFI"])  # Update the header labels
        table.horizontalHeader().setStretchLastSection(True)

        for i, update in enumerate(sorted(updates, key=lambda x: x['timestamp'])):
            table.setItem(i, 0, QTableWidgetItem(update['timestamp']))
            table.setItem(i, 1, QTableWidgetItem(update['operation']))
            table.setItem(i, 2, QTableWidgetItem(update['operator']))  # Add operator to the table
            for j, key in enumerate(['Location', 'CompletionDate', 'ClosedBy', 'Status', 'Comments', 'CFI'], start=3):
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


class ServiceOrderEditorDialog(QDialog):
    def __init__(self, service_order_data, db: ServiceOrderDB, editing_by):
        super().__init__()
        self.editing_by = editing_by
        self.setContentsMargins(5, 5, 5, 5)

        self.db = db
        self.all_operators = load_settings()
        self.setWindowTitle("Edit Service Order")
        self.service_order_data = service_order_data
        self.resize(1080, 480)
        layout = QVBoxLayout()

        # Create a QFormLayout for the input fields and labels
        input_layout = QFormLayout()

        # Service Order Number (unchangeable)
        so_number_label = QLabel("Service Order:")
        so_number_value = QLabel(str(self.service_order_data[0]))

        input_layout.addRow(so_number_label, so_number_value)

        # Location
        location_label = QLabel("Location:")
        self.location_input = QLineEdit(self.service_order_data[1])
        input_layout.addRow(location_label, self.location_input)

        # Closed By (dropdown)
        closed_by_label = QLabel("Closed By:")
        self.closed_by_input = QComboBox()
        self.closed_by_input.addItems(self.all_operators)
        self.closed_by_input.setCurrentText(self.service_order_data[3])
        input_layout.addRow(closed_by_label, self.closed_by_input)

        # Status (dropdown)
        status_label = QLabel("Status:")
        self.status_input = QComboBox()
        self.status_input.addItem("GREEN")
        self.status_input.addItem("YELLOW")

        self.status_input.setCurrentText(self.service_order_data[4])
        input_layout.addRow(status_label, self.status_input)

        # Comments
        comments_label = QLabel("Comments:")
        self.comments_input = QLineEdit(self.service_order_data[5])
        input_layout.addRow(comments_label, self.comments_input)

        # Wrap input_layout with a QHBoxLayout to center it
        input_centered_layout = QHBoxLayout()
        input_centered_layout.addStretch()
        input_centered_layout.addLayout(input_layout)
        input_centered_layout.addStretch()

        layout.addLayout(input_centered_layout)

        # Submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_changes)
        layout.addWidget(submit_button, alignment=Qt.AlignCenter)

        from TableWidget import ServiceOrderUpdatesLogTable
        log_table = ServiceOrderUpdatesLogTable(service_order_data[0], self)
        layout.addWidget(log_table)
        self.setLayout(layout)

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


class CalendarDialog(QDialog):
    def __init__(self, operators, db):
        super().__init__()
        self.setWindowTitle("Select Date Range")
        self.resize(600, 400)
        self.setContentsMargins(5, 5, 5, 5)

        self.start_date = None
        self.end_date = None
        self.db = db

        layout = QVBoxLayout()

        # Create calendar widget
        self.calendar = QCalendarWidget()

        layout.addWidget(self.calendar)

        # Label to display selected date range
        self.range_label = QLabel()
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.range_label.setFont(font)
        self.range_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.range_label)

        # Checkboxes and dropdowns for filtering service orders
        filters_layout = QHBoxLayout()

        # Filter by closed date checkbox
        self.close_date_checkbox = QCheckBox("By closed date")
        self.close_date_checkbox.setStyleSheet("font-size: 14px;")
        self.close_date_checkbox.setChecked(True)
        filters_layout.addWidget(self.close_date_checkbox)

        # Filter by updated date checkbox
        self.update_date_checkbox = QCheckBox("By updated date")
        self.update_date_checkbox.setStyleSheet("font-size: 14px;")
        filters_layout.addWidget(self.update_date_checkbox)

        self.checkout_checkbox = QCheckBox("Check Out")
        self.checkout_checkbox.setStyleSheet("font-size: 14px;")
        filters_layout.addWidget(self.checkout_checkbox)

        self.deleted_checkbox = QCheckBox("Deleted")
        self.deleted_checkbox.setStyleSheet("font-size: 14px;")
        filters_layout.addWidget(self.deleted_checkbox)

        self.closed_by_label = QLabel("Closed By")
        self.closed_by_label.setStyleSheet("font-size: 14px;")
        filters_layout.addWidget(self.closed_by_label)

        self.closed_by = QComboBox()
        self.closed_by.addItem("")
        self.closed_by.addItems(operators)
        filters_layout.addWidget(self.closed_by)

        self.checkout_by_label = QLabel("Check Out By")
        filters_layout.addWidget(self.checkout_by_label)

        self.checkout_by = QComboBox()
        self.checkout_by.addItem("")
        self.checkout_by.addItems(operators)
        filters_layout.addWidget(self.checkout_by)

        self.closed_by_label = QLabel("Status")
        filters_layout.addWidget(self.closed_by_label)
        self.status = QComboBox()
        self.status.addItems(['', 'GREEN', "YELLOW"])
        filters_layout.addWidget(self.status)

        layout.addLayout(filters_layout)

        # Apply and cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_button_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        self.calendar.clicked.connect(self.update_date_range)

    def update_date_range(self, clicked_date):
        if not self.start_date:
            self.start_date = clicked_date
            self.end_date = None
        elif not self.end_date:
            if clicked_date < self.start_date:
                self.start_date, self.end_date = clicked_date, self.start_date
            else:
                self.end_date = clicked_date
        else:
            self.start_date = clicked_date
            self.end_date = None

        # Update label with selected date range
        if self.start_date and not self.end_date:
            self.range_label.setText(self.start_date.toString("yyyy-MM-dd"))
        elif self.start_date and self.end_date:
            self.range_label.setText(
                f"{self.start_date.toString('yyyy-MM-dd')} - {self.end_date.toString('yyyy-MM-dd-dd')}")
        self.calendar_clicked()

    def calendar_clicked(self):
        if not self.start_date:
            self.start_date = self.calendar.selectedDate()
        elif self.end_date is not None:
            self.end_date = self.calendar.selectedDate()
            self.range_label.setText(f"Selected range: {self.start_date.toString()} - {self.end_date.toString()}")
        else:
            self.start_date = self.calendar.selectedDate()
            self.range_label.setText(f"Date {self.start_date.toString()} selected")

    def apply_button_clicked(self):
        if self.start_date is None and self.end_date is None:
            QMessageBox.warning(self, "Warning", "Please select a date.")
            return
        # Get filter values
        closedDate = self.close_date_checkbox.isChecked()
        updateDate = self.update_date_checkbox.isChecked()
        checkout = self.checkout_checkbox.isChecked()
        closed_by = self.closed_by.currentText()
        checkout_by = self.checkout_by.currentText()
        status = self.status.currentText()
        deleted = self.deleted_checkbox.isChecked()
        start_date, end_date = self.start_date.toString(
            'yyyy-MM-dd'), self.end_date if self.end_date is None else self.end_date.toString('yyyy-MM-dd')

        # Create a query with filters
        query = "SELECT * FROM ServiceOrders WHERE 1 "

        if updateDate:
            if end_date is None:
                query += f" AND DATE(LastUpdated)='{start_date}'"
            else:
                query += f" AND DATE(LastUpdated) BETWEEN '{start_date}' AND '{end_date}'"

        if closedDate:
            if end_date is None:
                query += f" AND DATE(CompletionDate)='{start_date}'"
            else:
                query += f" AND DATE(CompletionDate) BETWEEN '{start_date}' AND '{end_date}'"

        if checkout:
            if end_date is None:
                query += f" AND DATE(CheckOutDate)='{start_date}'"
            else:
                query += f" AND DATE(CheckOutDate) BETWEEN '{start_date}' AND '{end_date}'"

        if checkout:
            query += f" AND CheckedOut=1"

        if closed_by:
            query += f" AND ClosedBy='{closed_by}'"

        if checkout_by:
            query += f" AND CheckOutBy='{checkout_by}'"

        if status:
            query += f" AND Status='{status}'"

        if deleted:
            query += f" AND CFI=1"

        # Fetch data from the database
        results = self.db.execute(query, fetchall=True)

        # Create a QDialog to display the results
        result_dialog = QDialog(self)
        result_dialog.setWindowTitle("Filtered Results")
        result_dialog.resize(1800, 700)

        layout = QVBoxLayout(result_dialog)

        label = QLabel("Filtered Service Orders:")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)
        from TableWidget import CalendarTable
        self.table = CalendarTable(results)
        layout.addWidget(self.table)

        # Add a close button to the dialog
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(result_dialog.reject)
        layout.addWidget(button_box)

        # Show the result dialog
        result_dialog.exec_()

    def get_selected_date_range(self):
        return self.start_date, self.end_date


class LocationWarningDialog(QDialog):
    def __init__(self, location, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Location already exists")
        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel(f"The location '{location}' already exists.\n"
                                     "Do you want to add the unit to the current location or choose a different location?"))

        self.button_box = QDialogButtonBox(QDialogButtonBox.No | QDialogButtonBox.Yes)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_result(self):
        return self.result()


# Define a QDialog for entering a location
class LocationDialog(QDialog):
    location_warning = Signal(str)

    def __init__(self, db):
        super().__init__()
        self.setContentsMargins(5, 5, 5, 5)
        self.db = db
        self.setWindowTitle("Enter Location")
        layout = QVBoxLayout()

        # Create a QHBoxLayout for the label and input box
        hbox = QHBoxLayout()

        self.label = QLabel("Location:")
        self.location_input = QLineEdit()

        # Add the label and input box to the QHBoxLayout
        hbox.addWidget(self.label)
        hbox.addWidget(self.location_input)

        # Add the QHBoxLayout to the main QVBoxLayout
        layout.addLayout(hbox)
        self.location_input.returnPressed.connect(self.accept)
        self.setLayout(layout)

    def check_location_exists(self, location):
        return self.db.check_location_exists(location)


# Define a QDialog for selecting who closed the service order
class CloseByDialog(QDialog):
    def __init__(self, close_by_list):
        super().__init__()
        self.resize(200, 150)
        self.setContentsMargins(5, 5, 5, 5)

        self.setWindowTitle("Select Close By")
        layout = QGridLayout()
        self.button_group = QButtonGroup()
        for index, close_by in enumerate(close_by_list):
            button = QPushButton(close_by)
            self.button_group.addButton(button, index)
            layout.addWidget(button, index // 2, index % 2)
        self.setLayout(layout)
        self.button_group.buttonClicked.connect(self.accept)


# Define a QDialog for selecting an operator
class OperatorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.operators = load_settings()
        self.setContentsMargins(5, 5, 5, 5)

        self.setWindowTitle("Select Agent")
        layout = QGridLayout()
        self.button_group = QButtonGroup()
        self.buttons = []
        for index, operator in enumerate(self.operators):
            button = QPushButton(operator)
            self.buttons.append(button)

            self.button_group.addButton(button, index)
            layout.addWidget(button, index // 2, index % 2)
        self.setLayout(layout)
        self.button_group.buttonClicked.connect(self.on_button_clicked)
        self.selected_operator = None

    def on_button_clicked(self, button):
        button_id = self.button_group.id(button)
        self.selected_operator = self.operators[button_id]

        confirmation_message = QMessageBox(self)
        confirmation_message.setIcon(QMessageBox.Question)
        confirmation_message.setWindowTitle("Confirm Agent")
        confirmation_message.setText(f"Is '{self.selected_operator}' the correct Agent?")
        yes_button = confirmation_message.addButton(QMessageBox.Yes)
        no_button = confirmation_message.addButton(QMessageBox.No)
        confirmation_message.exec_()

        if confirmation_message.clickedButton() == yes_button:
            self.accept()
        else:
            self.selected_operator = None

    def get_operator(self):
        return self.selected_operator


# Define a QDialog for selecting a service order status
class StatusDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(100, 70)
        self.setWindowTitle("Status")
        self.setContentsMargins(5, 5, 5, 5)

        layout = QHBoxLayout()

        self.green_button = QPushButton("GREEN")
        self.yellow_button = QPushButton("YELLOW")

        layout.addWidget(self.green_button)
        layout.addWidget(self.yellow_button)

        self.setLayout(layout)

        self.status = None

        self.green_button.clicked.connect(self.set_status_green)
        self.yellow_button.clicked.connect(self.set_status_yellow)

    def set_status_green(self):
        self.status = "GREEN"
        self.accept()

    def set_status_yellow(self):
        self.status = "YELLOW"
        self.accept()


# Define a QDialog for entering comments
class CommentsDialog(QDialog):
    def __init__(self, status):
        super().__init__()
        self.resize(400, 200)
        self.setContentsMargins(5, 5, 5, 5)

        self.setWindowTitle("Enter Comments")
        layout = QVBoxLayout()
        self.label = QLabel("Comments (minimum 10 characters):")
        self.comments_input = QLineEdit()
        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.label)
        layout.addWidget(self.comments_input)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)
        if status == "YELLOW":
            self.submit_button.clicked.connect(self.validate_comments)
        else:
            self.submit_button.clicked.connect(self.accept)

    def validate_comments(self):
        if len(self.comments_input.text()) >= 10:
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Comments must be at least 10 characters long.")
