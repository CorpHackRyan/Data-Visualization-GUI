import openpyxl
from PySide6.QtWidgets import QPushButton, QApplication, QMessageBox, QFileDialog
from PySide6.QtGui import QCloseEvent, QScreen
from PySide6.QtWidgets import QMainWindow
import main
import sqlite3
from typing import Tuple
from os import path


def insert_xls_db(cursor: sqlite3.Cursor, xls_tuple):
    sql = '''INSERT INTO jobdata_by_state (area_title, occ_code, occ_title, tot_emp, h_pct25, a_pct25, unique_id)
                VALUES (?,?,?,?,?,?,?)'''
    cursor.execute(sql, xls_tuple)


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:

    print("file exists:"+str(path.exists(filename)))

    db_connection = sqlite3.connect(filename)
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def read_excel_data(xls_filename, cursor: sqlite3.Cursor):
    work_book = openpyxl.load_workbook(xls_filename)
    work_sheet = work_book.active

    # BETTER SOLUTION: Get columns with specific titles so no matter what order they are in we can get correct data.
    # Hard coded columns which contain the specific data we are looking for
    # col 1=area_title,  col7=occ_code,  col8=occ_title, col9=o_group, col10=tot_emp,  col19=h_pct25,  col24=a_pct25
    cols = [1, 7, 8, 9, 10, 19, 24]
    unique_id_counter = 1

    for row in work_sheet.iter_rows():

        cells = [cell.value for (idx, cell) in enumerate(row) if (
            idx in cols and cell.value is not None)]

        # skip header row in excel file if row 1
        if row[0].row == 1:
            pass
        else:
            if cells[3] == "major":
                # Using current row number as unique identifier because we wouldn't know why I'm doing this
                cells.append(unique_id_counter)
                unique_id_counter += 1
                del cells[3]
                print(cells)
                insert_xls_db(cursor, cells)


# not use: QWidget, QListWidget, QListWidgetItem , QtGui.QHoverEvent
# from typing import List, Dict

class GUIWindow(QMainWindow):
    def __init__(self, db_filename):
        super().__init__()
        self.db_name = db_filename
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
        select_xlsx_button = QPushButton("Select .xlsx file to update data", self)
        select_xlsx_button.clicked.connect(self.update_data)
        select_xlsx_button.resize(select_xlsx_button.sizeHint())
        select_xlsx_button.move(150, 175)
        # implement hover over button to update status bar with file chosen

        render_data_button = QPushButton("Render data analysis", self)
        render_data_button.clicked.connect(self.render_data)
        render_data_button.move(150, 200)
        render_data_button.resize(render_data_button.sizeHint())
        # disable this button until file has been selected

        quit_button = QPushButton("Exit", self)
        quit_button.clicked.connect(QApplication.instance().quit)
        quit_button.clicked.connect(QCloseEvent)
        quit_button.resize(quit_button.sizeHint())
        quit_button.move(150, 225)
        quit_button.setToolTip("Quit program")

    def update_data(self):
        file_name = QFileDialog.getOpenFileName(self, "'Open file")[0]
        print(file_name, " was the file selected.")
        conn, cursor = open_db(self.db_name)
        read_excel_data(str(file_name), cursor)
        main.close_db(conn)

        return file_name

    def render_data(self):
        message = QMessageBox()
        message.setText("Need to add more code to finish the project. Clicks Details for more info")
        message.setInformativeText("(Informative text block)")
        message.setWindowTitle("More coding required")
        message.setDetailedText("This is where you will render the data in color coded text or on a graphical map")
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()
        # render the color coded text or graphical map data

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
