import sqlite3
import os

root = os.path.dirname(__file__)
conn = sqlite3.connect(root + '/caffepiroaster.db')
c = conn.cursor()

sql = "CREATE TABLE IF NOT EXISTS RoastStatus ( "
sql += "Id          INTEGER PRIMARY KEY AUTOINCREMENT, "
sql += "RoastLogId  INTEGER, "
sql += "Time        STRING DEFAULT '00:00', "
sql += "Temperature REAL, "
sql += "Status      INTEGER DEFAULT 0, "
sql += "Heating     INTEGER DEFAULT 0)"
c.execute(sql)
if c.execute("SELECT count(*) from RoastStatus").fetchone()[0] == 0:
    c.execute("INSERT INTO RoastStatus (Status) VALUES (0)")
else:
    c.execute("UPDATE RoastStatus SET Status=0 and Time='00:00'")
conn.commit()

sql = "CREATE TABLE IF NOT EXISTS RoastLog ( "
sql += "Id INTEGER PRIMARY KEY AUTOINCREMENT, "
sql += "DateTime DATETIME DEFAULT (datetime('now','localtime')), "
sql += "Description STRING)"
c.execute(sql)

sql = "CREATE TABLE IF NOT EXISTS RoastDetails ("
sql += "Id INTEGER PRIMARY KEY AUTOINCREMENT, "
sql += "Time STRING, "
sql += "Heating NUMBER, "
sql += "TempRead REAL, "
sql += "TempSet REAL, "
sql += "RoastLogId INTEGER, "
sql += "FOREIGN KEY (RoastLogId) REFERENCES RoastLog(Id))"
c.execute(sql)

c.execute("CREATE INDEX IF NOT EXISTS idx_RoastDetails ON RoastDetails(RoastLogId)")

c.execute('CREATE TABLE IF NOT EXISTS parameters (id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, value STRING)')
if c.execute('SELECT count(*) from parameters').fetchone()[0] == 0:
    c.execute("INSERT INTO parameters (name, value) values ('roast_temp_max', '225')")
    conn.commit()


class DataAccess:
    def getcurrentstate(self):
        sqlq = "SELECT round(Temperature, 2) as Temperature, Time, Status, Heating, RoastLogId FROM RoastStatus LIMIT 1"
        c.execute(sqlq)
        return c.fetchone()

    def getroastdatabyid(self):
        retval = ""
        if roastlogid:
            sqlq = "SELECT "
            sqlq += "    Time, "
            sqlq += "    Heating, "
            sqlq += "    round(TempRead, 2) as TempRead, "
            sqlq += "    TempSet "
            sqlq += "FROM RoastDetails "
            sqlq += "WHERE RoastLogId IN (SELECT RoastLogId FROM RoastStatus)"

            c.execute(sqlq)
            retval = c.fetchall()
        return retval

    def insertroastdetails(self, roastlogid, time, heating, tempread, tempset, roasting):
        if roasting == 1:
            sqlq = "INSERT INTO RoastDetails (roastlogid, time, heating, tempread, tempset)  VALUES ("
            sqlq += str(roastlogid) + ", "
            sqlq += "'" + time + "', "
            sqlq += str(heating) + ", "
            sqlq += str(tempread) + ", "
            sqlq += str(tempset) + ")"
            c.execute(sqlq)
        sqlq = "UPDATE RoastStatus SET "
        sqlq += "Time = '" + str(time) + "', "
        sqlq += "Temperature = " + str(tempread) + ", "
        sqlq += "Heating = " + str(heating)
        c.execute(sqlq)
        conn.commit()

    def getroasttempmax(self):
        return c.execute("SELECT value FROM Parameters WHERE name='roast_temp_max'").fetchone()

    def startroasting(self, description):
        c.execute("INSERT INTO RoastLog (Description) VALUES ('" + description + "')")
        lastrowid = c.lastrowid
        sqlq = "UPDATE RoastStatus SET "
        sqlq += "Status = 1, "
        sqlq += "RoastLogId = " + str(lastrowid)
        c.execute(sqlq)
        conn.commit()

    def endroasting(self):
        c.execute("UPDATE RoastStatus SET Time = '00:00', Status = 0, RoastLogId = ''")
        conn.commit()

    def checkroasting(self):
        c.execute("SELECT Status, Temperature, RoastLogId FROM RoastStatus LIMIT 1")
        return c.fetchone()
