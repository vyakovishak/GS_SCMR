

# ---- Start for QRCodeGeneratorDialog.py ---- #
import qrcode
from PIL import Image
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import ImageFont
from PySide6.QtCore import QDir, QByteArray
from PySide6.QtGui import QPainter, QPixmap, QImage
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import QFileDialog, QMessageBox, QLabel, QHBoxLayout, QPushButton, QComboBox, QLineEdit, \
    QScrollArea, QGridLayout, QWidget, QVBoxLayout, QDialog
from numpy import ceil, sqrt

class QRCodeGeneratorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Code Generator")

        self.resize(1080, 720)
        self.qr_codes_per_row = 5

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
        self.font_size.addItems(["8", "10", "12", "14", "16", "18", "20"])
        size_layout.addWidget(width_label)
        size_layout.addWidget(self.width_box)
        size_layout.addWidget(height_label)
        size_layout.addWidget(self.height_box)
        size_layout.addWidget(font_size)
        size_layout.addWidget(self.font_size)
        layout.addLayout(size_layout)

        text_position_label = QLabel("Text Position:")
        self.text_position = QComboBox()
        self.text_position.addItems(["Top", "Bottom", "Left", "Right"])
        size_layout.addWidget(text_position_label)
        size_layout.addWidget(self.text_position)

        self.size_warning = QLabel("Size is too small. Minimum is 35 for both width and height.")
        self.size_warning.setStyleSheet("color: red;")
        self.size_warning.hide()
        layout.addWidget(self.size_warning)

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

        if width < 35 or height < 35:
            self.size_warning.show()
            return
        else:
            self.size_warning.hide()

        font_size = int(self.font_size.currentText())
        text_position = self.text_position.currentText()

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
            text_w, text_h = ImageDraw.Draw(img).textsize(text, font=ImageFont.truetype("arial.ttf", font_size))

            if text_position == "Top":
                background = Image.new('RGBA', (img_w, img_h + 20), (255, 255, 255, 255))
                background.paste(img, (0, 20))
                draw = ImageDraw.Draw(background)
                draw.text(((img_w - text_w) // 2, 0), text, font=ImageFont.truetype("arial.ttf", font_size),
                          fill="black")

            elif text_position == "Bottom":
                background = Image.new('RGBA', (img_w, img_h + 20), (255, 255, 255, 255))
                background.paste(img, (0, 0))
                draw = ImageDraw.Draw(background)
                draw.text(((img_w - text_w) // 2, img_h), text, font=ImageFont.truetype("arial.ttf", font_size),
                          fill="black")

            elif text_position == "Left":
                background = Image.new('RGBA', (img_w + text_w + 10, img_h), (255, 255, 255, 255))
                background.paste(img, (text_w + 10, 0))
                draw = ImageDraw.Draw(background)

                draw.text((10, (img_h - text_h) // 2), text, font=ImageFont.truetype("arial.ttf", font_size),
                          fill="black")
            else:
                background = Image.new('RGBA', (img_w + text_w + 10, img_h), (255, 255, 255, 255))
                background.paste(img, (0, 0))
                draw = ImageDraw.Draw(background)
                draw.text((img_w, (img_h - text_h) // 2), text, font=ImageFont.truetype("arial.ttf", font_size),
                          fill="black")

            qimg = QImage(QByteArray(background.tobytes()), background.width, background.height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimg)
            self.display_qr_code(pixmap, text)

    def display_qr_code(self, img, label_text):
        pixmap = img

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
        printer.setPageSize(QPrinter)
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

# ---- End for QRCodeGeneratorDialog.py ---- #