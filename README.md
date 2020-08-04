# Course Notifier

My first publicly launched personal project with over 150 users! A Python program to automate notifications for open spots in UWO classes. Queries SQL database for user information,  scrapes the online timetable for every present subject, validates each course number, emails users if their listed course is open, and updates SQL database. Script is deployed on Google Cloud Compute Engines re-running every 24 hours on cron jobs. Supported by PostgreSQL on ElephantSQL. Future support for text notification will be added.

Required Python libraries:
- bs4 (Beautiful Soup)
- Panadas
- Requests
- Dotenv
- Datetime
- Psycopg2

.env file configuration is present if you wish to set up this program locally with your own database. PostgreSQL configuration is "userinformation" table with coloumns "First Name", "Last Name", "Subject", "Class Number", "Email", and "Phone Number".
