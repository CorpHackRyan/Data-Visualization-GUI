# from PySide6.QtWidgets import QWidget, QPushButton, QListWidget, QApplication, QListWidgetItem
# from typing import List, Dict
#
#
# class GUI_Window(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.data = 0
#         self.list_control = None
#         self.setup_window()
#
#     def setup_window(self):
#         self.setWindowTitle(" Project1 - Sprint 4 - Ryan OConnor")
#         # display_list = QListWidget(self)
#         # self.list_control = display_list
#         # self.put_data_in_list(self.data)
#         # display_list.resize(400,350)
#         self.setGeometry(100, 100, 400, 500)
#         quit_button = QPushButton("Exit", self)
#         quit_button.clicked.connect(QApplication.instance().quit)
#         quit_button.resize(quit_button.sizeHint())
#         quit_button.move(150, 400)
#         self.show()
import self as self
from PySide2.QtWidgets import QMainWindow, QLabel, QGridLayout, QDesktopWidget, QWidget


class GUIWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.data = "data to show"
        self.setup_window()

    def setup_window(self):
        self.setWindowTitle("roconnor - Project 1 - Sprint 4 - Tues/Thurs")

        qtRectangle = self.frameGeometry()
        print(qtRectangle)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

       # self.setGeometry(100, 100, 280, 580)
        #self.move(60, 15)
        #display_msg = QLabel('<h1>Hello World!</h1>', parent=self)
        display_msg = QLabel("<h1>{self.data}<h1>")
        display_msg.move(60, 15)
        self.show()
