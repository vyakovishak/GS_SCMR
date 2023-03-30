from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path
from MainWindow import MainWin
from DialogsWindow import WelcomeScreen

def main():
    app = QApplication(sys.argv)

    config_path = Path("config.ini")
    if not config_path.exists():
        welcome_dialog = WelcomeScreen()
        welcome_dialog.exec_()
        config_path.touch()

    main_window = MainWin()
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()