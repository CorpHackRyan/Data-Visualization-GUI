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

    # This dict below came from the above url and will be used to compare against the data inserted into the new db
    # via the test below
    test_datadict = {
        "id": "165024",
        "school_name": "Bridgewater State University",
        "school_city": "Bridgewater",
        "student_size_2018": "9312",
        "student_size_2017": "9390",
        "earnings_3_yrs_after_completion_overall_count_over_poverty_line_2017":  "2137",
        "repayment_3_yr_repayment_overall_2016": "4403"
    }

    test_dbname = "test_db.db"
    conn, cursor = main.open_db(test_dbname)
    #main.setup_school_db(cursor)
    #test_meta_data = main.get_metadata(test_url)
    #main.process_data(test_url, test_meta_data, cursor)
    #main.close_db(conn)

    # pull a unique id # off the initial database , store it in here
    # do a sql query to match something in the db with our verified test data,
    # assert this.

#    2. The second test should create a new empty database, run your table creation function/method, then run your save data to
#    database method then check to see that the database contains the test university that you just put there

