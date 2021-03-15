import sys
import GUI_Sprint4
import PySide6.QtWidgets


def run_gui(db_filename):
    qt_app = PySide6.QtWidgets.QApplication(sys.argv)  # sys.argv is the list of command line arguments
    my_window = GUI_Sprint4.GUIWindow(db_filename)
    my_window.show()
    sys.exit(qt_app.exec_())


def main():
    db_name = "school_data.db"

    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=id," \
          "school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_" \
          "count_over_poverty_line,2016.repayment.3_yr_repayment.overall,school.state,2016.repayment.repayment_cohort.3_" \
          "year_declining_balance"

    run_gui(db_name, url)


if __name__ == '__main__':
    main()
