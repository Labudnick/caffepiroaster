import sqlite3
import os

root = os.path.dirname(__file__)
conn = sqlite3.connect(root + '/caffepiroaster.db')
c = conn.cursor()

sql = "CREATE TABLE IF NOT EXISTS RoastStatus ( "
sql += "Id          INTEGER PRIMARY KEY AUTOINCREMENT, "
sql += "RoastLogId  INTEGER, "
sql += "Time        STRING DEFAULT '00:00', "
sql += "TempRead    REAL, "
sql += "TempSet     REAL, "
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
        sqlq = "SELECT round(TempRead, 2) as TempRead, Time, Status, Heating, RoastLogId FROM RoastStatus LIMIT 1"
        c.execute(sqlq)
        return c.fetchone()

    def getcurrentroastdata(self):
        sqlq = "SELECT "
        sqlq += "    Time, "
        sqlq += "    Heating, "
        sqlq += "    round(TempRead, 2) as TempRead, "
        sqlq += "    TempSet "
        sqlq += "FROM RoastDetails "
        sqlq += "WHERE RoastLogId IN (SELECT RoastLogId FROM RoastStatus)"

        c.execute(sqlq)
        return c.fetchall()

    def insertroastdetails(self, roastlogid, time, heating, tempread, tempset, roasting):
        if roasting == 1:
            sqlq = "INSERT INTO RoastDetails (roastlogid, time, heating, tempread, tempset)  VALUES (?, ?, ?, ?, ?)"
            c.execute(sqlq, (str(roastlogid), time, str(heating), str(tempread), str(tempset)))

        sqlq = "UPDATE RoastStatus SET "
        sqlq += "Time = ?, "
        sqlq += "TempRead = ?, "
        sqlq += "Heating = ?"
        c.execute(sqlq, (time, str(tempread), str(heating)))
        conn.commit()

    def getroasttempmax(self):
        return c.execute("SELECT value FROM Parameters WHERE name='roast_temp_max'").fetchone()

    def startroasting(self, tempset, description):
        sqlq = "INSERT INTO RoastLog (Description) VALUES (?)"
        c.execute(sqlq, (description,))
        lastrowid = c.lastrowid
        sqlq = "UPDATE RoastStatus SET "
        sqlq += "Status = 1, "
        sqlq += "RoastLogId = ?, "
        sqlq += "TempSet = ?"
        c.execute(sqlq, (lastrowid, str(tempset)))
        conn.commit()

    def endroasting(self):
        c.execute("UPDATE RoastStatus SET Time = '00:00', Status = 0, RoastLogId = ''")
        conn.commit()

    def checkroasting(self):
        c.execute("SELECT status, tempread, tempset, roastlogid FROM roaststatus LIMIT 1")
        return c.fetchone()
