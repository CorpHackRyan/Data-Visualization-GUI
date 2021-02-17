import main


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

    conn, cursor = main.open_db("test_db.db")
    main.setup_school_db(cursor)
    test_meta_data = main.get_metadata(test_url)
    main.process_data(test_url, test_meta_data, cursor)
    main.close_db(conn)

#    2. The second test should create a new empty database, run your table creation function/method, then run your save data to
#    database method then check to see that the database contains the test university that you just put there
