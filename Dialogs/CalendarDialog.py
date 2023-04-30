# ---- Start for CalendarDialog.py ---- #
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QDialogButtonBox, QLabel, QVBoxLayout, QDialog, QMessageBox, QComboBox, QCheckBox, \
    QHBoxLayout, QCalendarWidget

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
            query += f" AND CheckedOut='YES'"

        if closed_by:
            query += f" AND ClosedBy='{closed_by}'"

        if checkout_by:
            query += f" AND CheckOutBy='{checkout_by}'"

        if status:
            query += f" AND Status='{status}'"

        if deleted:
            query += f" AND CFI='YES'"

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
        from Widgets.TableWidget import CalendarTable
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

# ---- End for CalendarDialog.py ---- #