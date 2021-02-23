import requests
import secrets
import math
import json
import sqlite3
from typing import Tuple
from os import path
import os
import openpyxl


def process_data(url: str, meta_from_main, cursor: sqlite3.Cursor):
    #  meta_from_main is a list with the following index descriptions
    #                 0 index = total results
    #                 1 index = current page
    #                 2 index = results per page
    #                 3 index = total pages

    page_counter = 0
    final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"

    for page_counter in range(meta_from_main[3]):
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
                          school_data["2016.repayment.3_yr_repayment.overall"])

            print(f"Page {page_counter} of {meta_from_main[3]} ->", school_tpl)

            insert_db(cursor, school_tpl)

        page_counter += 1
        final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"


def insert_db(cursor, school_tuple):
    sql = '''INSERT INTO school_export (school_id, school_name, school_city, student_size_2018, student_size_2017,
                earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017, repayment_3_yr_repayment_overall_2016)
                VALUES (?,?,?,?,?,?,?)'''
    cursor.execute(sql, school_tuple)


def insert_xls_db(cursor: sqlite3.Cursor, xls_tuple):
    sql = '''INSERT INTO jobdata_by_state (area_title, occ_code, occ_title, tot_emp, h_pct25, a_pct25, unique_id)
                VALUES (?,?,?,?,?,?,?)'''
    cursor.execute(sql, xls_tuple)


def write_data(filename, data_response):
    with open(filename, 'a') as export_file:
        json.dump(data_response, export_file)
        export_file.write("\n")


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


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:

    print("file exists:"+str(path.exists(filename)))

    db_connection = sqlite3.connect(filename)
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()


def setup_school_db(cursor: sqlite3.Cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS school_export(
    school_id INTEGER PRIMARY KEY,
    school_name TEXT,
    school_city TEXT,
    student_size_2018 INTEGER,
    student_size_2017 INTEGER,
    earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017 INTEGER,
    repayment_3_yr_repayment_overall_2016 INTEGER
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


def read_excel_data(xls_filename, cursor: sqlite3.Cursor):

    work_book = openpyxl.load_workbook(xls_filename)
    work_sheet = work_book.active

    # BETTER SOLUTION: Get columns with specific titles so no matter what order they are in we can get correct data.
    # Hard coded columns which contain the specific data we are looking for
    # col 1=area_title,  col2=occ_code,  col3=occ_title,  col4=tot_emp,  col5=h_pct25,  col6=a_pct25
    cols = [1, 7, 8, 10, 19, 24]

    for row in work_sheet.iter_rows():
        cells = [cell.value for (idx, cell) in enumerate(row) if (
            idx in cols and cell.value is not None)]
        print(cells)
        cells.append(str(row[0].row))
        # add if statement to check if it is zero, so we skip the first row from adding into DB
        print(cells)
        insert_xls_db(cursor, cells)

    # work_sheet.title = "WageJob_data"
    # work_book.save("python_stage_wage.xlsx")


def main():
    # comment
    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=id," \
          "school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_" \
          "count_over_poverty_line,2016.repayment.3_yr_repayment.overall"

    db_name = "school_data.db"
    xls_filename = "state_M2019_dl.xlsx"

    meta_data = get_metadata(url)

    # If school_data.db exists, delete it. This ensures I can run this over and over.
    if os.path.exists("school_data.db"):
        os.remove("school_data.db")

    conn, cursor = open_db(db_name)
    setup_school_db(cursor)
    process_data(url, meta_data, cursor)

    read_excel_data(xls_filename, cursor)

    close_db(conn)


if __name__ == '__main__':
    main()
