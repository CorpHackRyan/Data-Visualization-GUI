    Last updated: 3/22/21 - 1:59AM - Final Submission

    (To view the GUI test plan, please view the Ryan_OConnor_GUI_manual_test_plan.pdf file)
    
Data Visualization GUI is a program that will connect to api.data.gov through the API and request information about universities. It then takes that data and exports it into a newly created database. Next, it navigates through a local copy of a MS-Excel file (.xlsx) through the use of the openpyxl library in Python. It parses through the data with specific parameters and exports that data into to a new table in the already existing database.

When you load the application, you will be greeted with a small window with 3 options to choose from. You have the option to update data, render data analysis or quit the program. You must first update the data before you can render it. This is where the program will connect to data.gov, collect all the data and then prompt you to select the Excel file to insert into the database. 
If the update was a success, you will see a message in the status bar stating it was successful, otherwise you will receive an error message.

Once you have updated the data, you can now proceed to click render data analysis. This will bring up a window with multiple choices to select from for data points to display. Once you've picked the type of display you'd like to see (data in a listbox or data viewed on a choropleth map), click the visualize button and you will be able to display the results.
      
    REQUIREMENTS TO RUN
- dependencies: openpyxl, requests, plotly, pyside6, pandas, pyqt, libgl1-mesa-dev


    

- api key for data.gov in secrets

  
    DATABASE LAYOUT

The database created gets two tables. One is labeled 'school_export' which is populated from the api.dat.gov requests. The second table is called 'jobdata_by_state' and contains information about state wages and is populated from data collected in the xlsx file.   

    INSTALL DIRECTIONS

Do not forget to have a secrets.py in the same directory and add your API key to it 

Your secrets.py file should look like:  
      api_key = "xxx"
    
Where xxx is your API key for data.gov

