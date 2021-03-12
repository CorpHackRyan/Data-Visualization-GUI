from PySide6.QtWidgets import QWidget, QPushButton, QListWidget, QApplication, QListWidgetItem, QMessageBox, QFileDialog
from PySide6.QtGui import QCloseEvent, QScreen, QHoverEvent
from PySide6.QtWidgets import QMainWindow



from typing import List, Dict


class GUIWindow(QMainWindow): # the class GUIWindow inherits all the properties of QWidget and thats the constructor type
    def __init__(self):
        super().__init__()
        self.data = 0
        self.list_control = None
        self.setup_window()

    def setup_window(self):
        self.setWindowTitle("Project1 - Sprint 4 - Ryan OConnor")
        self.setGeometry(100, 100, 400, 500)
        # display_list = QListWidget(self)
        # self.list_control = display_list
        # self.put_data_in_list(self.data)
        # display_list.resize(400,350)
        self.statusBar().showMessage("Ryan OConnor - Sprint 4 - Project 1 - "' "GUI PROJECT"')
        self.gui_components()
        self.center()
        self.show()

    def gui_components(self):
        quit_button = QPushButton("Exit", self)
        quit_button.clicked.connect(QApplication.instance().quit)
        quit_button.clicked.connect(QCloseEvent)
        quit_button.resize(quit_button.sizeHint())
        quit_button.move(150, 400)
        quit_button.setToolTip("Quit program")
        # implement hover over button to update status bar

        update_data_button = QPushButton("Update Data", self)
        update_data_button.clicked.connect(self.update_data)

    def update_data(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')
        print(file_name)

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self,
            'Message',
            'Are you sure you want to quit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        screen_center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        self_geometry = self.frameGeometry()
        self_geometry.moveCenter(screen_center)
        self.move(self_geometry.topLeft())

