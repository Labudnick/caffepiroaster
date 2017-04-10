sql =  "select "
sql += "substr(datetime,12,4) || '0' as date, "
sql += "round(min(sens_temp), 2) as sens_temp "
sql += "from sensors "
sql += "where id in ( select id from sensors order by id desc limit 1440 ) "
sql += "group by substr(datetime,1,15) || '0' "

print (sql)
