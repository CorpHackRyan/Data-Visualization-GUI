    Last updated: 2/24/21

    Sprint3 (for Project 1)
    Authored by: Ryan O'Connor

roconnor-Sprint3 is a program that navigates a local copy of a MS-Excel through the use of the openpyxl library in Python. It parses through the data with specific parameters and exports that data row by row to a new table in an already existing database.

    INSTALL DIRECTIONS

Do not forget to have a secrets.py in the same directory and add your API key to it 

Your secrets.py file should look like:  
      api_key = "xxx"
    
Where xxx is your API key for data.gov


    DATABASE LAYOUT

The database is laid out as a single table labeled 'school_export'. Inside this table is a school_id which is used as the primary key for the table. The data we collect is then imported into the database with columns that are labeled similar to the field parameters used to gather the information from the website.  

REQUIREMENTS:
- dependencies: openpyxl, requests, urllib
- api key,
- internet connection
- 