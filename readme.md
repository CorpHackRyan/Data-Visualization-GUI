    Last updated: 2/17/21

    Sprint2 (for Project 1)
    Authored by: Ryan O'Connor

roconnor-Sprint2 is a program that takes the data we have requested from a given URL with specific field parameters in it. It will then create a local database and import the data it has collected from our data.gov link.

    INSTALL DIRECTIONS

Do not forget to have a secrets.py in the same directory and add your API key to it 

Your secrets.py file should look like:  
      api_key = "xxx"
    
Where xxx is your API key for data.gov


    DATABASE LAYOUT

The database is laid out as a single table labeled 'school_export'. Inside this table is a school_id which is used as the primary key for the table. The data we collect is then imported into the database with columns that are labeled similar to the field parameters used to gather the information from the website.  

MISSING FROM PROJECT: 
- Nothing
