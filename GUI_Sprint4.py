import openpyxl
from PySide6.QtWidgets import QPushButton, QApplication, QMessageBox, QFileDialog, QWidget, QListWidget, QListWidgetItem
from PySide6.QtGui import QCloseEvent, QScreen, QCursor, Qt, QFont
from PySide6.QtWidgets import QMainWindow, QLabel, QCheckBox
import sqlite3
from typing import Tuple
from os import path
import secrets
import requests
import math
import os
import DisplayMap
from datetime import datetime


def process_data(url: str, meta_from_main, cursor: sqlite3.Cursor):
    #  meta_from_main is a list with the following index descriptions
    #                 0 index = total results
    #                 1 index = current page
    #                 2 index = results per page
    #                 3 index = total pages

    page_counter = 0
    final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"

    # for page_counter in range(meta_from_main[3]):
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
        print(str(error))
        error_msg(str(error))


def error_msg(error_message):
    message = QMessageBox()
    message.setText("There was a problem processing your file. Please click more details for more information.")
    message.setInformativeText(error_message)
    message.setWindowTitle("Error processing file")
    message.setDetailedText(error_message)
    message.setStandardButtons(QMessageBox.Ok)
    QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
    message.exec_()


def abbreviate_state(state_long_name):
    states = {"Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
              "Connecticut": "CT",
              "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
              "Idaho": "ID",
              "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
              "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
              "Mississippi": "MS",
              "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
              "New Jersey": "NJ",
              "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
              "Oklahoma": "OK",
              "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
              "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
              "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Guam": "GU", "Puerto Rico": "PR",
              "Virgin Islands": "VI", "Alabama": "AL"}

    state_abbreviated = states[state_long_name]

    return state_abbreviated


class RenderData(QWidget):
    def __init__(self, db_name_from_visualize):
        super().__init__()
        self.db_name_from_visual_btn = db_name_from_visualize
        self.type_of_display = QLabel("Please choose how you'd like to display the data", self)
        self.type_of_display.move(20, 20)
        self.type_of_display.setStyleSheet("border: 1px solid black;")
        self.type_of_display.setFont(QFont("Calibre", 12))

        self.which_data = QLabel("Please select which data you'd like to display", self)
        self.which_data.move(430, 20)
        self.which_data.setStyleSheet("border: 1px solid black")
        self.which_data.setFont(QFont("Calibre", 12))

        # LIST BOXES
        display_list = QListWidget(self)
        self.list_control = display_list
        display_list.resize(770, 440)
        display_list.move(10, 200)

        # CHECKBOXES
        self.color_coded_checkbox = QCheckBox("Color coded text in a list", self)
        self.color_coded_checkbox.move(100, 60)
        self.render_map_checkbox = QCheckBox("Render a Map", self)
        self.render_map_checkbox.move(100, 90)

        self.analysis_type1_checkbox = QCheckBox(
            "Compare the number of college graduates in a state \n(for the most recent "
            "year) with number of jobs in that \nstate that likely expect a college "
            "education.", self)
        self.analysis_type1_checkbox.setGeometry(430, 20, 300, 100)
        self.analysis_type2_checkbox = QCheckBox("Compare the 3 year graduate cohort declining balance \npercentage to "
                                                 "the 25% salary in the state.", self)
        self.analysis_type2_checkbox.setGeometry(430, 70, 400, 100)

        # BUTTONS
        self.render_data_button = QPushButton("VISUALIZE", self)
        self.render_data_button.setGeometry(10, 150, 770, 40)
        self.render_data_button.clicked.connect(self.display_visualization)

        self.sort_ascending_button = QPushButton("Sort Ascending", self)
        self.sort_ascending_button.setGeometry(10, 650, 120, 30)
        self.sort_ascending_button.clicked.connect(self.sort_ascending)

        self.sort_descending_button = QPushButton("Sort Descending", self)
        self.sort_descending_button.setGeometry(130, 650, 120, 30)
        self.sort_descending_button.clicked.connect(self.sort_descending)

        self.close_visual_window_button = QPushButton("CLOSE", self)
        self.close_visual_window_button.setGeometry(660, 650, 120, 30)
        self.close_visual_window_button.clicked.connect(lambda: self.close())

        self.setWindowTitle("Data Visualization for Project 1 - Sprint 4 - Ryan O'Connor - COMP490 - T/R")
        self.setGeometry(100, 100, 800, 700)
        self.setFixedSize(800, 700)
        self.center()

    def display_visualization(self):
        conn, cursor = open_db(self.db_name_from_visual_btn)

        cursor.execute('SELECT school_state, student_size_2018 FROM school_export')
        table = cursor.fetchall()
        # final_data_list = []

        self.list_control.clear()

        # ################################  DATA ANALYSIS - PART 1A  ##################################
        num_grads_in_state = {"AK": 0, "AL": 0, "AR": 0, "AS": 0, "AZ": 0, "CA": 0,
                              "CO": 0, "CT": 0, "DC": 0, "DE": 0, "FL": 0, "FM": 0, "GA": 0,
                              "GU": 0, "HI": 0, "IA": 0, "ID": 0, "IL": 0, "IN": 0, "KS": 0,
                              "KY": 0, "LA": 0, "MA": 0, "MD": 0, "ME": 0, "MH": 0, "MI": 0,
                              "MN": 0, "MO": 0, "MP": 0, "MS": 0, "MT": 0, "NC": 0, "ND": 0,
                              "NE": 0, "NH": 0, "NJ": 0, "NM": 0, "NV": 0, "NY": 0, "OH": 0,
                              "OK": 0, "OR": 0, "PA": 0, "PR": 0, "PW": 0, "RI": 0, "SC": 0,
                              "SD": 0, "TN": 0, "TX": 0, "UT": 0, "VA": 0, "VI": 0, "VT": 0,
                              "WA": 0, "WI": 0, "WV": 0, "WY": 0}

        for idx, row in enumerate(table):
            print(idx, row)
            record = f"{row[0]}, {row[1]}"

            print("Record directly from the row in the table: state/student size 2018-->", record)
            # final_data_list.append(record)

            if row[1] is None:
                continue

            else:
                # row [0] is a STRING state name ... row [1] includes an INTEGER - 2018 student size
                # counter = counter + row[1]
                state_abbr_from_table = row[0]
                student_size_2018 = row[1]

                state_total = num_grads_in_state[state_abbr_from_table]

                num_grads_in_state[state_abbr_from_table] = state_total + student_size_2018
                print(num_grads_in_state[state_abbr_from_table], "totals from each states:")

            # print("should be same as counter", num_grads_in_state["CA"], "\n")

        # I'm dividing by 4 years here, to simplify the size of a senior graduating class
        for student_total_2018 in num_grads_in_state:
            num_grads_in_state[student_total_2018] = num_grads_in_state[student_total_2018] / 4

        # ################################  DATA ANALYSIS - PART 1B   #########################

        num_jobs_in_state = {"AK": 0, "AL": 0, "AR": 0, "AS": 0, "AZ": 0, "CA": 0,
                             "CO": 0, "CT": 0, "DC": 0, "DE": 0, "FL": 0, "FM": 0, "GA": 0,
                             "GU": 0, "HI": 0, "IA": 0, "ID": 0, "IL": 0, "IN": 0, "KS": 0,
                             "KY": 0, "LA": 0, "MA": 0, "MD": 0, "ME": 0, "MH": 0, "MI": 0,
                             "MN": 0, "MO": 0, "MP": 0, "MS": 0, "MT": 0, "NC": 0, "ND": 0,
                             "NE": 0, "NH": 0, "NJ": 0, "NM": 0, "NV": 0, "NY": 0, "OH": 0,
                             "OK": 0, "OR": 0, "PA": 0, "PR": 0, "PW": 0, "RI": 0, "SC": 0,
                             "SD": 0, "TN": 0, "TX": 0, "UT": 0, "VA": 0, "VI": 0, "VT": 0,
                             "WA": 0, "WI": 0, "WV": 0, "WY": 0}

        cursor.execute('SELECT area_title, occ_code, tot_emp FROM jobdata_by_state')
        table = cursor.fetchall()
        total_jobs_by_state = []

        for idx, row in enumerate(table):
            total_jobs_by_state.append(record)

            check_occ_code = row[1]
            check_occ_code = int(check_occ_code[:2])

            if 30 <= check_occ_code <= 49:
                # print(row[:2], "did not make the cut!", idx, "<-- index")
                continue

            else:
                state_from_school_export = str(row[0])
                print(state_from_school_export, "made the cut", "occ code ->", check_occ_code,
                      "state abbreviated: ", abbreviate_state(state_from_school_export),
                      "total_emp col: ", row[2])

                abbr_state = abbreviate_state(state_from_school_export)
                tot_emp_jobs_in_state = int(row[2])
                tot_emp = num_jobs_in_state[abbr_state]
                num_jobs_in_state[abbr_state] = tot_emp + tot_emp_jobs_in_state

        print("should be same as counter", num_jobs_in_state["WY"], "\n")

        print(num_jobs_in_state)
        print(num_grads_in_state)

        compare_total_jobs_to_grads = {k: (num_jobs_in_state[k] / num_grads_in_state[k]) for k in num_jobs_in_state}

        print("Final numbers", compare_total_jobs_to_grads, )

        display_data = open("display_map_data.csv", "w+")
        display_data.writelines("state,data\n")

        for key in compare_total_jobs_to_grads:
            # print(key, '->', compare_total_jobs_to_grads[key])
            # display_text = f"{key}\t {compare_total_jobs_to_grads[key]}"
            total_jobs_rounded = (round(compare_total_jobs_to_grads[key], 2))

            if total_jobs_rounded == 0:
                display_text = f"State: {key}\t Total jobs: {num_jobs_in_state[key]}\t\t Total college grads: " \
                               f"{num_grads_in_state[key]}\t\t {total_jobs_rounded} jobs available " \
                               f"per graduating student"
                display_data.writelines(f"{key}, {total_jobs_rounded}\n")

            else:
                display_text = f"State: {key}\t Total jobs: {num_jobs_in_state[key]}\t Total college grads: " \
                               f"{num_grads_in_state[key]}\t\t {total_jobs_rounded} jobs available " \
                               f"per graduating student"
                display_data.writelines(f"{key}, {total_jobs_rounded}\n")

            list_item = QListWidgetItem(display_text, listview=self.list_control)
            list_item.setForeground(Qt.darkRed)

        display_data.close()
        DisplayMap.display_map(compare_total_jobs_to_grads)

        # DATA ANALYSIS PART 2A
        # Compare the 3 year graduate cohort declining balance percentage to the 25% salary in the state

        # Select school_state, repayment_repayment_cohort_3_year_declining_balance_2016 from school_export
        # Update a dictionary of states with sums of the data from each state in above cursor
        #
        # Select area_title and a_pct25 from jobdata_by_state
        # Update the area_title to convert to state (use earlier function)
        # Update dictionary of states with sums of the data for each state
        #
        # Then divide a_pct25 / 2016_cohort

        # PART 2A

        repayment_2016_dict = {"AK": 0, "AL": 0, "AR": 0, "AS": 0, "AZ": 0, "CA": 0,
                               "CO": 0, "CT": 0, "DC": 0, "DE": 0, "FL": 0, "FM": 0, "GA": 0,
                               "GU": 0, "HI": 0, "IA": 0, "ID": 0, "IL": 0, "IN": 0, "KS": 0,
                               "KY": 0, "LA": 0, "MA": 0, "MD": 0, "ME": 0, "MH": 0, "MI": 0,
                               "MN": 0, "MO": 0, "MP": 0, "MS": 0, "MT": 0, "NC": 0, "ND": 0,
                               "NE": 0, "NH": 0, "NJ": 0, "NM": 0, "NV": 0, "NY": 0, "OH": 0,
                               "OK": 0, "OR": 0, "PA": 0, "PR": 0, "PW": 0, "RI": 0, "SC": 0,
                               "SD": 0, "TN": 0, "TX": 0, "UT": 0, "VA": 0, "VI": 0, "VT": 0,
                               "WA": 0, "WI": 0, "WV": 0, "WY": 0}

        cursor.execute(
            'SELECT school_state, repayment_repayment_cohort_3_year_declining_balance_2016 FROM school_export')
        table = cursor.fetchall()

        for idx, row in enumerate(table):
            if row[1] is None:
                continue

            else:
                state_from_school_export = str(row[0])
                repayment_2016_data = row[1]
                repayment_2016_data_tot_sum = repayment_2016_dict[state_from_school_export]
                repayment_2016_dict[state_from_school_export] = repayment_2016_data + repayment_2016_data_tot_sum

        for key in repayment_2016_dict:
            if repayment_2016_dict[key] == 0:
                repayment_2016_dict[key] = 0.0001  # States with 0 data get this due to dividing by 0

            print(key, repayment_2016_dict[key])

        # ########################### PART 2B
        # cursor.execute(
        #     'SELECT area_title, a_pct25 FROM jobdata_by_state')
        # table = cursor.fetchall()
        #
        # for idx, row in enumerate(table):
        #     record = f"From jobdata_by_state: [school_state] [a_pct25] {row[0]}, {row[1]}"
        #     print(record)  # print(idx, row, record)
        #
        # # ##################### Need to convert state to state initial
        # state_from_school_export = str(row[0])
        # print(state_from_school_export, "made the cut", "occ code ->", check_occ_code,
        #       "state abbreviated: ", abbreviate_state(state_from_school_export),
        #       "total_emp col: ", row[2])
        #
        # abbr_state = abbreviate_state(state_from_school_export)
        # tot_emp_jobs_in_state = int(row[2])
        # tot_emp = num_jobs_in_state[abbr_state]
        # num_jobs_in_state[abbr_state] = tot_emp + tot_emp_jobs_in_state

        close_db(conn)

    def sort_ascending(self):
        self.list_control.sortItems(Qt.AscendingOrder)

    def sort_descending(self):
        self.list_control.sortItems(Qt.DescendingOrder)

    def swap_color_checkbox(self):
        self.render_map_checkbox.setChecked(False)

    def swap_render_map_checkbox(self):
        self.render_map_checkbox.setChecked(False)

    def center(self):
        screen_center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
        self_geometry = self.frameGeometry()
        self_geometry.moveCenter(screen_center)
        self.move(self_geometry.topLeft())


class GUIWindow(QMainWindow):
    def __init__(self, db_filename_from_main):
        super().__init__()
        self.setWindowFlag(Qt.WindowMinMaxButtonsHint, False)
        self.db_name = db_filename_from_main
        self.render_gui = RenderData(db_filename_from_main)
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
        self.setGeometry(100, 100, 400, 70)
        self.setFixedSize(400, 100)
        self.statusBar().showMessage("")
        self.gui_components()
        self.center()
        self.show()

    def gui_components(self):
        update_data = QPushButton("Update Data", self)
        update_data.clicked.connect(self.update_data)
        update_data.resize(update_data.sizeHint())
        update_data.move(20, 25)
        # implement hover over button to update status bar with file chosen

        render_data_button = QPushButton("Render data analysis", self)
        render_data_button.clicked.connect(self.render_data)
        render_data_button.move(140, 25)
        render_data_button.resize(render_data_button.sizeHint())
        # disable this button until file has been selected

        quit_button = QPushButton("Exit", self)
        quit_button.clicked.connect(QApplication.instance().quit)
        quit_button.clicked.connect(QCloseEvent)
        quit_button.resize(quit_button.sizeHint())
        quit_button.move(300, 25)
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

        file_name = QFileDialog.getOpenFileName(self, "Please select an .xlsx file to import from")[0]
        print(file_name, " was the file selected.")
        conn, cursor = open_db(self.db_name)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        read_excel_data(file_name, cursor)
        close_db(conn)
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))

        self.statusBar().showMessage(f"Update success from: {file_name} on {datetime.now()}")

        return file_name

    def render_data(self):
        self.render_gui.show()
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
