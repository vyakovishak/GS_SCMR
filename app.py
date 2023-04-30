#app.py
from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path

from Dialogs.WelcomeScreen import WelcomeScreen
from Dialogs.MainWindowDialog import MainWin



def main():
    app = QApplication(sys.argv)
    config_path = Path("Dependents/config.ini")
    if not config_path.exists():
        welcome_dialog = WelcomeScreen()
        welcome_dialog.exec_()
        config_path.touch()

    main_window = MainWin()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
#End of app.py