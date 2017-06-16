import sqlite3
import json
import os

ROOT = os.path.dirname(__file__)
conn = sqlite3.connect(ROOT + '/coffeepiroaster.db')
c = conn.cursor()
c.execute("PRAGMA foreign_keys")

sql = "CREATE TABLE  IF NOT EXISTS roast_status ( "
sql += "id                  INTEGER PRIMARY KEY AUTOINCREMENT, "
sql += "roast_log_id        INTEGER, "
sql += "roast_time          TEXT DEFAULT '00:00', "
sql += "temp_read           REAL, "
sql += "temp_set            REAL, "
sql += "status              INTEGER DEFAULT 0, "
sql += "heating             INTEGER DEFAULT 0,"
sql += "first_crack_time    TEXT DEFAULT '00:00',"
sql += "first_crack_dt      DATETIME)"
c.execute(sql)
if c.execute("SELECT count(*) from roast_status").fetchone()[0] == 0:
    c.execute("INSERT INTO roast_status (status) VALUES (0)")
else:
    c.execute("UPDATE roast_status SET status=0 and roast_time='00:00'")
conn.commit()

sql = "CREATE TABLE IF NOT EXISTS roast_log ( "
sql += "id INTEGER PRIMARY KEY AUTOINCREMENT, "
sql += "date_time DATETIME DEFAULT (datetime('now','localtime')), "
sql += "coffee_name TEXT, "
sql += "roast_size TEXT, "
sql += "beans_size INTEGER, "
sql += "description TEXT,"
sql += "first_crack_time DATETIME"
sql += "roast_end_time DATETIME)"
c.execute(sql)

sql = "CREATE TABLE IF NOT EXISTS roast_details ("
sql += "id INTEGER PRIMARY KEY AUTOINCREMENT, "
sql += "roast_time TEXT, "
sql += "heating NUMBER, "
sql += "temp_read REAL, "
sql += "temp_set REAL, "
sql += "roast_log_id INTEGER, "
sql += "FOREIGN KEY (roast_log_id) REFERENCES roast_log(id))"
c.execute(sql)

c.execute("CREATE INDEX IF NOT EXISTS idx_roast_details_fk ON roast_details(roast_log_id)")

c.execute('CREATE TABLE IF NOT EXISTS parameters (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, value TEXT)')
if c.execute('SELECT count(*) from parameters').fetchone()[0] == 0:
    c.execute("INSERT INTO parameters (name, value) values ('roast_temp_max', '225')")
    conn.commit()

if c.execute("select count(1) from roast_log where roast_end_time = ''").fetchone()[0] > 0:
    sql = 'update ROAST_LOG set roast_end_time = datetime(date_time, (SELECT "+" || substr(MAX(roast_time), 1, 2) '
    sql += '|| " minutes" from roast_details WHERE roast_log_id = roast_log.id), (SELECT "+" || '
    sql += 'substr(MAX(roast_time), 4, 2) || " seconds" from roast_details WHERE roast_log_id = roast_log.id)) '
    sql += "WHERE roast_end_time = ''"
    c.execute(sql)
    conn.commit()

class DataAccess:
    def getcurrentstate(self):
        sqlq = "SELECT round(temp_read, 2), roast_time, status, heating, roast_log_id, first_crack_time "
        sqlq += "FROM roast_status LIMIT 1"
        c.execute(sqlq)
        return c.fetchone()

    def get_roast_data_by_id(self, roast_log_id):
        sqlq = "SELECT "
        sqlq += "    roast_time, "
        sqlq += "    heating, "
        sqlq += "    round(temp_read, 2) as temp_read, "
        sqlq += "    temp_set "
        sqlq += "FROM roast_details "
        sqlq += "WHERE roast_log_id = ?"

        c.execute(sqlq, (roast_log_id,))
        return c.fetchall()

    def insertroastdetails(self, roast_log_id, roast_time, heating, temp_read, temp_set, roasting, first_crack_time):
        if roasting > 0:
            sqlq = "INSERT INTO roast_details (roast_log_id, roast_time, heating, temp_read, temp_set) "
            sqlq += "VALUES (?, ?, ?, ?, ?)"
            c.execute(sqlq, (str(roast_log_id), roast_time, str(heating), str(temp_read), str(temp_set)))

        sqlq = "UPDATE roast_status SET "
        sqlq += "roast_time = ?, "
        sqlq += "temp_read = ?, "
        sqlq += "heating = ?,"
        sqlq += "first_crack_time = ?"
        c.execute(sqlq, (roast_time, str(temp_read), str(heating), first_crack_time))
        conn.commit()

    def getroasttempmax(self):
        return c.execute("SELECT value FROM parameters WHERE name='roast_temp_max'").fetchone()

    def startroasting(self, temp_set, description, coffee_name, roast_size, beans_size):
        sqlq = "INSERT INTO roast_log (description, coffee_name, roast_size, beans_size) VALUES (?, UPPER(?), ?, ?)"
        c.execute(sqlq, (description, coffee_name, roast_size, beans_size))
        lastrowid = c.lastrowid
        sqlq = "UPDATE roast_status SET "
        sqlq += "status = 1, "
        sqlq += "roast_log_id = ?, "
        sqlq += "temp_set = ?"
        c.execute(sqlq, (lastrowid, str(temp_set)))
        conn.commit()
        return lastrowid

    def endroasting(self):
        sqlq = "UPDATE roast_status "
        sqlq += "SET roast_time = '00:00', status = 0, roast_log_id = '', first_crack_time='00:00', first_crack_dt=''"
        c.execute(sqlq)
        conn.commit()

    def checkroasting(self):
        c.execute("SELECT status, temp_read, temp_set, roast_log_id, first_crack_dt FROM roast_status LIMIT 1")
        return c.fetchone()

    def setfirstcrack(self):
        c.execute("UPDATE roast_status SET status = 2, first_crack_dt=datetime('now', 'localtime')")
        sqlq = "UPDATE roast_log "
        sqlq += "SET first_crack_time=datetime('now', 'localtime')"
        sqlq += "WHERE id IN (SELECT roast_log_id FROM roast_status LIMIT 1)"
        c.execute(sqlq)
        conn.commit()

    def setroasttempmax(self, roast_temp_max):
        c.execute("UPDATE roast_status SET temp_set = ?", (str(roast_temp_max),))
        conn.commit()

    def getroastslist(self, sort_order, start_index, page_size):

        record_count = c.execute("SELECT COUNT(1) FROM roast_log").fetchone()

        conn.row_factory = sqlite3.Row
        d = conn.cursor()
        sqlq = "SELECT id, upper(coffee_name) as coffee_name, date_time, roast_size, beans_size, description, "
        sqlq += "strftime('%M:%S', time(julianday(first_crack_time) - julianday(date_time))) as first_crack_time, "
        sqlq += "strftime('%M:%S', time(julianday(roast_end_time) - julianday(first_crack_time))) as crack_to_end, "
        sqlq += "strftime('%M:%S', time(julianday(roast_end_time) - julianday(date_time))) as start_to_end "
        sqlq += "FROM roast_log"
        if sort_order:
            sqlq += " ORDER BY " + sort_order
        sqlq += " LIMIT " + page_size + " OFFSET " + start_index
        rows = d.execute(sqlq).fetchall()

        conn.row_factory = ''
        return json.dumps({"Result": "OK", "Records": [dict(ix) for ix in rows], "TotalRecordCount": record_count})

    def delete_past_roast(self, roast_log_id):
        c.execute("DELETE FROM roast_details WHERE roast_log_id = ?", (roast_log_id,))
        c.execute("DELETE FROM roast_log WHERE id = ?", (roast_log_id,))
        conn.commit()
        return json.dumps({"Result": "OK"})

    def update_past_roast(self, row_id, coffee_name, roast_size, beans_size, description):
        sqlq = "UPDATE roast_log SET coffee_name = UPPER(?), roast_size = ?, beans_size = ?, description = ? "
        sqlq += "WHERE id = ?"
        c.execute(sqlq, (coffee_name, roast_size, beans_size, description, row_id))
        conn.commit()
