sudo killall python
cwd=$(pwd)
python -m tornado.autoreload $cwd/web/webserver.py 2>$cwd/logerr_webserver.log &
