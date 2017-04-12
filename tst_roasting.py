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
roast = 0
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
roast_stop_flag = '.roast_stop_flag'
#roast_stop_flag = os.path.dirname(__file__) + '/' + roast_stop_flag_name
print roast_stop_flag


class sensor():
    def readTempC(self):
	return round(random.uniform(20, 210), 2)


class Roaster():
    def start(self):
	print "roasting.Roaster().start"
	# Removing a flag that stops roasting
	if os.path.isfile(roast_stop_flag):
	    os.remove(roast_stop_flag)

	# Innitiate fan
#	GPIO.output(relay_fan, relay_on)
	print "GPIO.output(relay_fan, relay_on)"
	licznik = 0
	while not os.path.isfile(roast_stop_flag) and licznik <=5:
	    licznik += 1
	    time.sleep(1)

	print "Heating starts"
	# Roasting with target temperature - currently fixed 205 Celsius deg.
	while not os.path.isfile(roast_stop_flag):
	    sens_temp = sensor().readTempC()
	    # Fix temperature reading issues
	    if (( sens_temp == 0) or (isNaN(sens_temp))):
		time.sleep(1)
		sens_temp = sensor().readTempC()
	    if sens_temp > roasting_temp + roasting_delta:
		roast = 1;
		print "GPIO.output(relay_heater, relay_off)"
	    elif sens_temp < roasting_temp - roasting_delta:
		roast = 0
		print "GPIO.output(relay_heater, relay_on)"

	    # Send reads to the database
	    datetime=strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	    Sensors().InsertData(sens_temp, datetime, roast)
	    print sens_temp, datetime, roast
	    time.sleep(1)

	# Cooling down the roaster to set temperature
	roast = 0
	print "GPIO.output(relay_heater, relay_off)"
	print 'Cooling down started'
	while sens_temp > cooldown_temp:
	    time.sleep(1)
	    sens_temp = sensor().readTempC()
	    datetime  = strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	    Sensors().InsertData(sens_temp, datetime, roast)
	    print sens_temp, datetime, roast

	print "GPIO.output(relay_fan, relay_off)"
	print "GPIO.cleanup()"
	print 'Cooling down finished'

    def end(self):
	print 'roasting.end().start'
	file.open(roast_stop_flag, 'W')
	file.close()

print sensor().readTempC()
