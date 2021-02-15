import requests
import secrets
import math
import json
import sqlite3
from typing import Tuple


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


def write_data(filename, data_response):
    with open(filename, 'a') as export_file:
        json.dump(data_response, export_file)
        export_file.write("\n")


def get_metadata(url: str):
    final_url = f"{url}&api_key={secrets.api_key}&page=0"
    response = requests.get(final_url)

    if response.status_code != 200:
        print(response.text)
        return[]

    json_data = response.json()

    print(json_data)

    total_results = json_data["metadata"]["total"]
    current_page = json_data["metadata"]["page"]
    results_per_page = json_data["metadata"]["per_page"]
    total_pages = total_results / results_per_page

    return [total_results, current_page, results_per_page, math.ceil(total_pages)]


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(filename)
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()


def setup_db(cursor: sqlite3.Cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS school_export(
    school_id INTEGER PRIMARY KEY,
    school_name TEXT,
    school_city TEXT,
    student_size_2018 INTEGER,
    student_size_2017 INTEGER,
    earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017 INTEGER,
    repayment_3_yr_repayment_overall_2016 INTEGER
    );''')


def main():

    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=id," \
          "school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_" \
          "count_over_poverty_line,2016.repayment.3_yr_repayment.overall"

    db_name = "school_data.db"

    meta_data = get_metadata(url)

    conn, cursor = open_db(db_name)
    setup_db(cursor)
    process_data(url, meta_data, cursor)
    close_db(conn)


if __name__ == '__main__':
    main()
