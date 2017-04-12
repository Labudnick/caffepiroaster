#import system libraries
import os
#import os import exists
import time
import random
from time import strftime
from models import Sensors

#Load GPIO board module
try:
#    import RPi.GPIO as GPIO
    import time
except RunTimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

#import Adafruit_GPIO.SPI as SPI
#import Adafruit_MAX31855.MAX31855 as MAX31855


#Variables
roasting_temp = 205.00
roasting_delta = 1.50
heat = 0
cooldown_temp = 30

#NaN tester
def isNaN(num):
    return num != num

#Relay channels setup - BCM pin numbering 
relay_fan    = 17 #Fan power supply (BOARD #11)
relay_heater = 4  #Heater power supply (BOARD# 7)

#Relay is off with HIGH state
relay_off = 1 #GPIO.HIGH
relay_on  = 0 #GPIO.LOW

#Define PIN numbering method
#GPIO.setmode(GPIO.BCM)

#Initialize relay channels
#GPIO.setup(relay_fan, GPIO.OUT, initial=relay_off)
#GPIO.setup(relay_heater, GPIO.OUT, initial=relay_off)


# Raspberry Pi software SPI configuration.
CLK = 25
CS  = 24
DO  = 18
#sensor = MAX31855.MAX31855(CLK, CS, DO)


#Roasting stop flag file definition
roast_stop_flag_fname = '.roast_stop_flag'
roast_stop_flag = os.path.dirname(__file__) + '/' + roast_stop_flag_fname
#print roast_stop_flag

class sensor():
    def readTempC(self):
	return round(random.uniform(20, 210), 2)

class Roaster():
    def innitiate(self):
        print "--->Roasting process started on python side"
        
        # Create a flag that prevents roasting from starting
        if not os.path.isfile(roast_stop_flag):
            file=open(roast_stop_flag, 'w')
            file.close()

        # Main loop
        while True:
            if not os.path.isfile(roast_stop_flag): 
                # Roast start process flag appeared
                
                print "--->Innitiate fan"
                #GPIO.output(relay_fan, relay_on)
                licznik = 0
                while not os.path.isfile(roast_stop_flag) and licznik <=5:
                    licznik += 1
                    time.sleep(1)

                print "--->Heating starts"
                # Roasting with target temperature.
                while not os.path.isfile(roast_stop_flag):
                    sens_temp = sensor().readTempC()
                    # Fix temperature reading issues
                    if (( sens_temp == 0) or (isNaN(sens_temp))):
                        time.sleep(1)
                        sens_temp = sensor().readTempC()
                    if sens_temp > roasting_temp + roasting_delta:
                        heat = 1;
                        #GPIO.output(relay_heater, relay_off)
                    elif sens_temp < roasting_temp - roasting_delta:
                        heat = 0
                        #GPIO.output(relay_heater, relay_on)

                    # Send reads to the database
                    datetime=strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    Sensors().InsertData(sens_temp, datetime, heat)
                    #print sens_temp, datetime, heat
                    time.sleep(1)

                print '--->Cooling down started'
                # Cooling down the roaster to set temperature
                heat = 0
                #GPIO.output(relay_heater, relay_off)
                sens_temp = sensor().readTempC()
                while sens_temp > cooldown_temp:
                    time.sleep(1)
                    sens_temp = sensor().readTempC()
                    datetime  = strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    Sensors().InsertData(sens_temp, datetime, heat)
                    print sens_temp, datetime, heat

                #GPIO.output(relay_fan, relay_off)
                #GPIO.cleanup()
                print "--->Cooling down finished"
            
            time.sleep(1)
        
    def end(self):
        print '------>Stop roasting event'
        file=open(roast_stop_flag, 'w')
        file.close()
    def start(self):
        print "------>Start roasting event"
        os.remove(roast_stop_flag)
