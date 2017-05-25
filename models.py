import sqlite3
import os

root = os.path.dirname(__file__)
conn = sqlite3.connect(root + '/caffepiroaster.db')

c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS temp_reads (id INTEGER PRIMARY KEY AUTOINCREMENT, sens_temp real, datetime string, heat number, roasting number)')
c.execute('DELETE from temp_reads')
conn.commit()

c.execute('CREATE TABLE IF NOT EXISTS parameters (id INTEGER PRIMARY KEY AUTOINCREMENT, param_name STRING, param_value string)')

if (c.execute('SELECT count(*) from parameters').fetchone()[0] == 0):
    c.execute("INSERT INTO parameters (param_name, param_value) values ('roast_temp_max', '225')")
    conn.commit()

class Sensors():
    def getLast(self):
        #print "models.Sensors().getLast"
        c.execute('SELECT round(sens_temp, 2), datetime FROM temp_reads ORDER BY id DESC LIMIT 1')
        return c.fetchone()

    def getAll(self):
        sql =  "select "
        sql += "substr(datetime,3,4) || '0' as date, "
        sql += "round(sens_temp, 2) as sens_temp, "
        sql += "heat "
        sql += "from temp_reads "
        sql += "where roasting = 1 "
      
        c.execute(sql)
        return c.fetchall()

    def InsertData(self, sens_temp, datetime, heat, roasting):
        sql = "INSERT INTO temp_reads (sens_temp, datetime, heat, roasting)  VALUES ("
        sql += str(sens_temp)
        sql += ",'" + datetime
        sql += "'," + str(heat)
        sql += "," + str(roasting)
        sql += ")"
        c.execute(sql)
        conn.commit()

    def EraseData(self):
        #print "Data erased"
        c.execute('DELETE from temp_reads')
        conn.commit()

    def GetRoastTempMax(self):
        return c.execute("SELECT param_value from parameters where param_name='roast_temp_max'").fetchone()
