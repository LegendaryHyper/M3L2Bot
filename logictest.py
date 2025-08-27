import sqlite3
from config import token, DATABASE

class DB_Manager:
    def __init__(self, database):
        self.database = database # veri tabanının adı
        
    def create_tables(self):
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        with con:
            cur.execute('''
            CREATE TABLE IF NOT EXISTS VideoRelease(
                VidReleaseID INTEGER PRIMARY KEY,
                VidReleasePeriod TEXT
                )
                        ''')
            cur.execute('''
            CREATE TABLE IF NOT EXISTS VideoViews(
                VidViewsID INTEGER PRIMARY KEY,
                VidViewCount TEXT
                )
                        ''')
            cur.execute('''
            CREATE TABLE IF NOT EXISTS videos(
                ID INTEGER PRIMARY KEY,
                Title TEXT,
                Channel TEXT,
                VidReleaseID INTEGER,
                VidViewsID INTEGER,
                FOREIGN KEY (VidReleaseID)  REFERENCES VideoRelease (VidReleaseID) ON DELETE CASCADE,
                FOREIGN KEY (VidViewsID)  REFERENCES VideoViews (VidViewsID) ON DELETE CASCADE
                )
            ''')
            con.commit()

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()