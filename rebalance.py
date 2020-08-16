import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os


def main():
    load_dotenv(override=True)
    DB_NAME = os.getenv("DB_NAME")
    USER = os.getenv("USER")
    HOST = os.getenv("HOST")
    DB_PASS = os.getenv("DB_PASS")

    conn = psycopg2.connect(dbname=DB_NAME, user=USER, host=HOST, password=DB_PASS)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("""TRUNCATE TABLE subjectlist RESTART IDENTITY""")
    cur.execute("""INSERT INTO subjectlist (subject) (SELECT DISTINCT(subject) FROM userinformation)""")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()

# select * from (SELECT id, row_number() over (order by id) as row, subject FROM subjectlist) as a where row % 2 = 1
