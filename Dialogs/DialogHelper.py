# ---- Start for DialogHelper.py ---- #

from PySide6.QtGui import Qt
from PySide6.QtWidgets import QDialog, QApplication, QItemDelegate, QVBoxLayout, QLabel, QDialogButtonBox
class CenteredDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.center_on_screen()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        self_geometry = self.frameGeometry()
        center_point = screen.center()
        self_geometry.moveCenter(center_point)
        self.move(self_geometry.topLeft())


class AlignCenterDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(AlignCenterDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        return None

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignHCenter | Qt.AlignVCenter
        super(AlignCenterDelegate, self).paint(painter, option, index)


class CustomQDialog(QDialog):
    def __init__(self, should_display: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.should_display = should_display

    def exec_(self):
        if self.should_display:
            return super().exec_()
        return QDialog.Rejected


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
        """

        :return:
        """
        return self.result()

# ---- End for DialogHelper.py ---- #