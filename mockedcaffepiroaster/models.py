import sqlite3
import os

root = os.path.dirname(__file__)
conn = sqlite3.connect(root + '/caffepiroaster.db')

c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS sensors (id INTEGER PRIMARY KEY AUTOINCREMENT, sens_temp real, datetime string )')

class Sensors():
    def getLast(self):
        c.execute('SELECT round(sens_temp, 2) FROM sensors ORDER BY id DESC LIMIT 1')
        return c.fetchone()

    def getDay(self):
      sql =  "select "
      sql += "substr(datetime,12,4) || '0' as date, "
      sql += "round(avg(sens_temp), 2) as sens_temp "
      sql += "from sensors "
      sql += "where id in ( select id from sensors order by id desc limit 1440 ) "
      sql += "group by substr(datetime,1,15) || '0' "

      c.execute(sql)
      return c.fetchall()

    def InsertData(self, sens_temp, datetime):
        c.execute("INSERT INTO sensors (sens_temp, datetime)  VALUES ("+str(sens_temp)+",'"+datetime+"')")
        conn.commit()

