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
        data = DataAccess().get_current_state()
        self.write(json.dumps(data))


class TempAll(tornado.web.RequestHandler):
    def get(self):
        roast_log_id = self.get_argument("roastLogId", None, True)
        data = DataAccess().get_roast_data_by_id(roast_log_id)
        self.write(json.dumps(data))


class RoastStart(tornado.web.RequestHandler):
    def get(self):
        description = self.get_argument("description", None, True)
        tempset = self.get_argument("tempset", None, True)
        coffee_name = self.get_argument("coffeeName", None, True)
        roast_size = self.get_argument("roastSize", None, True)
        beans_size = self.get_argument("beansSize", None, True)
        after_1st_crack_time = self.get_argument("after1stCrackTime", None, True)
        data = DataAccess().start_roasting(float(tempset), description, coffee_name, roast_size, beans_size, after_1st_crack_time)
        self.write(json.dumps(data))

class RoastEnd(tornado.web.RequestHandler):
    def get(self):
        roast_log_id = self.get_argument("roast_log_id", None, True)
        DataAccess().end_roasting(roast_log_id)


class FirstCrack(tornado.web.RequestHandler):
    def get(self):
        DataAccess().set_first_crack()


class GetParamByName(tornado.web.RequestHandler):
    def get(self):
        param_name = self.get_argument("paramName", None, True)
        data = DataAccess().get_param_by_name(param_name)
        self.write(json.dumps(data))


class SetRoastTempMax(tornado.web.RequestHandler):
    def get(self):
        tempset = self.get_argument("tempset", None, True)
        DataAccess().set_roast_temp_max(tempset)


class GetRoastsList(tornado.web.RequestHandler):
    def post(self):
        jt_name_filter = self.get_argument("jtNameFilter", None, True)
        jt_sorting = self.get_argument("jtSorting", None, True)
        jt_start_index = self.get_argument("jtStartIndex", None, True)
        jt_page_size = self.get_argument("jtPageSize", None, True)
        roasts_list = DataAccess().get_roasts_list(jt_name_filter, jt_sorting, jt_start_index, jt_page_size)
        self.write(roasts_list)


class DeletePastRoast(tornado.web.RequestHandler):
    def post(self):
        roastLogId = self.get_argument("id", None, True)
        result = DataAccess().delete_past_roast(roastLogId)
        self.write(result)

class UpdatePastRoast(tornado.web.RequestHandler):
    def post(self):
        row_id = self.get_argument("id", None, True)
        coffee_name = self.get_argument("coffee_name", None, True)
        roast_size = self.get_argument("roast_size", None, True)
        beans_size = self.get_argument("beans_size", None, True)
        description = self.get_argument("description", None, True)
        DataAccess().update_past_roast(row_id, coffee_name, roast_size, beans_size, description)
        self.write(json.dumps({"Result":"OK"}))

class GetInitialData(tornado.web.RequestHandler):
    def get(self):
        data = DataAccess().get_initial_data();
        self.write(json.dumps(data))

class PowerOff(tornado.web.RequestHandler):
    def get(self):
        os.system("sudo poweroff &")

application = tornado.web.Application([
    (r"/last/", TempLast),
    (r"/all/", TempAll),
    (r"/start/", RoastStart),
    (r"/end/", RoastEnd),
    (r"/firstcrack/", FirstCrack),
    (r"/getparambyname/", GetParamByName),
    (r"/setroasttempmax/", SetRoastTempMax),
    (r"/roastslist/", GetRoastsList),
    (r"/updatepastroast/", UpdatePastRoast),
    (r"/deleteroast/", DeletePastRoast),
    (r"/poweroff/", PowerOff),
    (r"/init/", GetInitialData),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "index.html"})
])

if __name__ == '__main__':
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
