import sqlite3
import bcrypt
from datetime import datetime

class Database(object):
    username = "root"
    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(b"root" , salt).decode()
    
    def __init__(self , database_name='database.sqlite3') -> None:
        self.database_name = database_name
        self.database = sqlite3.connect(database_name)
        self.cur = self.database.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS tools_informations(tools_name NOT NULL , tools_desc  NOT NULL, tools_path NOT NULL , tools_id NOT NULL , img_path NOT NULL , PRIMARY KEY(tools_id))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tools_panel(tools_id NOT NULL, input_name NOT NULL , input_place NOT NULL ,FOREIGN KEY(tools_id) REFERENCES tools_informations(tools_id))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS admin_panel(username NOT NULL, passwd NOT NULL , hint NOT NULL , email NOT NULL)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tool_logs(data_log NOT NULL, date_log NOT NULL, start_time NOT NULL)")
        self.database.commit()
        self.database.close()
        return None

    def read_tools(self) -> list:
        self.database = sqlite3.connect(self.database_name)
        self.cur = self.database.cursor()
        result = self.cur.execute("SELECT * FROM tools_informations;").fetchall()
        path_tools = [{'id':i[3] , 'path':i[2]} for i in result]
        informatiosn_tools = [{"title":i[0] , 'desc':i[1] , 'id':i[3] , 'img':i[4]} for i in result]
        self.database.commit()
        self.database.close()
        
        return path_tools , informatiosn_tools

    def get_tools(self , id_:str) -> list:
        self.database = sqlite3.connect(self.database_name)
        self.cur = self.database.cursor()
        result_1 = self.cur.execute("SELECT tools_name , tools_desc FROM tools_informations WHERE tools_id = ?;" , (id_)).fetchall()
        result_2 = self.cur.execute("SELECT input_name , input_place FROM tools_panel  WHERE tools_id = ?",(id_)).fetchall()
        tools_inputs = [{'text':i[0] ,'place':i[1]} for i in result_2]
        self.database.commit()
        self.database.close()
        return tools_inputs , result_1

    def write_logs(self , data , date , start_time):
        self.database = sqlite3.connect(self.database_name)
        self.cur = self.database.cursor()
        self.cur.execute("INSERT INTO tool_logs(data_log , date_log , start_time) VALUES(? ,? ,?);" , (data , date , start_time))
        self.database.commit()
        self.database.close()

    def read_log(self , date):
        self.database = sqlite3.connect(self.database_name)
        self.cur = self.database.cursor()
        result = self.cur.execute("SELECT * FROM tool_logs WHERE date_log = ?;" , (date,)).fetchone()
        self.database.commit()
        self.database.close()
        return result

    def check_user(self , username , password) -> bool:
        dt = datetime.now()
        date = str(dt.today().year) + "/" + str(dt.today().month) + "/" + str(dt.today().day) 
        time = str(dt.today().hour) + ":" + str(dt.today().minute) + ":" + str(dt.today().second)    
        self.database = sqlite3.connect(self.database_name)
        self.cur = self.database.cursor()
        passwd = self.cur.execute("SELECT passwd FROM admin_panel WHERE username = ?;", (username,)).fetchall()[0][0]
        if bcrypt.checkpw(password=password.encode() ,hashed_password=passwd.encode()):
            self.write_logs(data=f"The User {username} Was Login" , date=date , start_time=time)
            return True
        else:
            self.write_logs(data=f"The User {username} Can't Login" , date=date , start_time=time)
            return False

    def get_logs(self):
        self.database = sqlite3.connect(self.database_name)
        self.cur = self.database.cursor()
        result = self.cur.execute("SELECT * FROM tool_logs;").fetchall()
        self.database.commit()
        self.database.close()
        return result
    
    def get_photos(self):
        self.database = sqlite3.connect(self.database_name)
        self.cur = self.database.cursor()
        result = self.cur.execute("SELECT tools_id,img_path,tools_desc FROM tools_informations;").fetchall()
        self.database.commit()
        self.database.close()
        return result
    