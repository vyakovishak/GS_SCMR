from PySide6.QtWidgets import QWidget, QMainWindow, QTableWidgetItem


class LayoutSettings():
    def __init__(self):
        super().__init__()

    @staticmethod
    def main_window_layout(window):
        window.setFixedSize(1080, 720)
        window.setRowCount(3)
        window.setColumnCount(3)
        window.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

        # Add some data to the table
        for row in range(3):
            for col in range(3):
                item = QTableWidgetItem(f"Row {row + 1}, Col {col + 1}")
                window.setItem(row, col, item)


