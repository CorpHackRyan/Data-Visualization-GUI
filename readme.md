    Last updated: 2/25/21 - 11:45PM - Final Submission

    Sprint3 (for Project 1)
    Authored by: Ryan O'Connor

roconnor-Sprint3 is a program that will connect to api.data.gov through the API and request information about universities. It then takes that data and exports it into a newly created database. Next, it navigates through a local copy of a MS-Excel file (.xlsx) through the use of the openpyxl library in Python. It parses through the data with specific parameters and exports that data into to a new table in the already existing database.

      REQUIREMENTS TO RUN
- dependencies: openpyxl, requests

- api key for data.gov in secrets

  
    DATABASE LAYOUT

The database created gets two tables. One is labeled 'school_export' which is populated from the api.dat.gov requests. The second table is called 'jobdata_by_state' and contains information about state wages and is populated from data collected in the xlsx file.   

    INSTALL DIRECTIONS

Do not forget to have a secrets.py in the same directory and add your API key to it 

Your secrets.py file should look like:  
      api_key = "xxx"
    
Where xxx is your API key for data.gov

