import os
import sys
import inspect
import tornado.ioloop
import tornado.web
import json

# import from parent directory
root = os.path.dirname(__file__)
os.chdir(root)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from models import DataAccess

os.system("python " + parentdir + "/roast_daemon.py &")

port = 8888


class TempLast(tornado.web.RequestHandler):
    def get(self):
        data = DataAccess().getcurrentstate()
        self.write(json.dumps(data))


class TempAll(tornado.web.RequestHandler):
    def get(self):
        data = DataAccess().getcurrentroastdata()
        self.write(json.dumps(data))


class RoastStart(tornado.web.RequestHandler):
    def get(self):
        description = self.get_argument("description", None, True)
        tempset = self.get_argument("tempset", None, True)
        coffee_name = self.get_argument("coffeeName", None, True)
        roast_size = self.get_argument("roastSize", None, True)
        beans_size = self.get_argument("beansSize", None, True)
        DataAccess().startroasting(float(tempset), description, coffee_name, roast_size, beans_size)


class RoastEnd(tornado.web.RequestHandler):
    def get(self):
        DataAccess().endroasting()


class FirstCrack(tornado.web.RequestHandler):
    def get(self):
        DataAccess().setfirstcrack()


class GetRoastTempMax(tornado.web.RequestHandler):
    def get(self):
        data = DataAccess().getroasttempmax()
        self.write(json.dumps(data))


class SetRoastTempMax(tornado.web.RequestHandler):
    def get(self):
        tempset = self.get_argument("tempset", None, True)
        DataAccess().setroasttempmax(tempset)


class GetRoastsList(tornado.web.RequestHandler):
    def post(self):
        jtSorting = self.get_argument("jtSorting", None, True)
        jtStartIndex = self.get_argument("jtStartIndex", None, True)
        jtPageSize = self.get_argument("jtPageSize", None, True)

        print jtSorting, jtStartIndex, jtPageSize
        roasts_list = DataAccess().getroastslist(jtSorting, jtStartIndex, jtPageSize)

        self.write(roasts_list)

class PowerOff(tornado.web.RequestHandler):
    def get(self):
        os.system("sudo poweroff &")

application = tornado.web.Application([
    (r"/last/", TempLast),
    (r"/all/", TempAll),
    (r"/start/", RoastStart),
    (r"/end/", RoastEnd),
    (r"/firstcrack/", FirstCrack),
    (r"/getroasttempmax/", GetRoastTempMax),
    (r"/setroasttempmax/", SetRoastTempMax),
    (r"/roastslist/", GetRoastsList),
    (r"/poweroff/", PowerOff),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "index.html"})
])

if __name__ == '__main__':
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
