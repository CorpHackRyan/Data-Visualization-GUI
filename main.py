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
    run_gui(db_name)


if __name__ == '__main__':
    main()
