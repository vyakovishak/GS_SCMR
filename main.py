from PySide6.QtWidgets import QApplication
import sys

from MainWIndow import MainWin


app = QApplication(sys.argv)

window = MainWin()
window.show()
app.exec()