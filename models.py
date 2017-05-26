import sqlite3
import os
import datetime

root = os.path.dirname(__file__)
conn = sqlite3.connect(root + '/caffepiroaster.db')

c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS temp_reads (id INTEGER PRIMARY KEY AUTOINCREMENT, sens_temp real, datetime string, heat number)')
c.execute('DELETE from temp_reads')
conn.commit()
c.execute("CREATE TABLE IF NOT EXISTS roast_process (id INTEGER PRIMARY KEY AUTOINCREMENT, datetime STRING DEFAULT '00:00', status NUMBER, currtemp REAL)")
if (c.execute("SELECT count(*) from roast_process").fetchone()[0] == 0):
    c.execute("INSERT INTO roast_process (status) VALUES (0)")
else:
    c.execute("UPDATE roast_process SET status=0 and datetime='00:00'")
conn.commit()

c.execute('CREATE TABLE IF NOT EXISTS parameters (id INTEGER PRIMARY KEY AUTOINCREMENT, param_name STRING, param_value string)')

if (c.execute('SELECT count(*) from parameters').fetchone()[0] == 0):
    c.execute("INSERT INTO parameters (param_name, param_value) values ('roast_temp_max', '225')")
    conn.commit()

class Sensors():
    def getLast(self):
        c.execute('SELECT round(currtemp, 2), datetime FROM roast_process LIMIT 1')
        return c.fetchone()

    def getAll(self):
        sql = "select "
        sql += "datetime as date, "
        sql += "round(sens_temp, 2) as sens_temp, "
        sql += "heat "
        sql += "from temp_reads "
      
        c.execute(sql)
        return c.fetchall()

    def insertData(self, sens_temp, datetime, heat, roasting):
        print datetime
        if roasting == 1:
            sql = "INSERT INTO temp_reads (sens_temp, datetime, heat)  VALUES ("
            sql += str(sens_temp)
            sql += ",'" + datetime
            sql += "'," + str(heat)
            sql += ")"
            c.execute(sql)
        c.execute("UPDATE roast_process SET currtemp = " + str(sens_temp) + ", datetime = '" + datetime +"'")
        conn.commit()

    def eraseData(self):
        #print "Data erased"
        c.execute('DELETE from temp_reads')
        conn.commit()

    def getRoastTempMax(self):
        return c.execute("SELECT param_value from parameters where param_name='roast_temp_max'").fetchone()

    def startRoasting(self):
        c.execute("UPDATE roast_process SET status = 1")
        conn.commit()

    def endRoasting(self):
        c.execute("UPDATE roast_process SET datetime = '00:00', status = 0")
        conn.commit()

    def checkRoasting(self):
        c.execute("SELECT status FROM roast_process LIMIT 1")
        return c.fetchone()[0]

