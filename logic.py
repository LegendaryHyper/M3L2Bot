import sqlite3
from config import DATABASE # Kütüphane ve modüller.

# Yetenek ve proje durumu olasılıkları (veritabanından silinmesi halinde geri eklenebilir.)
skills = [ (_,) for _ in (['Python', 'SQL', 'API', 'Discord'])]
statuses = [ (_,) for _ in (['Prototip Oluşturma', 'Geliştirme Aşamasında', 'Tamamlandı, kullanıma hazır', 'Güncellendi', 'Tamamlandı, ancak bakımı yapılmadı'])]

class DB_Manager: # Sınıf tanımı
    def __init__(self, database):
        self.database = database # Veri tabanı dosyasının tanımının eklenmesi.
        
    def create_tables(self): # Tabloları oluşturma.
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''') 
            conn.execute('''CREATE TABLE skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT
                        )''')
            conn.execute('''CREATE TABLE project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                        )''')
            conn.execute('''CREATE TABLE status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT
                        )''')
            conn.commit()

    def __executemany(self, sql, data): # Çoklu SQL çalıştırma fonksiyonu.
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    def __execute(self, sql): # SQL çalıştırma fonksiyonu.
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(sql)
            conn.commit()
    def __select_data(self, sql, data = tuple()): # Belirli bir kısmı seçip döndürür.
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
        
    def default_insert(self): # Varsayılan yetenek ve proje durumlarını veri tabanına ekler.
        sql = 'INSERT OR IGNORE INTO skills (skill_name) values(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (status_name) values(?)'
        data = statuses
        self.__executemany(sql, data)


    def insert_project(self, data): # Proje ekler.
        sql = "INSERT INTO projects (user_id, project_name, url, status_id) values(?, ?, ?, ?)"
        self.__executemany(sql, data)
    def insert_project_w_desc(self, data): # Açıklama ile ekler.
        sql = "INSERT INTO projects (user_id, project_name, description, url, status_id) values(?, ?, ?, ?, ?)"
        self.__executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill): # Projeye yetenek ekler.
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills VALUES(?, ?)'
        self.__executemany(sql, data)


    def get_statuses(self):
        sql = "SELECT status_name from status"
        return self.__select_data(sql)
        

    def get_status_id(self, status_name): # Proje durumunu döndürür.
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_projects(self, user_id): # Proje döndürür.
        sql = "SELECT * FROM projects WHERE user_id = ?"
        return self.__select_data(sql, data = (user_id,))
        
    def get_project_id(self, project_name, user_id): # Belirli bir projenin kimlik sayısını döndürür.
        return self.__select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?  ', data = (project_name, user_id,))[0][0]
        
    def get_skills(self): # Tüm olası yetenek girdilerini döndürür.
        return self.__select_data(sql='SELECT * FROM skills')
    
    def get_project_skills(self, project_name):
        res = self.__select_data(sql='''SELECT skill_name FROM projects 
JOIN project_skills ON projects.project_id = project_skills.project_id 
JOIN skills ON skills.skill_id = project_skills.skill_id 
WHERE project_name = ?''', data = (project_name,) )
        return ', '.join([x[0] for x in res])
    
    def get_project_info(self, user_id, project_name):
        sql = """
SELECT project_name, description, url, status_name FROM projects 
JOIN status ON
status.status_id = projects.status_id)
WHERE project_name=? AND user_id=?
"""
        return self.__select_data(sql=sql, data = (project_name, user_id))


    def update_projects(self, param, data): # Proje tablosunda belirli bir parametreye yeni bir değer atar.
        sql = "UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?"
        self.__executemany(sql, [data])


    def delete_project(self, user_id, project_id): # Projeyi siler.
        sql = "DELETE from projects WHERE user_id = ? AND project_id = ?"
        self.__executemany(sql, [(user_id, project_id)])
    
    def delete_skill(self, project_id, skill_id): # (Bu project_skills olmayacak mıydı?)
        sql = "DELETE from skills WHERE skill_id = ? AND project_id = ?"
        self.__executemany(sql, [(skill_id, project_id)])
    def alter_projects(self, new_column_name, new_column_type): # Projeye belirli bir ad ve türde yeni bir satır ekler.
        sql = f"ALTER TABLE projects ADD COLUMN {new_column_name} {new_column_type}"
        self.__execute(sql)
    def delete_project_column(self, new_column_name): # Projeye belirli bir ad ve türde yeni bir satır ekler.
        sql = f"ALTER TABLE projects DROP COLUMN {new_column_name}"
        self.__execute(sql)


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    # manager.delete_project_column("screenshots")
    # manager.create_tables()
    # manager.default_insert()