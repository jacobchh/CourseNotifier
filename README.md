# Course Notifier

My first publicly launched personal project with over 150 users! A Python program to automate notifications for open spots in UWO classes. Queries SQL database for user information,  scrapes the online timetable for every present subject, validates each course number, emails users if their listed course is open, and updates SQL database. Script is deployed on Google Cloud Compute Engines re-running every 24 hours on cron jobs. Supported by PostgreSQL on ElephantSQL. Rebalance.py runs in between jobs to redistribute the subject list across asynchronous scripts. Future support for text notification will be added.

Required Python libraries:
- bs4 (Beautiful Soup)
- Panadas
- Requests
- Dotenv
- Datetime
- Psycopg2

.env file configuration is present if you wish to set up this program locally with your own database. PostgreSQL configuration is "userinformation" table with columns "FirstName", "LastName", "Subject", "ClassNumber", "Email", and "PhoneNumber". Concurrent configuration is "subjectlist" table with columns "ID" as serial and "Subject" as primary key.

To run asynchronously on multiple servers, duplicate the scrape#.py file. Edit the readUserInformation() under main() passing in the number of scripts (n) you are running and the id number of that specific script from 0-n. This will allow the scripts to select different unique subjects from the userinformation and subjectlist table thus reducing the time between refreshes.
