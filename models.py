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
sql += "temp_read           REAL, "
sql += "temp_set            REAL, "
sql += "status              INTEGER DEFAULT 0, "
sql += "heating             INTEGER DEFAULT 0, "
sql += "after_1crack_set    TEXT, "
sql += "roast_start_dt      DATETIME, "
sql += "first_crack_dt      DATETIME)"
c.execute(sql)

c.execute("DELETE FROM roast_status")
c.execute("INSERT INTO roast_status (status) VALUES (0)")
conn.commit()

sql = "CREATE TABLE IF NOT EXISTS roast_log ( "
sql += "id               INTEGER PRIMARY KEY AUTOINCREMENT, "
sql += "date_time        DATETIME DEFAULT (datetime('now','localtime')), "
sql += "coffee_name      TEXT, "
sql += "roast_size       TEXT, "
sql += "beans_size       INTEGER, "
sql += "description      TEXT, "
sql += "first_crack_time TEXT, "
sql += "roast_end_time   TEXT, "
sql += "from_1crack_time TEXT, "
sql += "after_1crack_set TEXT)"
c.execute(sql)

sql = "CREATE TABLE IF NOT EXISTS roast_details ("
sql += "id           INTEGER PRIMARY KEY AUTOINCREMENT, "
sql += "roast_time   TEXT, "
sql += "heating      NUMBER, "
sql += "temp_read    REAL, "
sql += "temp_set     REAL, "
sql += "roast_log_id INTEGER, "
sql += "FOREIGN KEY (roast_log_id) REFERENCES roast_log(id))"
c.execute(sql)

c.execute("CREATE INDEX IF NOT EXISTS idx_roast_details_fk ON roast_details(roast_log_id)")

c.execute('CREATE TABLE IF NOT EXISTS parameters (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, value TEXT)')
if c.execute('SELECT count(*) from parameters').fetchone()[0] == 0:
    c.execute("INSERT INTO parameters (name, value) values ('roast_temp_max', '215')")
    conn.commit()

if c.execute("select count(1) from roast_log where ifnull(roast_end_time, '') = ''").fetchone()[0] > 0:
    sql = 'UPDATE roast_log '
    sql += 'SET roast_end_time = datetime(date_time, '
    sql += '                              (SELECT "+" || substr(MAX(roast_time), 1, 2) || " minutes" '
    sql += '                                 FROM roast_details '
    sql += '                                WHERE roast_log_id = roast_log.id), '
    sql += '                              (SELECT "+" || substr(MAX(roast_time), 4, 2) || " seconds" '
    sql += '                                 FROM roast_details '
    sql += '                                WHERE roast_log_id = roast_log.id)) '
    sql += "WHERE ifnull(roast_end_time, '') = ''"
    c.execute(sql)
    conn.commit()

class DataAccess:
    def get_current_state(self):
        sqlq = "SELECT  round(temp_read, 2), "
        sqlq += "       strftime('%M:%S', julianday('now', 'localtime') - julianday(roast_start_dt)) AS roast_time, "
        sqlq += "       status, "
        sqlq += "       heating, "
        sqlq += "       roast_log_id, "
        sqlq += "       strftime('%M:%S', julianday(first_crack_dt) - julianday(roast_start_dt)) AS first_crack_time, "
        sqlq += "       strftime('%M:%S', julianday('now', 'localtime') - julianday(first_crack_dt)) AS from_1crack_time "
        sqlq += "FROM roast_status LIMIT 1"
        c.execute(sqlq)
        return c.fetchone()

    def get_roast_data_by_id(self, roast_log_id):
        sqlq = "SELECT  roast_time, "
        sqlq += "       heating, "
        sqlq += "       round(temp_read, 2) as temp_read, "
        sqlq += "       temp_set "
        sqlq += "FROM roast_details "
        sqlq += "WHERE roast_log_id = ?"
        c.execute(sqlq, (roast_log_id,))
        return c.fetchall()

    def insert_roast_details(self, roast_log_id, heating, temp_read, temp_set, roasting):
        if roasting > 0:
            sqlq = "INSERT INTO roast_details (roast_log_id, roast_time, heating, temp_read, temp_set) "
            sqlq += "VALUES (?, "
            sqlq += "        (SELECT strftime('%M:%S', julianday('now', 'localtime') - julianday(roast_start_dt)) "
            sqlq += "         FROM roast_status LIMIT 1), "
            sqlq += "        ?, ?, ?)"
            c.execute(sqlq, (str(roast_log_id), str(heating), str(temp_read), str(temp_set)))
        sqlq = "UPDATE roast_status SET "
        sqlq += "temp_read = ?, "
        sqlq += "heating = ? "
        c.execute(sqlq, (str(temp_read), str(heating)))
        conn.commit()

    def get_roast_temp_max(self):
        return c.execute("SELECT value FROM parameters WHERE name='roast_temp_max'").fetchone()

    def start_roasting(self, temp_set, description, coffee_name, roast_size, beans_size, after_1st_crack_time):
        sqlq = "INSERT INTO roast_log (description, coffee_name, roast_size, beans_size, after_1crack_set) "
        sqlq += "VALUES (?, UPPER(?), ?, ?, ?)"
        c.execute(sqlq, (description, coffee_name, roast_size, beans_size, after_1st_crack_time))
        lastrowid = c.lastrowid
        sqlq = "UPDATE roast_status SET "
        sqlq += "status = 1, "
        sqlq += "roast_log_id = ?, "
        sqlq += "temp_set = ?, "
        sqlq += "after_1crack_set = ?, "
        sqlq += "roast_start_dt = datetime('now', 'localtime')"
        c.execute(sqlq, (lastrowid, str(temp_set), after_1st_crack_time))
        conn.commit()
        return lastrowid

    def end_roasting(self, roast_log_id):
        sqlq = "UPDATE roast_log "
        sqlq += "SET roast_end_time = (SELECT strftime('%M:%S', julianday('now', 'localtime') - julianday(roast_start_dt)) "
        sqlq += "                      FROM roast_status LIMIT 1), "
        sqlq += "    from_1crack_time = (SELECT strftime('%M:%S', julianday('now', 'localtime') - julianday(first_crack_dt)) "
        sqlq += "                      FROM roast_status LIMIT 1) "
        sqlq += "WHERE id = ?"
        c.execute(sqlq, (roast_log_id,))
        c.execute("DELETE FROM roast_status")
        c.execute("INSERT INTO roast_status (status) VALUES (0)")
        conn.commit()

    def check_roasting(self):
        sqlq = "SELECT status, temp_read, temp_set, roast_log_id, after_1crack_set, "
        sqlq += "strftime('%M:%S', julianday('now', 'localtime') - julianday(first_crack_dt)) "
        sqlq += "FROM roast_status LIMIT 1"
        return c.execute(sqlq).fetchone()

    def set_first_crack(self):
        c.execute("UPDATE roast_status SET status = 2, first_crack_dt = datetime('now','localtime')")
        sqlq = "UPDATE roast_log "
        sqlq += "SET first_crack_time = ("
        sqlq += "   SELECT strftime('%M:%S', julianday('now', 'localtime') - julianday(roast_start_dt)) "
        sqlq += "   FROM roast_status LIMIT 1) "
        sqlq += "WHERE id IN (SELECT roast_log_id FROM roast_status LIMIT 1)"
        c.execute(sqlq)
        conn.commit()

    def set_roast_temp_max(self, roast_temp_max):
        c.execute("UPDATE roast_status SET temp_set = ?", (str(roast_temp_max),))
        conn.commit()

    def get_roasts_list(self, name_filter, sort_order, start_index, page_size):

        sqlq = "SELECT COUNT(1) FROM roast_log"
        if name_filter:
            sqlq += " WHERE UPPER(coffee_name) like UPPER('%" + name_filter + "%')"

        record_count = c.execute(sqlq).fetchone()

        conn.row_factory = sqlite3.Row
        d = conn.cursor()
        sqlq = "SELECT id, "
        sqlq += "upper(coffee_name) as coffee_name, "
        sqlq += "date_time, "
        sqlq += "roast_size, "
        sqlq += "beans_size, "
        sqlq += "description, "
        sqlq += "first_crack_time, "
        sqlq += "from_1crack_time as crack_to_end, "
        sqlq += "roast_end_time as start_to_end "
        sqlq += "FROM roast_log"
        if name_filter:
            sqlq += " WHERE UPPER(coffee_name) like '%" + name_filter + "%'"
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

    def get_initial_data(selfself):
        sqlq = "SELECT  s.roast_log_id, "
        sqlq += "       strftime('%M:%S', julianday('now', 'localtime') - julianday(s.roast_start_dt)) AS roast_time, "
        sqlq += "       s.temp_set, "
        sqlq += "       s.status, "
        sqlq += "       strftime('%M:%S', julianday(s.first_crack_dt) - julianday(s.roast_start_dt)) AS first_crack_time, "
        sqlq += "       strftime('%M:%S', julianday('now', 'localtime') - julianday(first_crack_dt)) AS from_1crack_time, "
        sqlq += "       l.coffee_name, "
        sqlq += "       l.roast_size, "
        sqlq += "       l.beans_size, "
        sqlq += "       l.description, "
        sqlq += "       s.after_1crack_set "
        sqlq += "FROM roast_status s LEFT JOIN roast_log l ON s.roast_log_id=l.id"
        return c.execute(sqlq).fetchone()