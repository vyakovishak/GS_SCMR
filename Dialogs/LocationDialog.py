# ---- Start for DialogHelper.py ---- #
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import Signal

class LocationDialog(QDialog):
    location_warning = Signal(str)

    def __init__(self, db, location=None):
        super().__init__()
        self.setContentsMargins(5, 5, 5, 5)
        self.db = db
        self.setWindowTitle("Enter Location")
        layout = QVBoxLayout()

        # Create a QHBoxLayout for the current location label

        # Create a QHBoxLayout for the new location label and input box
        hbox_new = QHBoxLayout()
        self.label = QLabel("New Location:")
        self.location_input = QLineEdit()
        hbox_new.addWidget(self.label)
        hbox_new.addWidget(self.location_input)
        if location is not None:
            hbox_current = QHBoxLayout()
            self.current_location = QLabel(f"Current Location: {location}")
            hbox_current.addWidget(self.current_location)
            # Add the QHBoxLayouts to the main QVBoxLayout
            layout.addLayout(hbox_current)

        layout.addLayout(hbox_new)

        self.location_input.returnPressed.connect(self.accept)
        self.setLayout(layout)

    def check_location_exists(self, location):
        return self.db.check_location_exists(location)


# ---- End for DialogHelper.py ---- #