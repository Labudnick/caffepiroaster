#import system libraries
import os

#Roasting stop flag file definition
roast_stop_flag_fname = '.roast_stop_flag'
roast_stop_flag = os.path.dirname(__file__) + '/' + roast_stop_flag_fname
#print roast_stop_flag

        
class Roaster():
    def end(self):
        print '------>Stop roasting event'
        if not os.path.isfile(roast_stop_flag):
            file=open(roast_stop_flag, 'w')
            file.close()
    def start(self):
        print "------>Start roasting event"
        if os.path.isfile(roast_stop_flag):
            os.remove(roast_stop_flag)
