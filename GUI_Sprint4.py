from PySide6.QtWidgets import QWidget, QPushButton, QListWidget, QApplication, QListWidgetItem
from typing import List, Dict


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.data = 0
        self.list_control = None
        self.setup_window()

    def setup_window(self):
        self.setWindowTitle(" Project1 - Sprint 4 - Ryan OConnor")
        # display_list = QListWidget(self)
        # self.list_control = display_list
        # self.put_data_in_list(self.data)
        # display_list.resize(400,350)
        self.setGeometry(100, 100, 400, 500)
        quit_button = QPushButton("Exit", self)
        quit_button.clicked.connect(QApplication.instance().quit)
        quit_button.resize(quit_button.sizeHint())
        quit_button.move(150, 400)
        self.show()
