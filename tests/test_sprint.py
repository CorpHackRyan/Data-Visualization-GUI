import main
import urllib

def test_get_meta_data():
    test_url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=id," \
          "school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_" \
          "count_over_poverty_line,2016.repayment.3_yr_repayment.overall"

    results = main.get_metadata(test_url)
    assert results[0] > 1000


def test_database():
    test_url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=id," \
              "school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_" \
              "count_over_poverty_line,2016.repayment.3_yr_repayment.overall"

    # This dict below came from the above url and will be used to compare against the data inserted into the new db
    # via the test below
    test_datadict = {
        "school_id": "165024",
        "school_name": "Bridgewater State University",
        "school_city": "Bridgewater",
        "student_size_2018": "9312",
        "student_size_2017": "9390",
        "earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017":  "2137",
        "repayment_3_yr_repayment_overall_2016": "4403"
    }

    test_school_id = test_datadict["school_id"]

    test_dbname = "test_db.db"
    conn, cursor = main.open_db(test_dbname)
    main.setup_school_db(cursor)
    test_meta_data = main.get_metadata(test_url)
    main.process_data(test_url, test_meta_data, cursor)

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
              f'Test DB 3 yr repayment 2016: {test_datadict["repayment_3_yr_repayment_overall_2016"]}')

    assert row[0] == int(test_datadict["school_id"])

    main.close_db(conn)


def test_xlsx_read():

    # Make sure our read from excel file works properly

    # So read  use the function from main to read the excel. it will then create the xcel file
    # then, tak ea row of data of that file, and compare it to the data we have stored in our dict

    # Random row of data with columns we need from actual excel file
    test_datadict = {
        # col 1=area_title,  col7=occ_code,  col8=occ_title, col9=o_group, col10=tot_emp,  col19=h_pct25,  col24=a_pct25
        "area_title": "Massachusetts",
        "occ_code": "15-0000",
        "occ_title": "Computer and Mathematical Occupations",
        "o_group": "major",
        "tot_emp": "147070",
        "h_pct25": "34.25",
        "a_pct25": "156450"
    }

    test_dbname = "test_db.db"
    test_xls_filename = "state_M2019_dl.xlsx"

    xls_link = "https://webhost.bridgew.edu/jsantore/Spring2021/Capstone/state_M2019_dl.xlsx"
    urllib.request.urlretrieve(xls_link, test_xls_filename)

    conn, cursor = main.open_db(test_dbname)
    main.setup_school_db(cursor)
    main.read_excel_data(test_xls_filename, cursor)

    # test_result = cursor.execute("""
    #                           SELECT *
    #                           FROM jobdata_by_state
    #                           WHERE school_id = ?""", (test_school_id,))

    #test_school_id = test_datadict["school_id"]
    #test_meta_data = main.get_metadata(test_url)
    #main.process_data(test_url, test_meta_data, cursor)


    #for row in test_result:
    #    print(f'School id: {row[0]}  \nTest DB school id: {test_datadict["school_id"]} \n\n'
    #          f'School name: {row[1]}\nTest DB school name: {test_datadict["school_name"]}\n\n'
    #          f'School city: {row[2]}\nTest DB school city: {test_datadict["school_city"]}\n\n'
    #         f'School student size 2018: {row[3]}\nTest DB School size 2018: {test_datadict["student_size_2018"]}\n\n'
    #          f'School student size 2017: {row[4]}\nTest DB Student size 2017: {test_datadict["student_size_2017"]}\n\n'
    #          f'2017 earnings over poverty: {row[5]}\nTest DB 2017 earnings over poverty: '
    #          f'{test_datadict["earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017"]}\n\n'
    #          f'3 yr repayment 2016: {row[6]}\n'
    #          f'Test DB 3 yr repayment 2016: {test_datadict["repayment_3_yr_repayment_overall_2016"]}')

    #assert row[0] == int(test_datadict["school_id"])

    main.close_db(conn)



