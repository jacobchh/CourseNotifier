import requests
import pandas as pd
import time as t
from datetime import datetime, time
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os
import traceback

TIMETABLE_URL = 'https://studentservices.uwo.ca/secure/timetables/mastertt/ttindex.cfm'
SUBJECT_CODES = {'ACTURSCI': 'Actuarial Science', 'AMERICAN': 'American Studies',
                 'ANATCELL': 'Anatomy and Cell Biology', 'ANTHRO': 'Anthropology', 'APPLMATH': 'Applied Mathematics',
                 'ARABIC': 'Arabic', 'AH': 'Art History', 'ARTHUM': 'Arts and Humanities', 'ASTRONOM': 'Astronomy',
                 'BIBLSTUD': 'Biblical Studies', 'BIOCHEM': 'Biochemistry', 'BIOLOGY': 'Biology',
                 'BME': 'Biomedical Engineering', 'BIOSTATS': 'Biostatistics', 'BUSINESS': 'Business Administration',
                 'CALCULUS': 'Calculus', 'CGS': 'Centre for Global Studies', 'CBE': 'Chem & Biochem Engineering',
                 'CHEMBIO': 'Chemical Biology', 'CHEM': 'Chemistry', 'CSI': 'Childhood & Social Institutns',
                 'CHINESE': 'Chinese', 'CHURCH': 'Church History', 'CHURLAW': 'Church Law',
                 'CHURMUSI': 'Church Music', 'CEE': 'Civil & Envrnmntl Engineering', 'CLASSICS': 'Classical Studies',
                 'CMBPROG': 'Combined Program Enrollment', 'COMMSCI': 'Communication Sci & Disorders',
                 'COMPLIT': 'Comparative Lit & Culture', 'COMPSCI': 'Computer Science', 'DANCE': 'Dance',
                 'DIGICOMM': 'Digital Communication', 'DIGIHUM': 'Digital Humanities',
                 'DISABST': 'Disability Studies', 'EARTHSCI': 'Earth Sciences', 'ECONOMIC': 'Economics',
                 'EELC': 'Education English Language Cen', 'ECE': 'Elect & Computer Engineering',
                 'ENGSCI': 'Engineering Science', 'ENGLISH': 'English', 'ENVIRSCI': 'Environmental Science',
                 'EPID': 'Epidemiology', 'EPIDEMIO': 'Epidemiology & Biostatistics', 'FIMS': 'FIMS',
                 'FAMLYSTU': 'Family Studies & Human Develop', 'FLDEDUC': 'Field Education', 'FILM': 'Film Studies',
                 'FINMOD': 'Financial Modelling', 'FOODNUTR': 'Foods and Nutrition', 'FRENCH': 'French',
                 'GEOGRAPH': 'Geography', 'GEOLOGY': 'Geology', 'GERMAN': 'German', 'GGB': 'Global Great Books',
                 'GLE': 'Governance,Leadership & Ethics', 'GREEK': 'Greek', 'GPE': 'Green Process Engineering',
                 'HEALTSCI': 'Health Sciences', 'HEBREW': 'Hebrew', 'HISTTHEO': 'Historical Theology',
                 'HISTORY': 'History', 'HISTSCI': 'History of Science', 'HOMILET': 'Homiletics',
                 'HUMANECO': 'Human Ecology', 'HUMANRS': 'Human Rights Studies', 'INDIGSTU': 'Indigenous Studies',
                 'INTEGSCI': 'Integrated Science', 'ICC': 'Intercultural Communications',
                 'INTERDIS': 'Interdisciplinary Studies', 'INTREL': 'International Relations', 'ITALIAN': 'Italian',
                 'JAPANESE': 'Japanese', 'JEWISH': 'Jewish Studies', 'MTP-BRJR': 'Journalism-Broadcasting Fanshw',
                 'KINESIOL': 'Kinesiology', 'LATIN': 'Latin', 'LAW': 'Law', 'LS': 'Leadership Studies',
                 'LINGUIST': 'Linguistics', 'LITURST': 'Liturgical Studies', 'LITURGIC': 'Liturgics',
                 'MOS': 'Management & Organizational St', 'MTP-MKTG': 'Marketing - Fanshawe', 'MATH': 'Mathematics',
                 'MME': 'Mech & Materials Engineering', 'MSE': 'Mechatronic Systems Engineerin',
                 'MIT': 'Media, Information &Technocult', 'MEDBIO': 'Medical Biophysics',
                 'MEDHINFO': 'Medical Health Informatics', 'MEDSCIEN': 'Medical Sciences',
                 'MEDIEVAL': 'Medieval Studies', 'MICROIMM': 'Microbiology & Immunology',
                 'MORALTHE': 'Moral Theology', 'MTP-MMED': 'Multimed Dsgn & Prod Fanshawe',
                 'MCS': 'Museum and Curatorial Studies', 'MUSIC': 'Music', 'NEURO': 'Neuroscience',
                 'NURSING': 'Nursing', 'ONEHEALT': 'One Health', 'PASTTHEO': 'Pastoral Theology',
                 'PATHOL': 'Pathology', 'PHARM': 'Pharmacology', 'PHILST': 'Philosophical Studies',
                 'PHILOSOP': 'Philosophy', 'PHYSICS': 'Physics', 'PHYSIOL': 'Physiology',
                 'PHYSPHRM': 'Physiology and Pharmacology', 'POLISCI': 'Political Science',
                 'PPE': 'Politics, Philosophy, Economic', 'PSYCHOL': 'Psychology',
                 'REHABSCI': 'Rehabilitation Sciences', 'RELEDUC': 'Religious Education',
                 'RELSTUD': 'Religious Studies', 'SACRTHEO': 'Sacramental Theology', 'SCHOLARS': 'Scholars Electives',
                 'SCIENCE': 'Science', 'SOCLJUST': 'Social Justice & Peace Studies', 'SOCSCI': 'Social Science',
                 'SOCWORK': 'Social Work', 'SOCIOLOG': 'Sociology', 'SE': 'Software Engineering',
                 'SPANISH': 'Spanish', 'SPEECH': 'Speech', 'SPIRTHEO': 'Spiritual Theology',
                 'STATS': 'Statistical Sciences', 'SA': 'Studio Art', 'SYSTHEO': 'Systematic Theology',
                 'THANAT': 'Thanatology', 'THEATRE': 'Theatre Studies', 'THEOETH': 'Theological Ethics',
                 'THEOLST': 'Theological Studies', 'THESIS': 'Thesis', 'TJ': 'Transitional Justice',
                 'WTC': 'Western Thought & Civilization', 'WOMENST': "Women's Studies",
                 'WORLDLIT': 'World Literatures and Cultures', 'WRITING': 'Writing'}


# returns a dictionary of all courseCodes and their statuses for a given subject
# subject code is in all caps
def getCourseCodeStatus(subjectCode):
    data = {'subject': subjectCode, 'command': 'search'}
    r = requests.post(TIMETABLE_URL, data)
    soup = BeautifulSoup(r.text, 'html.parser')

    # retrieves all different courses for given subject
    courseList = soup.findAll("table", class_="table table-striped")
    for i in range(len(courseList)):
        courseList[i] = courseList[i].find("tbody")

    statusDict = {}

    # store all courses in a list
    for course in courseList:
        # store all sections per course in a list
        tempSectionList = course.findAll("tr")
        # every other 'tr' tag is a day of week table therefore it is ignored
        tempSectionList = tempSectionList[::2]

        for section in tempSectionList:
            sectionInfo = section.findAll("td")
            # td 3 and 10 are course number and class status
            statusDict[sectionInfo[2].text] = sectionInfo[-3].text.strip()

    return statusDict


# returns a list of all class names (1000-4000) for a given subject
def findCourseTitles(subjectCode):
    data = {'subject': subjectCode, 'command': 'search'}
    r = requests.post(TIMETABLE_URL, data)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Get the course titles through filtering 'h4' header tags
    courseTitles = []
    courseList = soup.find_all("h4")
    for course in courseList:
        courseTitles.append(course.text)
    return courseTitles


# imports user information from csv file with pandas, returns a sorted data frame
def readUserInformation(cur, scripts, idNum):
    scripts = str(scripts)
    idNum = str(idNum)
    cur = cur
    cur.execute("""SELECT subject FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS row, subject FROM subjectlist) AS t WHERE t.row % """ + scripts + " = " + idNum)

    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["Subject"], dtype="string")

    queryStr = "("
    for index, row in df.iterrows():
        queryStr += "'" + row["Subject"] + "',"

    queryStr = """SELECT * FROM userinformation WHERE subject IN """ + queryStr[:len(queryStr)-1] + ")"

    cur.execute(queryStr)

    rows = cur.fetchall()
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=["First Name", "Last Name", "Subject", "Class Number", "Email", "Phone Number"],
                      dtype="string")
    df = df.sort_values(["Subject", "Class Number"])

    return df


# sends an email notification to the user
def emailUser(name, email, courseNumber, subject):
    SENDER_EMAIL = os.getenv("EMAIL")
    SENDER_PASSWORD = os.getenv("EMAIL_PASS")

    receiverName = name
    receiverEmail = email
    courseNumber = courseNumber
    subject = subject  # "Calculus"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your UWO Course Is Now Open!"
    message["From"] = SENDER_EMAIL
    message["To"] = receiverEmail

    # write the plain text part
    text = """\
    Hi {name},

    A spot in your {subject} class #{xxxx} just opened up! Log into Student Center right away to register.

    Your information will be deleted from our database soon. If you could not get into your class, please sign up again on our website to receive another notification.

    - MyUWOCourseIsFull
    """

    # write the HTML part
    html = """\
    <html>
        <body>
            <div>
                <div>Hi {name},</div>
                <div><br></div>
                <div>A spot in your {subject} class #{xxxx} just opened up! Log into <a href="https://student.uwo.ca/">Student Center</a> right away to register.<br></div>
                <div><br></div>
                <div>
                    Your information will be deleted from our database soon. If you could not get into your class, please sign up again on our <a href="https://www.coursenotifier.com/">website</a> to receive another notification.<br>
                    <div><br></div>
                    <div>
                        - CourseNotifier
                        <div></div>
                        <div><br></div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    # convert both parts to MIMEText objects and add them to the MIMEMultipart message
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # set up the SMTP server
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, receiverEmail,
                    message.as_string().format(name=receiverName, subject=subject, xxxx=courseNumber))
    server.close()


# sends an email notification to the user saying that the course number was invalid
def emailUserCourseError(name, email, courseNumber, subject):
    SENDER_EMAIL = os.getenv("EMAIL")
    SENDER_PASSWORD = os.getenv("EMAIL_PASS")

    receiverName = name
    receiverEmail = email
    courseNumber = courseNumber
    subject = subject  # "Calculus"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Class Number Is Invalid!"
    message["From"] = SENDER_EMAIL
    message["To"] = receiverEmail

    # write the plain text part
    text = """\
    Hi {name},

    The class number you entered for {subject} class #{xxxx} is invalid!

    Please refer to the "What's This?" link on our website, and sign up again to receive another notification.

    - MyUWOCourseIsFull
    """

    # write the HTML part
    html = """\
    <html>
        <body>
            <div>
                <div>Hi {name},</div>
                <div><br></div>
                <div>The class number you entered for {subject} class #{xxxx} is invalid!<br></div>
                <div><br></div>
                <div>
                    Please refer to this <a href="https://www.coursenotifier.com/class-number.png">picture</a> on identifying your class number, and sign up again on our <a href="https://www.coursenotifier.com/">website</a> to receive another notification.<br>
                    <div><br></div>
                    <div>
                        - CourseNotifier
                        <div></div>
                        <div><br></div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    # convert both parts to MIMEText objects and add them to the MIMEMultipart message
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # set up the SMTP server
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, receiverEmail,
                    message.as_string().format(name=receiverName, subject=subject, xxxx=courseNumber))
    server.close()


# sends an email notification to the administrator informing of an error
def emailAdminError(errorMsg):
    SENDER_EMAIL = os.getenv("EMAIL")
    SENDER_PASSWORD = os.getenv("EMAIL_PASS")

    receiverEmail = "jacob.chun@gmail.com"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Program Error"
    message["From"] = SENDER_EMAIL
    message["To"] = receiverEmail

    # write the plain text
    text = "There was an error with program #1. Please check the components.\n\n{error}"

    # convert the text to MIMEText objects and add them to the MIMEMultipart message
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    # set up the SMTP server
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, receiverEmail, message.as_string().format(error=errorMsg))
    server.close()


# loops through the pandas data frame and checks all requested courses' status
# emails all users with "Not Full" courses and then deletes their information
# saves the updated csv file
def loopThroughDataFrame(userDataFrame, cur):
    # check if the data frame is empty before processing it
    if userDataFrame.empty:
        t.sleep(20)
        return

    cur = cur

    # get all the subjects present in the data frame
    subjectList = userDataFrame["Subject"].unique()

    # create a dictionary where subject is the key and a list of all class numbers present in data frame is the value
    presentUserCourses = {}
    for subject in subjectList:
        tempDf = userDataFrame.loc[userDataFrame["Subject"] == subject]
        classNumberList = tempDf["Class Number"].unique()
        presentUserCourses[subject] = classNumberList

    # loop through each subject and each list of class numbers to find which ones are "Not Full"
    # create a list of course numbers that are open
    listOfOpenCourses = []
    for subject in presentUserCourses.keys():
        courseStatus = getCourseCodeStatus(subject)

        # check if the program encountered a captcha
        if courseStatus == {}:
            t.sleep(10)
            continue

        for classNumber in presentUserCourses[subject]:
            # removes the user if the class number is not valid
            try:
                if courseStatus[classNumber] == "Not Full":
                    listOfOpenCourses.append(classNumber)
            except KeyError:
                dfFiltered = userDataFrame.loc[userDataFrame["Class Number"] == classNumber]
                for index, row in dfFiltered.iterrows():
                    emailUserCourseError(row["First Name"], row["Email"], row["Class Number"],
                                         SUBJECT_CODES[row["Subject"]])
                # delete user from database
                cur.execute("""DELETE FROM userInformation WHERE classNumber = '""" + classNumber + "';")

        # pauses for 6 secs before looping to avoid captcha code from website
        t.sleep(6)

    # loop through each open course, return all users that have selected that course and email them
    for classNumber in listOfOpenCourses:
        dfFiltered = userDataFrame.loc[userDataFrame["Class Number"] == classNumber]
        for index, row in dfFiltered.iterrows():
            emailUser(row["First Name"], row["Email"], row["Class Number"], SUBJECT_CODES[row["Subject"]])
        # delete users from database
        cur.execute("""DELETE FROM userInformation WHERE classNumber = '""" + classNumber + "';")


def main():
    load_dotenv(override=True)
    DB_NAME = os.getenv("DB_NAME")
    USER = os.getenv("USER")
    HOST = os.getenv("HOST")
    DB_PASS = os.getenv("DB_PASS")

    conn = psycopg2.connect(dbname=DB_NAME, user=USER, host=HOST, password=DB_PASS)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    start = time(23, 50)
    end = time(23, 55)

    while True:
        try:
            # query user information from PostgreSQl and return a data frame of user information
            # enter the number (n) of scripts you're running and the id number of the script from 0 to n-1
            userDataFrame = readUserInformation(cur, 2, 0)

            # loop through data frame, email users, delete users from database that have been messaged
            loopThroughDataFrame(userDataFrame, cur)
        except:
            # emails the admin if there is any error
            error = traceback.format_exc()
            emailAdminError(str(error))
            exit()

        # time to restart script
        now = datetime.now().time()
        if start < now < end:
            cur.close()
            conn.close()
            exit()


if __name__ == "__main__":
    main()
