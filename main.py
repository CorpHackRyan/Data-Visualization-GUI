import requests
import secrets
import math
import json
import sqlite3
from typing import Tuple


def process_data(url: str, meta_from_main, export_filename):
    #  meta_from_main is a list with the following index descriptions
    #                 0 index = total results
    #                 1 index = current page
    #                 2 index = results per page
    #                 3 index = total pages

    page_counter = 0
    final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"

    # for page_counter in range(meta_from_main[3]):
    for page_counter in range(1):  # testing purposes for just 1 page of data to export to db
        response = requests.get(final_url)

        if response.status_code != 200:
            print(response.text)
            exit(-1)

        json_data = response.json()


        # All the results on each page in a singular list returned
        each_page_data = json_data["results"]

        for school_data in each_page_data:
            # Sprint 1 - export data to txt file
            # print(school_data)
            # write_data(export_filename, school_data)

            # Sprint 2 - export data to database
            # write to database
            # right here, school_data[dict has 7 entries]
            # need to look at each list, reference the DB column name I have without ints', when matched,
            # add it to that rows, using id as unique identifier
            # Probably need to loop through each school_data to export each field-key matching
            # and insert into DB

            print(school_data["school.name"])








        page_counter += 1
        final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"


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
    cursor.execute('''CREATE TABLE IF NOT EXISTS students(
    banner_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gpa REAL DEFAULT 0,
    credits INTEGER DEFAULT 0
    );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS course(
    course_prefix TEXT NOT NULL,
    course_number INTEGER NOT NULL,
    cap INTEGER DEFAULT 20,
    description TEXT,
    PRIMARY KEY(course_prefix, course_number)
    );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS school_data(
    registration_id INTEGER PRIMARY KEY,
    course_prefix TEXT NOT NULL,
    course_number INTEGER NOT NULL,
    banner_id INTEGER NOT NULL,
    registration_date TEXT,
    FOREIGN KEY (banner_id) REFERENCES student (banner_id)
    ON DELETE CASCADE ON UPDATE NO ACTION,
    FOREIGN KEY (course_prefix, course_number) REFERENCES courses (course_prefix, course_number)
    ON DELETE CASCADE ON UPDATE NO ACTION
    );''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS school_export(
    school_id INTEGER PRIMARY KEY, 
    school_name TEXT,
    school_city TEXT,
    student_size_2018 INTEGER,
    student_size_2017 INTEGER,
    earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017 INTEGER,
    repayment_3_yr_repayment_overall_2016 INTEGER 
    );''')


def make_initial_courses(cursor: sqlite3.Cursor):
    # cursor.execute('''INSERT INTO COURSE (course_prefix, course_number, cap, description)
    # VALUES ('COMP', 151, 24, 'This is the intro course, you will learn to program, maybe for the first time')''')

    # cursor.execute('''INSERT INTO COURSE (course_prefix, course_number, cap, description)
    # VALUES ('COMP', 490, 20, 'This is the final course. You will get a chance to apply much of what you learned troughout the undergrad degree')''')

    # cursor.execute('''INSERT INTO COURSE (course_prefix, course_number, cap, description)
    # VALUES ('MATH', 130, 20, 'This course is changing to include much more on graph theory and number bases/systems')''')

    # cursor.execute('''
    return[]




def main():

    og_url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=school." \
          "name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_count_over_" \
          "poverty_line,2016.repayment.3_yr_repayment.overall"

    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=id," \
          "school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_count_over_" \
          "poverty_line,2016.repayment.3_yr_repayment.overall"

    file_name = "school_export.txt"

    db_name = "school_data.db"

    meta_data = get_metadata(url)
    process_data(url, meta_data, file_name)

    conn, cursor = open_db(db_name)

    setup_db(cursor)
    # make_initial_courses(cursor)
    print(cursor)
    close_db(conn)


if __name__ == '__main__':
    main()
