import urllib
import GUI_Sprint4
import main

def test_get_meta_data():
    test_url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=id," \
               "school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_" \
               "count_over_poverty_line,2016.repayment.3_yr_repayment.overall,school.state,2016.repayment.repayment_cohort." \
               "3_year_declining_balance"

    results = GUI_Sprint4.get_metadata(test_url)
    assert results[0] > 1000


def test_database():
    test_url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&" \
                "fields=id,school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_" \
                "completion.overall_count_over_poverty_line,2016.repayment.3_yr_repayment.overall,school.state," \
                "2016.repayment.repayment_cohort.3_year_declining_balance"

    # This dict below came from the above url and will be used to compare against the data inserted into the new db
    # via the test below
    test_datadict = {
        "school_id": "165024",
        "school_name": "Bridgewater State University",
        "school_city": "Bridgewater",
        "student_size_2018": "9312",
        "student_size_2017": "9390",
        "earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017":  "2137",
        "repayment_3_yr_repayment_overall_2016": "4403",
        "school_state": "MA",
        "repayment_repayment_cohort_3_year_declining_balance_2016": "0.6359300477"
    }

    test_school_id = test_datadict["school_id"]

    test_dbname = "test_db.db"
    conn, cursor = GUI_Sprint4.open_db(test_dbname)
    GUI_Sprint4.setup_school_db(cursor)
    test_meta_data = GUI_Sprint4.get_metadata(test_url)
    GUI_Sprint4.process_data(test_url, test_meta_data, cursor)

    test_result = cursor.execute("""
                            SELECT *
                            FROM school_export
                            WHERE school_id = ?""", (test_school_id,))

    for row in test_result:
        print(f'School id: {row[0]}  \nTest DB school id: {test_datadict["school_id"]} \n\n'
              f'School name: {row[1]}\nTest DB school name: {test_datadict["school_name"]}\n\n'
              f'School city: {row[2]}\nTest DB school city: {test_datadict["school_city"]}\n\n'
              f'School student size 2018: {row[3]}\nTest DB School size 2018: {test_datadict["student_size_2018"]}\n\n'
              f'School student size 2017: {row[4]}\nTest DB Student size 2017: {test_datadict["student_size_2017"]}\n\n'
              f'2017 earnings over poverty: {row[5]}\nTest DB 2017 earnings over poverty: '
              f'{test_datadict["earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017"]}\n\n'
              f'3 yr repayment 2016: {row[6]}\n'
              f'Test DB 3 yr repayment 2016: {test_datadict["repayment_3_yr_repayment_overall_2016"]}\n'
              f'School state: {row[7]}\nTest DB School state: {test_datadict["school_state"]}\n\n'
              f'2016 Repayment cohort 3 yr declining balance: {row[8]}\n')

    assert row[0] == int(test_datadict["school_id"])
    GUI_Sprint4.close_db(conn)


def test_xlsx_read():

    # Original excel document contains 22 'Massachusetts' major entries
    test_assertion_data = "Massachusetts"
    counter = 0
    times_assertion_data_appears = 22

    test_dbname = "test_db.db"
    test_xls_filename = "state_M2019_dl.xlsx"
    xls_link = "https://webhost.bridgew.edu/jsantore/Spring2021/Capstone/state_M2019_dl.xlsx"

    urllib.request.urlretrieve(xls_link, test_xls_filename)

    conn, cursor = GUI_Sprint4.open_db(test_dbname)
    GUI_Sprint4.setup_school_db(cursor)
    GUI_Sprint4.read_excel_data(test_xls_filename, cursor)

    # Execute select statement for all rows that contain "Massachusetts"
    test_result = cursor.execute("""
                               SELECT *
                               FROM jobdata_by_state
                               WHERE area_title = ?""", (test_assertion_data,))

    for row in test_result:
        print(*row)
        counter += 1

    # If test passes, we should have read in all entries from the xlsx file, exported them to the db, and then
    # read in all data containing 'Massachusetts' (22 total from xlsx file) from the db.
    assert counter == times_assertion_data_appears

    GUI_Sprint4.close_db(conn)


def test_new_table_exists():
    test_dbname = "test_db.db"
    conn, cursor = GUI_Sprint4.open_db(test_dbname)

    table_name = "jobdata_by_state"

    test_result = cursor.execute("""
                                   SELECT count(*)
                                   FROM sqlite_master
                                   WHERE type='table' AND name = ?""", (table_name,))

    # If cursor returns a 1, table exists.
    table_exists = test_result.fetchone()[0]

    if table_exists == 1:
        print(f"Table {table_name} exists.")
    else:
        print(f"Table {table_name} does not exist.")

    assert(table_exists == 1)

    GUI_Sprint4.close_db(conn)


def test_old_table_exists():
    test_dbname = "test_db.db"
    conn, cursor = GUI_Sprint4.open_db(test_dbname)

    table_name = "school_export"

    result = cursor.execute("""    SELECT count(*)
                                   FROM sqlite_master
                                   WHERE type='table' AND name = ?""", (table_name,))

    # If cursor returns a 1, table exists.
    table_exists = result.fetchone()[0]

    if table_exists == 1:
        print(f"Table {table_name} exists.")
    else:
        print(f"Table {table_name} does not exist.")

    assert(table_exists == 1)
    GUI_Sprint4.close_db(conn)


def test_insert_xls_db():
    # (area_title, occ_code, occ_title, tot_emp, h_pct25, a_pct25, unique_id)
    test_data = ("Test_area_title", 0, "Test_occ_title", 0, 0, 0, "123456789")

    test_dbname = "test_db.db"
    conn, cursor = GUI_Sprint4.open_db(test_dbname)

    GUI_Sprint4.insert_xls_db(cursor, test_data)

    # read back what we just wrote to the database
    test_result = cursor.execute("""
                                  SELECT *
                                  FROM jobdata_by_state
                                  WHERE area_title = ?""", (test_data[0],))

    for row in test_result:
        print(*row)

    # assert -> selected case matches previous test_data case
    assert str(row[0]) == test_data[6]
    GUI_Sprint4.close_db(conn)


def test_abbreviate_state():
    abbr_state = GUI_Sprint4.abbreviate_state("Alaska")
    assert abbr_state == "AK"

    abbr_state = GUI_Sprint4.abbreviate_state("Hawaii")
    assert abbr_state != "AK"
