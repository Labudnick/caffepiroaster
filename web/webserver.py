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
        data = DataAccess().getroastdatabyid(roastlogid)
        self.write(json.dumps(data))


class RoastStart(tornado.web.RequestHandler):
    def get(self):
        description = self.get_argument("description", None, True)
        DataAccess().startroasting(description)


class RoastEnd(tornado.web.RequestHandler):
    def get(self):
        DataAccess().endroasting()


class RoastTempMax(tornado.web.RequestHandler):
    def get(self):
        data = DataAccess().getroasttempmax()
        self.write(json.dumps(data))


application = tornado.web.Application([
    (r"/last/", TempLast),
    (r"/all/", TempAll),
    (r"/start/", RoastStart),
    (r"/end/", RoastEnd),
    (r"/roasttempmax/", RoastTempMax),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "index.html"})
])

if __name__ == '__main__':
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
