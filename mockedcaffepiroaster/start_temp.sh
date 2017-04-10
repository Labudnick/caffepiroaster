python ./temp.py 1>/dev/null 2>logerr_temp.log&
python -m tornado.autoreload /home/pi/projects/cafferoaster/web/webserver.py 2./logerr_webserver.log>&
