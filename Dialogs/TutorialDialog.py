# ---- Start for TutorialDialog.py ---- #
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QDialog, QVBoxLayout, QSplitter, QListView, QPushButton


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
# ---- End for TutorialDialog.py ---- #