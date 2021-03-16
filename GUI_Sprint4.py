import openpyxl
from PySide6.QtWidgets import QPushButton, QApplication, QMessageBox, QFileDialog
from PySide6.QtGui import QCloseEvent, QScreen, QCursor, Qt
from PySide6.QtWidgets import QMainWindow, QLabel
import sqlite3
from typing import Tuple
from os import path
import secrets
import requests
import math
import os


def process_data(url: str, meta_from_main, cursor: sqlite3.Cursor):
    #  meta_from_main is a list with the following index descriptions
    #                 0 index = total results
    #                 1 index = current page
    #                 2 index = results per page
    #                 3 index = total pages

    page_counter = 0
    final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"
    # final_url = f"{url}&api_key={secrets.api_key}&page=0"  # for testing purposes

    #for page_counter in range(meta_from_main[3]):
    for page_counter in range(1):
        response = requests.get(final_url)

        if response.status_code != 200:
            print(response.text)
            exit(-1)

        json_data = response.json()

        # All the results on each page in a singular list returned
        each_page_data = json_data["results"]

        for school_data in each_page_data:
            school_tpl = (school_data["id"], school_data["school.name"], school_data["school.city"],
                          school_data["2018.student.size"], school_data["2017.student.size"],
                          school_data["2017.earnings.3_yrs_after_completion.overall_count_over_poverty_line"],
                          school_data["2016.repayment.3_yr_repayment.overall"], school_data["school.state"],
                          school_data["2016.repayment.repayment_cohort.3_year_declining_balance"])

            print(f"Page {page_counter} of {meta_from_main[3]} ->", school_tpl)

            insert_db(cursor, school_tpl)

        page_counter += 1
        final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"


def get_metadata(url: str):
    final_url = f"{url}&api_key={secrets.api_key}&page=0"
    response = requests.get(final_url)

    if response.status_code != 200:
        print(response.text)
        exit(-1)

    json_data = response.json()

    print(json_data)

    total_results = json_data["metadata"]["total"]
    current_page = json_data["metadata"]["page"]
    results_per_page = json_data["metadata"]["per_page"]
    total_pages = total_results / results_per_page

    return [total_results, current_page, results_per_page, math.ceil(total_pages)]


def setup_school_db(cursor: sqlite3.Cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS school_export(
    school_id INTEGER PRIMARY KEY,
    school_name TEXT,
    school_city TEXT,
    student_size_2018 INTEGER,
    student_size_2017 INTEGER,
    earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017 INTEGER,
    repayment_3_yr_repayment_overall_2016 INTEGER,
    school_state TEXT,
    repayment_repayment_cohort_3_year_declining_balance_2016 INTEGER
    );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS jobdata_by_state(
        unique_id INTEGER PRIMARY KEY,
        area_title TEXT,
        occ_code INTEGER,
        occ_title TEXT,
        tot_emp INTEGER,
        h_pct25 INTEGER,
        a_pct25 INTEGER
        );''')


def insert_db(cursor, school_tuple):
    sql = '''INSERT INTO school_export (school_id, school_name, school_city, student_size_2018, student_size_2017,
                earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017, repayment_3_yr_repayment_overall_2016,
                school_state, repayment_repayment_cohort_3_year_declining_balance_2016)
                VALUES (?,?,?,?,?,?,?,?,?)'''
    cursor.execute(sql, school_tuple)


def insert_xls_db(cursor: sqlite3.Cursor, xls_tuple):
    sql = '''INSERT INTO jobdata_by_state (area_title, occ_code, occ_title, tot_emp, h_pct25, a_pct25, unique_id)
                VALUES (?,?,?,?,?,?,?)'''
    cursor.execute(sql, xls_tuple)


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    print("file exists:" + str(path.exists(filename)))

    db_connection = sqlite3.connect(filename)
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()


def read_excel_data(xls_filename, cursor: sqlite3.Cursor):

    try:
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

    except Exception as error:
        print(error)


class GUIWindow(QMainWindow):
    def __init__(self, db_filename_from_main):
        super().__init__()
        self.db_name = db_filename_from_main
        self.url_name = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&" \
                        "fields=id,school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_" \
                        "completion.overall_count_over_poverty_line,2016.repayment.3_yr_repayment.overall,school.state," \
                        "2016.repayment.repayment_cohort.3_year_declining_balance"
        self.data = 0
        self.list_control = None
        self.progress_lbl = QLabel(self)
        self.setup_window()

    def setup_window(self):
        self.setWindowTitle("Project1 - Sprint 4 - Ryan OConnor")
        self.setGeometry(100, 100, 200, 250)
        # display_list = QListWidget(self)
        # self.list_control = display_list
        # self.put_data_in_list(self.data)
        # display_list.resize(400,350)
        self.statusBar().showMessage("Ryan OConnor - Sprint 4 - Project 1 - "' "GUI PROJECT"')
        self.gui_components()
        self.center()
        self.show()

    def gui_components(self):
        update_data = QPushButton("Update Data", self)
        update_data.clicked.connect(self.update_data)
        update_data.resize(update_data.sizeHint())
        update_data.move(10, 10)
        # implement hover over button to update status bar with file chosen

        render_data_button = QPushButton("Render data analysis", self)
        render_data_button.clicked.connect(self.render_data)
        render_data_button.move(10, 40)
        render_data_button.resize(render_data_button.sizeHint())
        # disable this button until file has been selected

        quit_button = QPushButton("Exit", self)
        quit_button.clicked.connect(QApplication.instance().quit)
        quit_button.clicked.connect(QCloseEvent)
        quit_button.resize(quit_button.sizeHint())
        quit_button.move(10, 70)
        quit_button.setToolTip("Quit program")

    def update_data(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        meta_data = get_metadata(self.url_name)

        if os.path.exists(self.db_name):
            os.remove(self.db_name)

        conn, cursor = open_db(self.db_name)
        setup_school_db(cursor)
        process_data(self.url_name, meta_data, cursor)
        close_db(conn)
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))

        file_name = QFileDialog.getOpenFileName(self, "'Open file")[0]
        print(file_name, " was the file selected.")
        conn, cursor = open_db(self.db_name)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        read_excel_data(file_name, cursor)
        close_db(conn)
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))

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
