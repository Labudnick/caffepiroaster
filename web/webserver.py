import os,sys,inspect
import tornado.ioloop
import tornado.web
import json

# import from parent directory
root = os.path.dirname(__file__)
os.chdir(root)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from models import Sensors
from roasting import Roaster

port = 8888
class TempLast(tornado.web.RequestHandler):
    def get(self):
        data = Sensors().getLast();
#        self.write(str(data[0]), str(data[1]), str(data[2]) )
        self.write(json.dumps(data))

class TempAll(tornado.web.RequestHandler):
    def get(self):
      data = Sensors().getAll()
      self.write(json.dumps(data))

class RoastStart(tornado.web.RequestHandler):
    def get(self):
      data = Roaster().start()
      self.write(json.dumps(data))

class RoastEnd(tornado.web.RequestHandler):
    def get(self):
      data = Roaster().end()
      self.write(json.dumps(data))

application = tornado.web.Application([
    (r"/last/", TempLast),
    (r"/all/", TempAll),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "index.html"}),
    (r"/start/", RoastStart),
    (r"/end/", RoastEnd)
])


if __name__ == '__main__':
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
