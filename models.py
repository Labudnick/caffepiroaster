import sqlite3
import os

root = os.path.dirname(__file__)
conn = sqlite3.connect(root + '/caffepiroaster.db')

c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS tbl_temperature_reads (id INTEGER PRIMARY KEY AUTOINCREMENT, sens_temp real, datetime string, roast number )')
c.execute('DELETE from tbl_temperature_reads')
conn.commit()

class Sensors():
    def getLast(self):
	print 'models.getLast'
        c.execute('SELECT round(sens_temp, 2) FROM tbl_temperature_reads ORDER BY id DESC LIMIT 1')
        return c.fetchone()

    def getAll(self):
      print 'models.getAll'
      sql =  "select "
      sql += "substr(datetime,12,4) || '0' as date, "
      sql += "round(sens_temp, 2) as sens_temp, "
      sql += "roast "
      sql += "from tbl_temperature_reads "
      sql += "order by id "
      print sql
      c.execute(sql)
      return c.fetchall()

    def InsertData(self, sens_temp, datetime, roast):
        print 'models.InsertData'
	c.execute("INSERT INTO sensors (sens_temp, datetime, roast)  VALUES ("+str(sens_temp)+",'"+datetime+"',"+roast+")")
        conn.commit()
	
