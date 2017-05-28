import os,sys,inspect
import tornado.ioloop
import tornado.web
import json
import threading#, time

# import from parent directory
root = os.path.dirname(__file__)
os.chdir(root)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from models import Sensors

os.system("python " + parentdir + "/roast_daemon.py &")

port = 8888

class TempLast(tornado.web.RequestHandler):
    def get(self):
        data = Sensors().getLast();
        self.write(json.dumps(data))

class TempAll(tornado.web.RequestHandler):
    def get(self):
      #print "TempAll started"
      data = Sensors().getAll()
      self.write(json.dumps(data))

class RoastStart(tornado.web.RequestHandler):
    def get(self):
      #print "RoastStart.get"
      Sensors().startRoasting()
      #self.write(json.dumps(data))

class RoastEnd(tornado.web.RequestHandler):
    def get(self):
      #print "RoastEnd.get"
      Sensors().endRoasting()
      #self.write(json.dumps(data))

class RoastTempMax(tornado.web.RequestHandler):
    def get(self):
        data = Sensors().getRoastTempMax()
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
