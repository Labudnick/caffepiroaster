<<<<<<< HEAD
python ./temp.py 1>/dev/null 2>logerr_temp.log&
python -m tornado.autoreload /home/pi/projects/cafferoaster/web/webserver.py 2./logerr_webserver.log>&
=======
<<<<<<< HEAD
python ./temp.py 1>/dev/null 2>logerr_temp.log &
python -m tornado.autoreload ./web/webserver.py 2>./logerr_webserver.log &
=======
python ./temp.py 1>/dev/null 2>logerr_temp.log&
python -m tornado.autoreload /home/pi/projects/cafferoaster/web/webserver.py 2./logerr_webserver.log>&
>>>>>>> 2bd3f5fe3e729c308f5d0a49bc3c9b68b6cc83c5
>>>>>>> 2beaeca32f3fe08ac47d8f9c1275b850e34f9b60
